"""Governed metric definitions: single source of meaning across interfaces."""
from .ingest import rows

METRICS = {
    "active_customers": {"definition": "Distinct customers with at least one account in demo snapshot",
                         "unit": "customers", "owner": "Data Governance"},
    "alert_rate": {"definition": "Alerted transactions / all transactions in snapshot",
                   "unit": "ratio", "owner": "Risk Analytics"},
    "total_transaction_volume_cents": {
        "definition": "Sum of absolute transaction amounts in integer USD cents",
        "unit": "USD cents", "owner": "Finance"},
    "training_completion_rate": {
        "definition": "Completed training seats / total HR headcount",
        "unit": "ratio", "owner": "HR"},
}


def compute(folder):
    """Calculate governed metrics from shared definitions, not ad hoc prompts."""
    customers = rows(folder, "customers")
    accounts = rows(folder, "accounts")
    tx = rows(folder, "transactions")
    alerts = rows(folder, "alerts")
    hr = rows(folder, "hr_metrics")
    return {
        "active_customers": len({a["customer_id"] for a in accounts}),
        "alert_rate": len({a["transaction_id"] for a in alerts}) / len(tx) if tx else 0,
        "total_transaction_volume_cents": sum(abs(int(t["amount_cents"])) for t in tx),
        "training_completion_rate": (
            sum(int(h["training_completed"]) for h in hr) /
            sum(int(h["headcount"]) for h in hr) if hr else 0),
    }
