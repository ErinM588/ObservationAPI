#!/usr/bin/env python3
"""Fetch one observation by its integer id.

Usage:
    python scripts/get_point.py <id>

Example:
    python scripts/get_point.py 3
"""
import sys
from _common import api_call, pretty

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: get_point.py <id>", file=sys.stderr)
        sys.exit(2)
    try:
        point_id = int(sys.argv[1])
    except ValueError:
        print(f"'{sys.argv[1]}' is not a valid integer id.", file=sys.stderr)
        sys.exit(2)

    result = api_call("GET", f"/api/points/{point_id}")
    pretty(result)
