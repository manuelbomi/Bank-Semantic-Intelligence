"""Load portable files or a real Delta table for text feedback."""
import csv
import json
from pathlib import Path


def rows(folder, table):
    """Read synthetic CSV tables; downstream components cast typed fields."""
    with (Path(folder) / f"{table}.csv").open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def reviews(folder, delta_path=None):
    """Delta table is optional; JSONL gives a zero-dependency path."""
    if delta_path:
        try:
            from deltalake import DeltaTable
        except ImportError as exc:
            raise RuntimeError("Install optional deltalake and pyarrow packages") from exc
        return DeltaTable(str(delta_path)).to_pyarrow_table().to_pylist()
    with (Path(folder) / "reviews.jsonl").open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def to_delta(folder, path):
    """Create a genuine Delta table from the narrative review fixture."""
    try:
        import pyarrow as pa
        from deltalake import write_deltalake
    except ImportError as exc:
        raise RuntimeError("Install optional deltalake and pyarrow packages") from exc
    write_deltalake(str(path), pa.Table.from_pylist(reviews(folder)), mode="overwrite")
