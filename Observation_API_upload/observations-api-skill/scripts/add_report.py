#!/usr/bin/env python3
"""Append a timestamped report to an existing observation.

Usage:
    python scripts/add_report.py <point_id> "<report text>"

Example:
    python scripts/add_report.py 1 "Fresh 30 cm of snow, trail closed above 3000 m."

The server stamps the current Unix time automatically.
"""
import sys
from _common import api_call, pretty

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: add_report.py <point_id> "<text>"', file=sys.stderr)
        sys.exit(2)

    try:
        point_id = int(sys.argv[1])
    except ValueError:
        print(f"'{sys.argv[1]}' is not a valid integer id.", file=sys.stderr)
        sys.exit(2)

    text = sys.argv[2].strip()
    if not text:
        print("Report text cannot be empty.", file=sys.stderr)
        sys.exit(2)

    body = {"text": text}
    result = api_call("POST", f"/api/points/{point_id}/reports", body)
    pretty(result)
