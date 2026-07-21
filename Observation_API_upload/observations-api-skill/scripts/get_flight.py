#!/usr/bin/env python3
"""Fetch every observation recorded on a given flight number.

Usage:
    python scripts/get_flight.py <flight_number>

Example:
    python scripts/get_flight.py 101
"""
import sys
from _common import api_call, pretty

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: get_flight.py <flight_number>", file=sys.stderr)
        sys.exit(2)
    try:
        flight_number = int(sys.argv[1])
    except ValueError:
        print(f"'{sys.argv[1]}' is not a valid integer flight number.", file=sys.stderr)
        sys.exit(2)

    result = api_call("GET", f"/api/points/flight/{flight_number}")
    pretty(result)
