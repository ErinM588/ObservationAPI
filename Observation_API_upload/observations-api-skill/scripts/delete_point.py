#!/usr/bin/env python3
"""Delete an observation by id.

Usage:
    python scripts/delete_point.py <id>
"""
import sys
from _common import api_call, pretty

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: delete_point.py <id>", file=sys.stderr)
        sys.exit(2)
    try:
        point_id = int(sys.argv[1])
    except ValueError:
        print(f"'{sys.argv[1]}' is not a valid integer id.", file=sys.stderr)
        sys.exit(2)

    result = api_call("DELETE", f"/api/points/{point_id}")
    pretty(result)
