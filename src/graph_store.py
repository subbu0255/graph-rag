import json
from pathlib import Path
import networkx as nx

def build_graph(extractions: list[dict]) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    for extraction in extractions:
        for entity in extraction["entities"]:
            name = entity["name"].strip()
            if name:
                graph.add_node(name, entity_type=entity.get("type", "Other"))
        for rel in extraction["relationships"]:
            source, target = rel["source"].strip(), rel["target"].strip()
            if not source or not target:
                continue
            graph.add_node(source, entity_type="Other")
            graph.add_node(target, entity_type="Other")
            graph.add_edge(
                source,
                target,
                relationship=rel["type"].upper(),
                evidence=rel.get("evidence", ""),
                source_document=rel.get("source_document", ""),
            )
    return graph

def save_graph(graph: nx.MultiDiGraph, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "nodes": [
            {"name": node, **attrs}
            for node, attrs in graph.nodes(data=True)
        ],
        "edges": [
            {"source": source, "target": target, **attrs}
            for source, target, attrs in graph.edges(data=True)
        ],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

def load_graph(path: Path) -> nx.MultiDiGraph:
    payload = json.loads(path.read_text(encoding="utf-8"))
    graph = nx.MultiDiGraph()
    for node in payload["nodes"]:
        attrs = dict(node)
        name = attrs.pop("name")
        graph.add_node(name, **attrs)
    for edge in payload["edges"]:
        attrs = dict(edge)
        source, target = attrs.pop("source"), attrs.pop("target")
        graph.add_edge(source, target, **attrs)
    return graph

def find_entity_mentions(question: str, graph: nx.MultiDiGraph) -> list[str]:
    q = question.casefold()
    matches = [node for node in graph.nodes if node.casefold() in q]
    # Prefer longer names first to avoid matching a short name inside a longer one.
    return sorted(matches, key=len, reverse=True)

def retrieve_graph_evidence(question: str, graph: nx.MultiDiGraph, max_hops: int = 4) -> dict:
    starts = find_entity_mentions(question, graph)
    if not starts:
        return {
            "answer": "I couldn't identify a known entity in the question.",
            "path": [],
            "evidence": [],
            "entities_found": [],
        }

    q = question.casefold()
    # Search simple directed paths from mentioned entities. Keep paths short and relevant.
    candidate_paths = []
    for start in starts:
        for target in graph.nodes:
            if target == start:
                continue
            try:
                paths = nx.all_simple_paths(graph, start, target, cutoff=max_hops)
                for path in paths:
                    if len(path) < 3:  # need at least two edges for this lab
                        continue
                    edge_details = []
                    for u, v in zip(path, path[1:]):
                        attrs = list(graph.get_edge_data(u, v).values())[0]
                        edge_details.append({
                            "source": u,
                            "relationship": attrs.get("relationship", "RELATED_TO"),
                            "target": v,
                            "evidence": attrs.get("evidence", ""),
                            "source_document": attrs.get("source_document", ""),
                        })
                    path_text = " ".join(path + [e["relationship"] for e in edge_details]).casefold()
                    # Prefer paths whose destination or relation terms match the question.
                    score = sum(1 for word in target.casefold().split() if word in q)
                    score += sum(1 for edge in edge_details if edge["relationship"].replace("_", " ").casefold() in q)
                    # Common question intent boosts appropriate relationship paths.
                    if any(term in q for term in ("which team", "what team", "maintain")):
                        score += sum(2 for e in edge_details if "MAINTAIN" in e["relationship"])
                    if "who leads" in q or "who lead" in q:
                        score += sum(2 for e in edge_details if "LED_BY" in e["relationship"])
                    candidate_paths.append((score, len(path), path, edge_details))
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

    if not candidate_paths:
        return {
            "answer": "No connected path of at least two edges was found. The graph may be incomplete.",
            "path": [],
            "evidence": [],
            "entities_found": starts,
        }

    # Prefer relevant paths, then shorter paths.
    candidate_paths.sort(key=lambda item: (-item[0], item[1]))
    _, _, path, evidence = candidate_paths[0]
    answer = " -> ".join(path)
    return {
        "answer": answer,
        "path": path,
        "evidence": evidence,
        "entities_found": starts,
    }
