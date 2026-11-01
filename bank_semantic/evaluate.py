"""Small evaluation harness: retrieval relevance and governance assertions."""
from .vector import search, load_documents
from .config import ROOT


def retrieval_eval():
    """Calculate recall@3 on an explicit synthetic FAQ gold set."""
    docs = load_documents(ROOT / "data" / "policies.json")
    gold = [
        ("How do I reset my mobile password?", "faq-password"),
        ("What is the mortgage partner data policy?", "policy-partner"),
        ("How do employees request leave?", "hr-leave"),
    ]
    found = sum(expected in [r["doc_id"] for r in search(q, docs, 3)]
                for q, expected in gold)
    return {"recall_at_3": found / len(gold), "gold_queries": len(gold)}
