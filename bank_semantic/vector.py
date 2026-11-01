"""Small transparent lexical retriever; optional embedding extension documented.

This is a zero-dependency search baseline, NOT an actual vector database.
"""
import math
import re
from collections import Counter
from pathlib import Path
import json


def tokenize(text):
    """Tokenize words for reproducible local document retrieval."""
    return re.findall(r"[a-z0-9]+", text.lower())


def search(query, documents, k=3):
    """Rank documents by normalized lexical overlap with a query."""
    q = Counter(tokenize(query))
    results = []
    for doc in documents:
        d = Counter(tokenize(doc["text"]))
        dot = sum(q[word] * d[word] for word in q)
        norm = math.sqrt(sum(x*x for x in q.values()) * sum(x*x for x in d.values()))
        score = dot / norm if norm else 0
        if score > 0:
            results.append({"doc_id": doc["doc_id"], "score": round(score, 5),
                            "text": doc["text"], "classification": doc["classification"]})
    return sorted(results, key=lambda row: row["score"], reverse=True)[:k]


def load_documents(path):
    """Read synthetic FAQ and policies with classification metadata."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
