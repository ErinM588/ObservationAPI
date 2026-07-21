#!/usr/bin/env python3
"""Search the Observations database by any combination of fields.

Usage:
    python scripts/search_points.py <key=value> [<key=value> ...]

Supported keys:
    name=<substring>          case-insensitive name match
    id=<int>                  exact id match
    flight_number=<int>       exact flight number match
    lat=<f>  lon=<f>  alt=<f> exact coordinate match
    lat_min / lat_max         latitude range (observation point)
    lon_min / lon_max         longitude range (observation point)
    alt_min / alt_max         altitude range
    observed_from / observed_to
                              observation date range; Unix timestamp or
                              ISO date (e.g. 2026-07-19)
    fp_lat_min / fp_lat_max / fp_lon_min / fp_lon_max
                              footprint search box — returns observations
                              whose footprint overlaps the box (all four
                              must be supplied together)
    report_text=<substring>   substring within any report

Examples:
    python scripts/search_points.py name=mount alt_min=3000
    python scripts/search_points.py observed_from=2026-07-01 observed_to=2026-07-31
    python scripts/search_points.py fp_lat_min=33 fp_lat_max=35 fp_lon_min=74 fp_lon_max=76
"""
import sys
from _common import api_call, qs, pretty

ALLOWED = {
    "name", "id", "flight_number",
    "lat", "lon", "alt",
    "lat_min", "lat_max",
    "lon_min", "lon_max",
    "alt_min", "alt_max",
    "observed_from", "observed_to",
    "fp_lat_min", "fp_lat_max",
    "fp_lon_min", "fp_lon_max",
    "report_text",
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: search_points.py key=value [key=value ...]", file=sys.stderr)
        print("Supported keys: " + ", ".join(sorted(ALLOWED)), file=sys.stderr)
        sys.exit(2)

    params = {}
    for arg in sys.argv[1:]:
        if "=" not in arg:
            print(f"Bad argument '{arg}': expected key=value.", file=sys.stderr)
            sys.exit(2)
        key, value = arg.split("=", 1)
        key = key.strip()
        if key not in ALLOWED:
            print(f"Unknown search key '{key}'.", file=sys.stderr)
            print("Supported keys: " + ", ".join(sorted(ALLOWED)), file=sys.stderr)
            sys.exit(2)
        params[key] = value.strip()

    result = api_call("GET", "/api/points/search" + qs(params))
    pretty(result)
