#!/usr/bin/env python3
"""Fetch every observation from the Observations API and print as JSON.

Usage:
    python scripts/get_points.py

Requires:
    OBSERVATIONS_API_URL  environment variable pointing at the deployed API
                          root (legacy POINTS_API_URL also accepted).
                          Defaults to http://127.0.0.1:5000 if unset.
"""
from _common import api_call, pretty

if __name__ == "__main__":
    result = api_call("GET", "/api/points")
    pretty(result)
