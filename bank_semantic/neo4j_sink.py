"""Optional Neo4j property-graph loader; only controlled labels/types allowed."""
import os
import re


def safe(value):
    """Labels and relationship types cannot be Cypher parameters: validate."""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", value):
        raise ValueError("Invalid graph identifier")
    return value


def load(graph):
    """Idempotent upserts with a global GraphNode ID uniqueness constraint."""
    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise RuntimeError("Install neo4j extra") from exc
    password = os.getenv("BANK_NEO4J_PASSWORD")
    if not password:
        raise RuntimeError("BANK_NEO4J_PASSWORD must be set")
    with GraphDatabase.driver(os.getenv("BANK_NEO4J_URI", "bolt://localhost:7687"),
                              auth=(os.getenv("BANK_NEO4J_USER", "neo4j"), password)) as driver:
        driver.verify_connectivity()
        with driver.session() as session:
            session.run("CREATE CONSTRAINT bank_node_id IF NOT EXISTS "
                        "FOR (n:GraphNode) REQUIRE n.id IS UNIQUE").consume()
            for n in graph["nodes"]:
                label = safe(n["label"])
                session.run(f"MERGE (n:GraphNode {{id:$id}}) SET n:`{label}` "
                            "SET n += $properties", id=n["id"],
                            properties=n["properties"]).consume()
            for e in graph["edges"]:
                rel = safe(e["type"])
                session.run("MATCH (a:GraphNode {id:$source}) "
                            "MATCH (b:GraphNode {id:$target}) "
                            f"MERGE (a)-[r:`{rel}` {{id:$id}}]->(b) "
                            "SET r.status=$status, r.evidence=$evidence", **e).consume()
