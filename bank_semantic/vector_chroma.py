"""Optional real vector database adapter using Chroma and local embeddings.

Unlike vector.py's lexical baseline, this stores dense vectors and queries by
semantic similarity. Model weights may be downloaded on first use: review data
policies and use only synthetic or approved data. Not used by the core demo.
"""
from pathlib import Path
from .vector import load_documents
from .config import ROOT


def index_and_query(question, persist_dir=None, top_k=3):
    """Build or reuse a persistent Chroma index of synthetic bank policies."""
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError("Install chromadb and sentence-transformers optional extras") from exc
    directory = str(persist_dir or ROOT / "artifacts" / "chroma")
    # Local CPU embeddings; replace with a reviewed enterprise model as needed.
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    docs = load_documents(ROOT / "data" / "policies.json")
    client = chromadb.PersistentClient(path=directory)
    collection = client.get_or_create_collection(name="bank_synthetic_policies")
    collection.upsert(
        ids=[d["doc_id"] for d in docs],
        documents=[d["text"] for d in docs],
        embeddings=model.encode([d["text"] for d in docs]).tolist(),
        metadatas=[{"classification": d["classification"]} for d in docs],
    )
    # Classification filter is applied *inside* retrieval, not after ranking.
    hits = collection.query(
        query_embeddings=model.encode([question]).tolist(),
        n_results=min(top_k, len(docs)),
        where={"classification": "public"},
    )
    return [{"doc_id": doc_id, "text": text, "distance": distance}
            for doc_id, text, distance in zip(hits["ids"][0],
                                              hits["documents"][0],
                                              hits["distances"][0])]
