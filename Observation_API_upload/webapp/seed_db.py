"""
Seed the TinyDB database with sample drone observations.
Run once:  python seed_db.py
"""
import time, os
from tinydb import TinyDB

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "points_db.json")

# Start fresh
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

db = TinyDB(DB_PATH, indent=2)
table = db.table("points")

SEED = [
    {
        "id": 1,
        "name": "Mount Rainier Summit",
        "lat": 46.8523,
        "lon": -121.7603,
        "alt": 4392.0,
        "footprint": {"lat_min": 46.83, "lat_max": 46.87, "lon_min": -121.78, "lon_max": -121.74},
        "observed_at": time.time() - 86400 * 3,
        "flight_number": 101,
        "reports": [
            {"time": time.time() - 86400 * 3, "text": "Clear skies, winds calm at summit."},
            {"time": time.time() - 86400, "text": "Heavy cloud cover below 3000 m, icy conditions."},
        ],
    },
    {
        "id": 2,
        "name": "Grand Canyon South Rim",
        "lat": 36.0544,
        "lon": -112.1401,
        "alt": 2100.0,
        "footprint": {"lat_min": 36.04, "lat_max": 36.07, "lon_min": -112.16, "lon_max": -112.12},
        "observed_at": time.time() - 86400 * 7,
        "flight_number": 101,
        "reports": [
            {"time": time.time() - 86400 * 7, "text": "Bright Angel Trail open. Temps around 28 °C at rim."},
        ],
    },
    {
        "id": 3,
        "name": "Yellowstone Old Faithful",
        "lat": 44.4605,
        "lon": -110.8281,
        "alt": 2240.0,
        "footprint": {"lat_min": 44.45, "lat_max": 44.47, "lon_min": -110.84, "lon_max": -110.82},
        "observed_at": time.time() - 3600 * 12,
        "flight_number": 102,
        "reports": [
            {"time": time.time() - 3600 * 12, "text": "Eruption interval ~94 min today."},
            {"time": time.time() - 3600 * 2, "text": "Boardwalk crowded, arrive early for good view."},
        ],
    },
    {
        "id": 4,
        "name": "Denali Base Camp",
        "lat": 63.0695,
        "lon": -151.0074,
        "alt": 2195.0,
        "footprint": {"lat_min": 63.05, "lat_max": 63.09, "lon_min": -151.03, "lon_max": -150.98},
        "observed_at": time.time() - 86400 * 14,
        "flight_number": 103,
        "reports": [
            {"time": time.time() - 86400 * 14, "text": "Snow accumulation 30 cm overnight."},
        ],
    },
    {
        "id": 5,
        "name": "Key West Southernmost Point",
        "lat": 24.5465,
        "lon": -81.7986,
        "alt": 0.5,
        "footprint": {"lat_min": 24.54, "lat_max": 24.56, "lon_min": -81.81, "lon_max": -81.79},
        "observed_at": time.time() - 86400 * 2,
        "flight_number": 104,
        "reports": [
            {"time": time.time() - 86400 * 2, "text": "Gorgeous sunset at 7:48 PM."},
            {"time": time.time() - 3600 * 6, "text": "Water temp 27 °C, calm seas."},
        ],
    },
]

table.insert_multiple(SEED)
print(f"✓ Seeded {len(SEED)} observations into {DB_PATH}")
