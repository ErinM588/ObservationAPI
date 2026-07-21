#!/usr/bin/env python3
"""Create a new observation in the database.

Usage:
    python scripts/create_point.py <name> <lat> <lon> <alt> [key=value ...]

Optional key=value fields:
    flight_number=<int>       drone flight number
    observed_at=<ts|date>     Unix timestamp or ISO date (e.g. 2026-07-19)
    footprint=<lat_min,lat_max,lon_min,lon_max>
                              bounding box of where observations were made

Examples:
    python scripts/create_point.py "Mount Hood" 45.3735 -121.6959 3429
    python scripts/create_point.py "Hirpora Survey" 33.65 74.66 3100 \
        flight_number=105 observed_at=2026-07-19 footprint=33.6,33.7,74.6,74.7

The server auto-assigns an integer id. Latitude must be in [-90, 90],
longitude in [-180, 180]. Altitude is in meters.
"""
import sys
from _common import api_call, pretty

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print('Usage: create_point.py "<name>" <lat> <lon> <alt> '
              '[flight_number=<int>] [observed_at=<ts|date>] '
              '[footprint=<lat_min,lat_max,lon_min,lon_max>]', file=sys.stderr)
        sys.exit(2)

    name = sys.argv[1].strip()
    if not name:
        print("Name cannot be empty.", file=sys.stderr)
        sys.exit(2)

    try:
        lat = float(sys.argv[2])
        lon = float(sys.argv[3])
        alt = float(sys.argv[4])
    except ValueError as e:
        print(f"Invalid numeric argument: {e}", file=sys.stderr)
        sys.exit(2)

    if not -90 <= lat <= 90:
        print(f"Latitude {lat} out of range [-90, 90].", file=sys.stderr)
        sys.exit(2)
    if not -180 <= lon <= 180:
        print(f"Longitude {lon} out of range [-180, 180].", file=sys.stderr)
        sys.exit(2)

    body = {"name": name, "lat": lat, "lon": lon, "alt": alt}

    for arg in sys.argv[5:]:
        if "=" not in arg:
            print(f"Bad argument '{arg}': expected key=value.", file=sys.stderr)
            sys.exit(2)
        key, value = arg.split("=", 1)
        key, value = key.strip(), value.strip()
        if key == "flight_number":
            try:
                body["flight_number"] = int(value)
            except ValueError:
                print(f"flight_number '{value}' is not an integer.", file=sys.stderr)
                sys.exit(2)
        elif key == "observed_at":
            body["observed_at"] = value
        elif key == "footprint":
            parts = value.split(",")
            if len(parts) != 4:
                print("footprint must be lat_min,lat_max,lon_min,lon_max.", file=sys.stderr)
                sys.exit(2)
            try:
                lat_min, lat_max, lon_min, lon_max = (float(p) for p in parts)
            except ValueError:
                print("footprint values must be numbers.", file=sys.stderr)
                sys.exit(2)
            body["footprint"] = {"lat_min": lat_min, "lat_max": lat_max,
                                 "lon_min": lon_min, "lon_max": lon_max}
        else:
            print(f"Unknown optional key '{key}'.", file=sys.stderr)
            sys.exit(2)

    result = api_call("POST", "/api/points", body)
    pretty(result)
