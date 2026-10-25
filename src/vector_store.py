from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_documents(directory: Path) -> list[dict]:
    docs = []
    for path in sorted(directory.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if text:
            docs.append({"id": path.name, "text": text})
    return docs

class TfidfRetriever:
    """Free local lexical retrieval baseline; not a neural embedding model."""
    def __init__(self, documents: list[dict]):
        self.documents = documents
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform([d["text"] for d in documents]) if documents else None

    def retrieve(self, question: str, top_k: int = 3) -> list[dict]:
        if not self.documents or self.matrix is None:
            return []
        query_vector = self.vectorizer.transform([question])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        ranked = scores.argsort()[::-1][:top_k]
        return [
            {
                **self.documents[i],
                "score": float(scores[i]),
            }
            for i in ranked
            if scores[i] > 0
        ]
