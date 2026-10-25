from src.vector_store import TfidfRetriever
from src.graph_store import retrieve_graph_evidence

def compare(question: str, documents: list[dict], graph):
    retriever = TfidfRetriever(documents)
    vector_results = retriever.retrieve(question, top_k=3)
    graph_result = retrieve_graph_evidence(question, graph)

    return {
        "question": question,
        "vector": {
            "retrieved_documents": vector_results,
            "note": (
                "This is a TF-IDF retrieval baseline. It shows which chunks a conventional "
                "retrieval stage might pass to an answer-generation LLM; it does not prove "
                "that vector RAG would answer incorrectly."
            ),
        },
        "graph": graph_result,
    }
