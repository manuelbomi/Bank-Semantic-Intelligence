"""Create canonical banking graph with evidence-bearing, typed relationships."""
import json
from pathlib import Path
from .ingest import rows


def build(folder, candidates):
    """Construct graph from authoritative FK facts and separate review claims."""
    nodes, edges = {}, {}

    def node(identifier, label, **properties):
        """Stable IDs prevent accidental duplicate nodes on re-runs."""
        nodes[identifier] = {"id": identifier, "label": label, "properties": properties}

    def edge(source, relation, target, evidence, status="verified_source"):
        """Record provenance and confidence category on every relationship."""
        if source not in nodes or target not in nodes:
            raise ValueError("Dangling relationship endpoint")
        identifier = f"{source}|{relation}|{target}|{evidence}"
        edges[identifier] = {"id": identifier, "source": source, "target": target,
                             "type": relation, "status": status, "evidence": evidence}

    customers = rows(folder, "customers")
    accounts = rows(folder, "accounts")
    transactions = rows(folder, "transactions")
    alerts = rows(folder, "alerts")
    signals = rows(folder, "mortgage_signals")
    for c in customers:
        # No email or DOB in the graph export: minimize sensitive attributes.
        node("C" + c["customer_id"], "Customer", region=c["region"],
             marketing_consent=c["marketing_consent"])
    for a in accounts:
        aid = "A" + a["account_id"]
        node(aid, "Account", account_type=a["account_type"])
        edge("C" + a["customer_id"], "OWNS", aid, "accounts.customer_id")
    for t in transactions:
        tid = "T" + t["transaction_id"]
        node(tid, "Transaction", amount_cents=int(t["amount_cents"]),
             tx_type=t["tx_type"], country=t["country"])
        edge("A" + t["account_id"], "HAS_TRANSACTION", tid, "transactions.account_id")
    for a in alerts:
        alert_id = "F" + a["alert_id"]
        node(alert_id, "FraudAlert", rule=a["rule_name"], disposition=a["disposition"])
        edge("T" + a["transaction_id"], "TRIGGERED_ALERT", alert_id,
             "alerts.transaction_id")
    for s in signals:
        if s["mortgage_interest"] == "1":
            # These signals are synthetic, not creditworthiness or eligibility decisions.
            target = "C" + s["customer_id"]
            node("P:mortgage", "Product", name="mortgage")
            edge(target, "INTEREST_SIGNAL", "P:mortgage", "mortgage_signals.csv",
                 "synthetic_signal")
    for fact in candidates:
        review_id = "R" + fact["review_id"]
        node(review_id, "Review", theme=fact["relation"])
        # A review is not linked to a person unless the source supplies a stable ref.
        if fact["customer_ref"] is not None:
            cid = "C" + str(fact["customer_ref"])
            if cid in nodes:
                edge(cid, "AUTHORED_REVIEW_CANDIDATE", review_id,
                     fact["review_id"], "unverified")
        topic_id = "TOPIC:" + fact["relation"]
        node(topic_id, "Topic", name=fact["relation"])
        edge(review_id, "MENTIONS_CANDIDATE", topic_id,
             fact["review_id"] + ":" + fact["evidence"], "unverified")
    return {"nodes": list(nodes.values()), "edges": list(edges.values())}


def save(graph, path):
    """Write an inspectable graph snapshot for Neo4j and local analytics."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return {"nodes": len(graph["nodes"]), "edges": len(graph["edges"])}
