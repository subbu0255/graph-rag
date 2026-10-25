import argparse
import sys
from src.config import DOCUMENTS_DIR, ARTIFACTS_DIR, GRAPH_PATH
from src.extraction import extract_from_document
from src.graph_store import build_graph, save_graph, load_graph
from src.vector_store import load_documents
from src.qa import compare

def build():
    files = sorted(DOCUMENTS_DIR.glob("*.txt"))
    if not files:
        print(f"No .txt documents found in {DOCUMENTS_DIR}")
        return 1
    print(f"Found {len(files)} documents. Extracting facts with Groq...")
    extractions = []
    for path in files:
        print(f"  Extracting: {path.name}")
        extractions.append(extract_from_document(path))
    graph = build_graph(extractions)
    save_graph(graph, GRAPH_PATH)
    print(f"\nGraph saved to: {GRAPH_PATH}")
    print(f"Nodes: {graph.number_of_nodes()} | Edges: {graph.number_of_edges()}")
    print("\nExtracted edges:")
    for source, target, attrs in graph.edges(data=True):
        print(f"  {source} --{attrs.get('relationship')}--> {target}")
        print(f"    source: {attrs.get('source_document')} | evidence: {attrs.get('evidence')}")
    return 0

def ask(question):
    if not GRAPH_PATH.exists():
        print("Graph not built yet. Run: python run.py build")
        return 1
    graph = load_graph(GRAPH_PATH)
    docs = load_documents(DOCUMENTS_DIR)
    result = compare(question, docs, graph)

    print("\n" + "=" * 72)
    print("QUESTION:", question)
    print("=" * 72)
    print("\n[1] TF-IDF / vector-style retrieval baseline")
    if result["vector"]["retrieved_documents"]:
        for doc in result["vector"]["retrieved_documents"]:
            print(f"\n- {doc['id']} (score={doc['score']:.3f})")
            print(f"  {doc['text']}")
    else:
        print("No documents scored above zero.")
    print("\nInterpretation:", result["vector"]["note"])

    print("\n[2] Graph retrieval")
    print("Entities detected in question:", result["graph"]["entities_found"])
    print("Path:", " -> ".join(result["graph"]["path"]) if result["graph"]["path"] else "(none)")
    print("Graph result:", result["graph"]["answer"])
    if result["graph"]["evidence"]:
        print("\nEvidence:")
        for edge in result["graph"]["evidence"]:
            print(
                f"- {edge['source']} --{edge['relationship']}--> {edge['target']}"
                f" | document={edge['source_document']}"
            )
            if edge["evidence"]:
                print(f"  supporting text: {edge['evidence']}")
    print("\nNote: the graph path is evidence, not a guarantee of truth. Check source text.")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Free GraphRAG teaching lab")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="Extract facts from documents and build the graph")
    ask_parser = sub.add_parser("ask", help="Compare TF-IDF retrieval with graph retrieval")
    ask_parser.add_argument("question", nargs="+", help="Question to ask")
    args = parser.parse_args()

    if args.command == "build":
        try:
            return build()
        except Exception as exc:
            print(f"\nBuild failed: {exc}", file=sys.stderr)
            print("Check .env, your Groq API key, model availability, and network connection.")
            return 1
    if args.command == "ask":
        return ask(" ".join(args.question))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
