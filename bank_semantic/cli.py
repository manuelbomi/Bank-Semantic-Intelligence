"""CLI orchestration for the bank semantic knowledge system."""
import argparse
import json
from .config import DATA, ARTIFACTS, ROOT
from .synthetic import generate
from .ingest import reviews, to_delta
from .extract import extract_all
from .graph import build, save
from .assistant import answer
from .evaluate import retrieval_eval


def main():
    """Run offline first; opt in to infrastructure-dependent features."""
    parser = argparse.ArgumentParser(description="Bank semantic intelligence lab")
    parser.add_argument("command", choices=["generate", "demo", "ask", "evaluate",
                                            "delta-write", "splink", "neo4j-load"])
    parser.add_argument("--role", default="analyst")
    parser.add_argument("--question", default="How many active customers and what is transaction volume?")
    parser.add_argument("--customer-id", type=int)
    parser.add_argument("--mode", choices=["offline", "llm"], default="offline")
    parser.add_argument("--delta-path")
    args = parser.parse_args()
    if args.command == "generate":
        print(json.dumps(generate(), indent=2))
        return
    if not (DATA / "customers.csv").exists():
        generate()
    if args.command == "delta-write":
        to_delta(DATA, ROOT / "data" / "delta" / "reviews")
        print("Delta table written")
        return
    if args.command == "splink":
        from .identity import splink_candidates
        pairs = splink_candidates(DATA)
        ARTIFACTS.mkdir(exist_ok=True)
        (ARTIFACTS / "splink_candidates.json").write_text(json.dumps(pairs, indent=2, default=str))
        print(f"Candidate pairs: {len(pairs)} (not verified identity links)")
        return
    if args.command == "ask":
        print(json.dumps(answer(args.question, args.role, DATA, args.customer_id), indent=2))
        return
    if args.command == "evaluate":
        print(json.dumps(retrieval_eval(), indent=2))
        return
    candidates = extract_all(reviews(DATA, args.delta_path), args.mode)
    graph = build(DATA, candidates)
    stats = save(graph, ARTIFACTS / "graph.json")
    if args.command == "neo4j-load":
        from .neo4j_sink import load
        load(graph)
        print("Graph loaded into Neo4j")
    print(json.dumps({**stats, "extracted_candidates": len(candidates)}, indent=2))

if __name__ == "__main__":
    main()
