"""Quick smoke test using Flask's built-in test client (no server needed)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))

# Re-seed for a clean test
os.system("python seed_db.py")

from app import app

client = app.test_client()

def pp(label, resp):
    print(f"\n{'='*60}")
    print(f"  {label}  →  HTTP {resp.status_code}")
    print('='*60)
    print(json.dumps(resp.get_json(), indent=2)[:600])

# 0) Health check
pp("GET /api/health", client.get("/api/health"))

# 1) GET all
pp("GET /api/points", client.get("/api/points"))

# 2) POST new observation with footprint, date, and flight number
pp("POST /api/points", client.post("/api/points",
    json={"name": "Test Peak", "lat": 40.0, "lon": -105.0, "alt": 3000.0,
          "flight_number": 200, "observed_at": "2026-07-15",
          "footprint": {"lat_min": 39.9, "lat_max": 40.1,
                        "lon_min": -105.1, "lon_max": -104.9}}))

# 3) SEARCH by name
pp("SEARCH ?name=mount", client.get("/api/points/search?name=mount"))

# 4) SEARCH by altitude range
pp("SEARCH ?alt_min=3000", client.get("/api/points/search?alt_min=3000"))

# 5) SEARCH by report text
pp("SEARCH ?report_text=icy", client.get("/api/points/search?report_text=icy"))

# 6) SEARCH by observation date range
pp("SEARCH ?observed_from=2026-07-01&observed_to=2026-07-31",
   client.get("/api/points/search?observed_from=2026-07-01&observed_to=2026-07-31"))

# 7) SEARCH by footprint box (should catch Test Peak)
pp("SEARCH footprint box around Boulder",
   client.get("/api/points/search?fp_lat_min=39&fp_lat_max=41&fp_lon_min=-106&fp_lon_max=-104"))

# 8) SEARCH by flight number
pp("SEARCH ?flight_number=101", client.get("/api/points/search?flight_number=101"))

# 9) GET by flight number endpoint
pp("GET /api/points/flight/101", client.get("/api/points/flight/101"))

# 10) GET single observation
pp("GET /api/points/3", client.get("/api/points/3"))

# 11) POST report
pp("POST /api/points/2/reports", client.post("/api/points/2/reports",
    json={"text": "New trail closure on Kaibab."}))

# 12) PUT update (including new fields)
pp("PUT /api/points/5", client.put("/api/points/5",
    json={"name": "Key West Buoy", "alt": 1.0, "flight_number": 110}))

# 13) DELETE
pp("DELETE /api/points/6", client.delete("/api/points/6"))

print("\n✓ All endpoints exercised successfully.")
