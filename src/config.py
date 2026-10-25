from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DOCUMENTS_DIR = ROOT / "data" / "documents"
ARTIFACTS_DIR = ROOT / "artifacts"
GRAPH_PATH = ARTIFACTS_DIR / "knowledge_graph.json"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
