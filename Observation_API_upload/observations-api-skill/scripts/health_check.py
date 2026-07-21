#!/usr/bin/env python3
"""Check whether the Observations API is working (true/false recall).

Usage:
    python scripts/health_check.py

Prints the health JSON ({"ok": true, ...}) and exits 0 if ok is true,
non-zero otherwise.
"""
import sys
from _common import api_call, pretty

if __name__ == "__main__":
    result = api_call("GET", "/api/health")
    pretty(result)
    sys.exit(0 if result.get("ok") is True else 1)
