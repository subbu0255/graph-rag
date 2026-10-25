import json
from pathlib import Path
from groq import Groq
from src.config import GROQ_API_KEY, GROQ_MODEL

SYSTEM_PROMPT = """You extract factual knowledge from documents.
Return a JSON object with this exact top-level shape:
{
  "entities": [{"name": "canonical entity name", "type": "Person|Company|Team|System|Other"}],
  "relationships": [
    {"source": "entity name", "type": "UPPER_SNAKE_CASE_RELATIONSHIP",
     "target": "entity name", "evidence": "short exact or faithful supporting sentence"}
  ]
}
Rules:
- Extract only explicit facts supported by the supplied text.
- Do not infer relationships that are not stated.
- Use the same entity name consistently within this response.
- Relationship direction must preserve the meaning of the sentence.
- Include the source sentence in evidence.
- Return valid JSON only. Do not use markdown fences.
"""

def extract_from_document(path: Path) -> dict:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    content = path.read_text(encoding="utf-8").strip()
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Source file: {path.name}\n\nDocument:\n{content}"}
        ],
    )
    raw = response.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Groq returned invalid JSON for {path.name}: {raw}") from exc

    if not isinstance(data.get("entities"), list) or not isinstance(data.get("relationships"), list):
        raise ValueError(f"Unexpected extraction schema from {path.name}: {data}")

    entity_names = {
        str(item.get("name", "")).strip()
        for item in data["entities"]
        if isinstance(item, dict) and str(item.get("name", "")).strip()
    }
    clean_relationships = []
    for rel in data["relationships"]:
        if not isinstance(rel, dict):
            continue
        source = str(rel.get("source", "")).strip()
        relation = str(rel.get("type", "")).strip().upper().replace(" ", "_")
        target = str(rel.get("target", "")).strip()
        evidence = str(rel.get("evidence", "")).strip()
        if not source or not relation or not target:
            continue
        # Include endpoints even if the model omitted them from its entity list.
        entity_names.update([source, target])
        clean_relationships.append({
            "source": source,
            "type": relation,
            "target": target,
            "evidence": evidence,
            "source_document": path.name,
        })

    clean_entities = []
    raw_types = {
        str(item.get("name", "")).strip(): str(item.get("type", "Other")).strip() or "Other"
        for item in data["entities"] if isinstance(item, dict) and str(item.get("name", "")).strip()
    }
    for name in sorted(entity_names):
        clean_entities.append({"name": name, "type": raw_types.get(name, "Other")})

    return {"entities": clean_entities, "relationships": clean_relationships}
