from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Any


@dataclass
class DataFrame:
    rows: list[dict[str, Any]]


def load_csv(path: str) -> DataFrame:
    """Load a CSV file into a simple DataFrame wrapper."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return DataFrame(rows)


def write_csv(df: DataFrame, path: str) -> None:
    """Write a DataFrame to a CSV file."""
    if not df.rows:
        with open(path, "w", newline=""):
            return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=df.rows[0].keys())
        writer.writeheader()
        writer.writerows(df.rows)
