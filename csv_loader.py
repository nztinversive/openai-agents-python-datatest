from __future__ import annotations

import csv
import io  # Added for StringIO
from typing import Any, Dict, List


def load_csv(path: str) -> List[Dict[str, Any]]:
    """Load a CSV file into a list of dictionaries and validate it."""
    with open(path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV is missing headers")
        rows = list(reader)

    if not rows:
        raise ValueError("CSV file is empty")

    expected_fields = set(reader.fieldnames)
    for i, row in enumerate(rows, start=1):
        if set(row.keys()) != expected_fields:
            raise ValueError(f"Row {i} has inconsistent headers")

    return rows


def write_csv(data: List[Dict[str, Any]], path: str) -> None:
    """Write a list of dictionaries to a CSV file."""
    if not data:
        # Create an empty file or a file with headers if preferred
        with open(path, "w", newline="", encoding="utf-8") as f:
            # Optionally write headers even for empty data if that's desired
            # For example, if you had a way to get headers: csv.DictWriter(f, fieldnames=known_headers).writeheader()
            pass
        return

    fieldnames = list(data[0].keys())  # Get fieldnames from the first row
    with open(path, mode="w", newline="", encoding="utf-8") as f:  # Added mode, encoding
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def csv_string_to_dataframe(csv_string: str) -> List[Dict[str, Any]]:
    """Convert a CSV string into a list of dictionaries."""
    # Use io.StringIO to treat the string as a file
    file_like_object = io.StringIO(csv_string)
    reader = csv.DictReader(file_like_object)
    return list(reader)


def dataframe_to_csv_string(data: List[Dict[str, Any]]) -> str:
    """Convert a list of dictionaries into a CSV string."""
    if not data:
        return ""  # Return empty string for empty data

    fieldnames = list(data[0].keys())
    # Use io.StringIO to write to an in-memory text buffer
    string_buffer = io.StringIO()
    writer = csv.DictWriter(string_buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return string_buffer.getvalue()
