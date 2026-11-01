"""Optional real PostgreSQL ingestion adapter for the synthetic fixtures.

Only use a disposable development database; schema and data are synthetic.
The adapter uses psycopg parameters for values and explicit table allowlists.
"""
import os
from .ingest import rows

TABLES = ("customers", "accounts", "transactions", "alerts")


def load_synthetic(folder, dsn=None):
    """Insert fixture rows in FK order into a PostgreSQL dev database."""
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("Install psycopg[binary]") from exc
    dsn = dsn or os.getenv("BANK_POSTGRES_DSN")
    if not dsn:
        raise RuntimeError("BANK_POSTGRES_DSN must be configured")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            for table in TABLES:
                records = rows(folder, table)
                if not records:
                    continue
                columns = list(records[0])
                # Both table and column names are from trusted local contracts.
                names = ", ".join(columns)
                placeholders = ", ".join("%s" for _ in columns)
                query = f"INSERT INTO {table} ({names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                cur.executemany(query, [tuple(row[col] for col in columns) for row in records])
    return {"tables_loaded": list(TABLES)}
