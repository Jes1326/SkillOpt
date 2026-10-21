"""Evaluator for Test Data Generator skill output."""
from __future__ import annotations
import re


def _extract_table_rows(response: str) -> list[list[str]]:
    """Extract data rows from a markdown table (skip header and separator rows)."""
    rows = []
    for line in response.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Skip separator rows like |---|---|
        if re.match(r"^\|[\s\-:|]+\|", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 3:
            rows.append(cells)
    # First row is the header — remove it
    if rows:
        rows = rows[1:]
    return rows


def evaluate(response: str, checks: list[str]) -> dict:
    """Score the LLM response against required checks strictly.

    Checks:
    - has_table: markdown table with >= 4 columns present
    - has_positive: at least 1 row with Type=Positive and Expected=Accepted
    - has_negative: at least 2 rows with Type=Negative and Expected contains error/reject/invalid
    - has_boundary: at least 1 row with Type=Boundary
    - has_null: at least 1 row where Test Data is NULL/empty/blank
    - min_rows: at least 6 data rows total
    """
    rows = _extract_table_rows(response)

    # Determine column indices by scanning header line
    type_col = 2   # default: Test Data | Scenario | Type | Expected Result
    data_col = 0
    expected_col = 3

    # Try to detect actual column positions from header
    for line in response.splitlines():
        line = line.strip()
        if line.startswith("|") and not re.match(r"^\|[\s\-:|]+\|", line):
            headers = [c.strip().lower() for c in line.strip("|").split("|")]
            for i, h in enumerate(headers):
                if "type" in h:
                    type_col = i
                if "expected" in h:
                    expected_col = i
                if "test data" in h or "test value" in h:
                    data_col = i
            break

    def _cell(row, idx):
        return row[idx].lower().strip() if idx < len(row) else ""

    positive_rows = [
        r for r in rows
        if "positive" in _cell(r, type_col)
        and ("accept" in _cell(r, expected_col) or "valid" in _cell(r, expected_col) or "pass" in _cell(r, expected_col))
    ]
    negative_rows = [
        r for r in rows
        if "negative" in _cell(r, type_col)
        and any(w in _cell(r, expected_col) for w in ["error", "invalid", "reject", "fail", "not accept"])
    ]
    boundary_rows = [
        r for r in rows
        if "boundary" in _cell(r, type_col) or "edge" in _cell(r, type_col)
    ]
    null_rows = [
        r for r in rows
        if any(w in _cell(r, data_col) for w in ["null", "empty", "blank", "none", "\"\"", "''"])
        or _cell(r, data_col) == ""
    ]

    results = {
        "has_table": len(rows) > 0,
        "has_positive": len(positive_rows) >= 1,
        "has_negative": len(negative_rows) >= 2,
        "has_boundary": len(boundary_rows) >= 1,
        "has_null": len(null_rows) >= 1,
        "min_rows": len(rows) >= 6,
    }

    # Only score against checks requested for this item
    active_checks = [c for c in checks if c in results]
    passed = sum(1 for c in active_checks if results[c])
    total = len(active_checks) if active_checks else len(checks)
    soft = passed / total if total else 0.0
    hard = int(passed == total)

    return {
        "hard": hard,
        "soft": soft,
        "checks_passed": passed,
        "checks_total": total,
        "check_details": {c: results.get(c, False) for c in checks},
        "row_count": len(rows),
        "positive_count": len(positive_rows),
        "negative_count": len(negative_rows),
        "boundary_count": len(boundary_rows),
        "null_count": len(null_rows),
    }
