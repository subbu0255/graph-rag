# Free GraphRAG Lab (Groq + NetworkX)

A small, beginner-friendly GraphRAG project for VS Code. It compares:
1. **Vector-style retrieval baseline** using free local TF-IDF (scikit-learn).
2. **Graph-based retrieval** using entities and relationships extracted by Groq, stored in NetworkX, and traversed for multi-hop questions.

No paid database or embedding service is required. Groq API usage is subject to your account's limits. NetworkX and TF-IDF run locally.

## What you'll learn

- Extract structured entities and relationships from documents with an LLM.
- Build a knowledge graph automatically (no manually written edges).
- Preserve source-document provenance for extracted relationships.
- Traverse a graph to answer a multi-hop question.
- Compare retrieved evidence from vector-style and graph-based retrieval.

## Project structure

```text
graphrag_free_lab/
├── data/documents/       # Sample source documents
├── src/
│   ├── config.py
│   ├── extraction.py     # Groq-based entity/relationship extraction
│   ├── graph_store.py    # NetworkX graph construction and traversal
│   ├── vector_store.py   # Local TF-IDF retrieval baseline
│   └── qa.py             # Compare retrieval approaches
├── tests/
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```

## 1. Requirements

- Python 3.10 or newer recommended.
- VS Code with the Python extension.
- A Groq API key.
- Internet access during LLM extraction.

If you use an older Python version, create a virtual environment with Python 3.10+ if possible.

## 2. Open the project in VS Code

1. Download and extract `graphrag_free_lab.zip`.
2. In VS Code, choose **File → Open Folder** and select `graphrag_free_lab`.
3. Open the integrated terminal: **Terminal → New Terminal**.

## 3. Create and activate a virtual environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt and run:
```bat
.venv\Scripts\activate.bat
```

## 4. Add your Groq API key

Copy `.env.example` to `.env`, then edit `.env`:

```text
GROQ_API_KEY=put_your_real_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

The model name is configurable. If Groq reports that the model is unavailable for your account, set `GROQ_MODEL` to a currently supported chat model available in your Groq console.

**Never commit `.env` or share your API key.** The included `.gitignore` excludes it.

## 5. Run the project

First build the graph from the sample documents:

```bash
python run.py build
```

This calls Groq to extract entities and relationships, validates the response, and writes the graph to `artifacts/knowledge_graph.json`.

Then ask the sample multi-hop question:

```bash
python run.py ask "Which team maintains the gateway used by Acme Payments?"
```

Try the three-hop question:

```bash
python run.py ask "Who leads the team that maintains the gateway used by Acme Payments?"
```

The output shows:
- TF-IDF baseline: relevant chunks retrieved and the evidence available to a normal RAG pipeline.
- Graph retrieval: the relationship path found and the evidence used to answer.

The graph-based answer uses a simple relationship-path template so the traversal is easy to inspect. This is intentional for teaching: it separates **retrieval correctness** from answer-generation quality.

## 6. Add your own documents

Add `.txt` files under `data/documents/`. Keep each file focused on a few facts and include explicit relationships. Then rebuild:

```bash
python run.py build
python run.py ask "Your question here"
```

Start with simple questions that require at least two connected relationships. The graph can only answer relationships that the extraction stage successfully captures.

## 7. What if Groq extraction fails?

- Check that `.env` exists in the project root and the key is valid.
- Check your internet connection and Groq usage limits.
- Check whether `GROQ_MODEL` is currently supported by your account.
- The model must return JSON. The code asks for JSON mode and also validates the result.
- Fix extraction errors by inspecting the raw documents and model output; do not silently treat a missing relationship as a true fact.

## 8. Important limitations

- This is an educational prototype, not production GraphRAG.
- TF-IDF is a lightweight lexical baseline, not a modern embedding-based vector database.
- Entity matching and traversal are deliberately simple.
- LLM extraction can omit or misstate relationships. Source provenance is retained so you can inspect where each edge came from.
- GraphRAG is not guaranteed to outperform vector RAG on every question. Compare both using the same documents and evaluation questions.

## 9. Suggested classroom exercise

1. Run both commands and inspect the two retrieval results.
2. Add a new document linking another service to a team.
3. Rebuild the graph and ask a question that needs the new relationship.
4. Deliberately remove one source fact and observe how the graph answer changes.
5. Discuss why extraction validation, entity resolution, provenance and graph freshness matter.
