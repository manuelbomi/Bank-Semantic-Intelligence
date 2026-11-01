"""Role-aware, evidence-first prompt workflows with deterministic routing.

This intentionally avoids executing arbitrary model-generated SQL or Cypher.
"""
from .config import SCOPES
from .ingest import rows
from .semantic import compute, METRICS
from .vector import search, load_documents
from .config import ROOT


def answer(question, role, folder, actor_customer_id=None):
    """Authorize a user role, route known intents and cite source records."""
    if role not in SCOPES:
        raise PermissionError("Unknown role")
    q = question.casefold()
    scopes = SCOPES[role]
    if any(word in q for word in ("training", "headcount", "employee")):
        if "hr" not in scopes:
            raise PermissionError("HR data not authorized for this role")
        hr = rows(folder, "hr_metrics")
        metrics = compute(folder)
        return {"answer": f"Training completion rate: {metrics['training_completion_rate']:.1%}.",
                "citations": ["hr_metrics.csv", "semantic:training_completion_rate"],
                "departments": len(hr)}
    if any(word in q for word in ("mortgage partner", "partnership", "mortgage lender")):
        if "partnership" not in scopes:
            raise PermissionError("Partnership analytics not authorized")
        signals = rows(folder, "mortgage_signals")
        # Count consented interest; never expose identifiable customers to partners.
        count = sum(s["mortgage_interest"] == "1" and s["consent_to_contact"] == "1"
                    for s in signals)
        return {"answer": f"{count} synthetic customers show mortgage interest AND contact consent. "
                "This is not a lending eligibility or credit decision.",
                "citations": ["mortgage_signals.csv", "policy:partner-sharing"]}
    if any(word in q for word in ("my account", "my balance", "mobile app")) and role == "customer":
        if actor_customer_id is None:
            raise PermissionError("Authenticated customer ID required")
        accounts = [a for a in rows(folder, "accounts")
                    if a["customer_id"] == str(actor_customer_id)]
        return {"answer": f"You have {len(accounts)} synthetic accounts. "
                "Balances are unavailable in this dataset.",
                "citations": ["accounts.csv"],
                "account_ids": [a["account_id"] for a in accounts]}
    if any(word in q for word in ("alert", "fraud", "international")):
        if "aggregate" not in scopes:
            raise PermissionError("Risk aggregates not authorized")
        metrics = compute(folder)
        return {"answer": f"Rule-alert rate: {metrics['alert_rate']:.2%}; alerts are not confirmed fraud.",
                "citations": ["alerts.csv", "transactions.csv", "semantic:alert_rate"]}
    if any(word in q for word in ("customer", "transaction volume", "kpi")):
        if "aggregate" not in scopes:
            raise PermissionError("Aggregate banking metrics not authorized")
        metrics = compute(folder)
        return {"answer": f"Active customers: {metrics['active_customers']}; "
                f"transaction volume: ${metrics['total_transaction_volume_cents']/100:,.2f}.",
                "citations": ["accounts.csv", "transactions.csv", "semantic:active_customers"]}
    if "policy" not in scopes:
        raise PermissionError("Policy retrieval not authorized")
    docs = load_documents(ROOT / "data" / "policies.json")
    # Role-specific document filtering occurs BEFORE retrieval.
    allowed = [d for d in docs if d["classification"] == "public" or
               (d["classification"] == "internal_hr" and "hr" in scopes) or
               (d["classification"] == "internal" and role != "customer")]
    hits = search(question, allowed)
    return {"answer": hits[0]["text"] if hits else "No grounded answer found.",
            "citations": [h["doc_id"] for h in hits], "retrieval": hits}
