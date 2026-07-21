# Observations API — Flask + TinyDB

A lightweight REST API for managing drone observations for the Kashmir World
Foundation, backed by a JSON file database (TinyDB). Each observation is a
geographic point with an altitude, a bounding-box footprint of where the
observations were made, an observation timestamp, a flight number, and
timestamped text reports. Includes a KWF-themed web dashboard for browsing,
creating, searching, and annotating observations.

---

## Quick Start (local)

```bash
# 1. Install dependencies
pip install flask tinydb

# 2. Seed sample data
python seed_db.py

# 3. Run the server
python app.py
# → http://127.0.0.1:5000
```

---

## Deploy on PythonAnywhere

1. **Upload** the project folder to `/home/<username>/observations-api/`.
2. **Open a Bash console** and install dependencies:
   ```bash
   pip install --user flask tinydb
   cd ~/observations-api && python seed_db.py
   ```
3. **Create a Web App** → Manual configuration → Python 3.10+.
4. **Set Source code** to `/home/<username>/observations-api`.
5. **Edit the WSGI file** (`/var/www/<username>_pythonanywhere_com_wsgi.py`):
   ```python
   import sys
   sys.path.insert(0, '/home/<username>/observations-api')
   from app import app as application
   ```
6. **Reload** the web app.

---

## API Endpoints

| Method | Path                        | Description                                    |
| ------ | --------------------------- | ---------------------------------------------- |
| GET    | `/api/health`               | True/false health check                        |
| GET    | `/api/points`               | Return all observations                        |
| POST   | `/api/points`               | Create a new observation                       |
| GET    | `/api/points/search?…`      | Query by name, date, footprint, flight, etc.   |
| GET    | `/api/points/flight/<n>`    | All observations for a flight number           |
| GET    | `/api/points/<id>`          | Get a single observation                       |
| PUT    | `/api/points/<id>`          | Update an observation (partial)                |
| DELETE | `/api/points/<id>`          | Delete an observation                          |
| POST   | `/api/points/<id>/reports`  | Append a report to an observation              |

### Health Check

`GET /api/health` returns `{"ok": true, "observations": <count>}` when the API
and database are working, or `{"ok": false, "error": "..."}` with HTTP 500 if
not — a simple true/false recall to confirm the service is up.

### Search Parameters

All optional — combine with `&`:

| Param        | Type   | Behaviour                   |
| ------------ | ------ | --------------------------- |
| `name`       | string | Case-insensitive substring  |
| `id`         | int    | Exact match                 |
| `flight_number` | int | Exact match                  |
| `lat`, `lon`, `alt` | float | Exact match          |
| `lat_min` / `lat_max` | float | Range filter on point latitude |
| `lon_min` / `lon_max` | float | Range filter on point longitude |
| `alt_min` / `alt_max` | float | Range filter         |
| `observed_from` / `observed_to` | date | Observation date range; ISO date (`2026-07-19`) or Unix timestamp |
| `fp_lat_min`, `fp_lat_max`, `fp_lon_min`, `fp_lon_max` | float | Footprint search box — returns observations whose footprint overlaps the box (or whose lat/lon falls inside it if they have no footprint). All four required together. |
| `report_text`| string | Substring in any report     |

---

## Observation Schema

```json
{
  "id":            1,
  "name":          "Mount Rainier Summit",
  "lat":           46.8523,
  "lon":           -121.7603,
  "alt":           4392.0,
  "flight_number": 101,
  "observed_at":   1712345678.0,
  "footprint": {
    "lat_min": 46.83, "lat_max": 46.87,
    "lon_min": -121.78, "lon_max": -121.74
  },
  "reports": [
    { "time": 1712345678.0, "text": "Clear skies." }
  ]
}
```

- `footprint`, `flight_number` are optional. `observed_at` defaults to the
  creation time if not supplied; it accepts a Unix timestamp or ISO date string.

---

## Project Files

```
observations-api/
├── app.py              # Flask application & API routes
├── seed_db.py          # Populate DB with sample data
├── points_db.json      # TinyDB database (auto-created)
├── test_api.py         # Smoke test (Flask test client)
├── templates/
│   └── index.html      # KWF-themed web dashboard UI
└── README.md
```
