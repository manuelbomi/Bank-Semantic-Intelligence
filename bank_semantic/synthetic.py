"""Deterministic synthetic banking fixtures. No real bank/customer information."""
import csv
import json
import random
from pathlib import Path
from .config import DATA


def csv_write(path, items):
    """Write a table with consistent columns for repeatable examples."""
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(items[0]))
        writer.writeheader()
        writer.writerows(items)


def generate(n=120, seed=42, folder=DATA):
    """Generate customers, accounts, transactions, alerts, CRM and reviews."""
    rng = random.Random(seed)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    customers, accounts, transactions, alerts, crm, signals = [], [], [], [], [], []
    for i in range(1, n + 1):
        name = f"Demo Customer {i:04d}"
        email = f"demo{i:04d}@example.test"
        customers.append({"customer_id": i, "full_name": name,
                          "dob": f"{1970 + i % 35}-06-15", "email": email,
                          "region": ["NC", "NJ", "NY", "VA"][i % 4],
                          "marketing_consent": int(i % 3 == 0)})
        crm.append({"record_id": f"CRM-{i}",
                    "full_name": name if i % 7 else f"D. Customer {i:04d}",
                    "email": email if i % 11 else "", "region": ["NC", "NJ", "NY", "VA"][i % 4]})
        signals.append({"customer_id": i, "mortgage_interest": int(i % 9 == 0),
                        "consent_to_contact": int(i % 6 == 0),
                        "income_band": ["low", "mid", "high"][i % 3]})
        for j in range(2):
            aid = 100000 + i * 10 + j
            accounts.append({"account_id": aid, "customer_id": i,
                             "account_type": "checking" if j == 0 else "savings",
                             "opened_at": "2024-01-01"})
            for k in range(4):
                tid = 1000000 + i * 100 + j * 10 + k
                kind = "international_transfer" if k == 3 and i % 5 == 0 else "card"
                transactions.append({"transaction_id": tid, "account_id": aid,
                                     "amount_cents": rng.randint(1500, 250000),
                                     "currency": "USD", "tx_type": kind,
                                     "country": "SG" if kind == "international_transfer" else "US",
                                     "occurred_at": "2026-02-01T12:00:00Z"})
                if kind == "international_transfer":
                    alerts.append({"alert_id": len(alerts) + 1,
                                   "transaction_id": tid,
                                   "rule_name": "international_review",
                                   "disposition": "open"})
    for name, values in [("customers", customers), ("accounts", accounts),
                         ("transactions", transactions), ("alerts", alerts),
                         ("crm_profiles", crm), ("mortgage_signals", signals)]:
        csv_write(folder / f"{name}.csv", values)
    reviews = [{"review_id": f"REV-{i}", "customer_ref": i if i % 4 == 0 else None,
                "text": ("I am interested in a mortgage and want clear rates."
                         if i % 9 == 0 else "The mobile app transfer screen is confusing."),
                "consent_for_analytics": i % 3 == 0}
               for i in range(1, n + 1)]
    with (folder / "reviews.jsonl").open("w", encoding="utf-8") as stream:
        for row in reviews:
            stream.write(json.dumps(row) + "\n")
    csv_write(folder / "hr_metrics.csv", [
        {"department": dept, "headcount": count, "training_completed": done}
        for dept, count, done in [("Engineering", 24, 20), ("Risk", 16, 15),
                                  ("HR", 8, 8), ("Operations", 30, 27)]])
    return {"customers": len(customers), "accounts": len(accounts),
            "transactions": len(transactions), "alerts": len(alerts),
            "reviews": len(reviews)}
