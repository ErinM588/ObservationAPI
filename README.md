# Points API — Flask + TinyDB

A lightweight REST API for managing geographic points-of-interest, backed by a
JSON file database (TinyDB). Includes a dark-themed web dashboard for browsing,
creating, searching, and annotating points.

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

1. **Upload** the project folder to `/home/<username>/points-api/`.
2. **Open a Bash console** and install dependencies:
   ```bash
   pip install --user flask tinydb
   cd ~/points-api && python seed_db.py
   ```
3. **Create a Web App** → Manual configuration → Python 3.10+.
4. **Set Source code** to `/home/<username>/points-api`.
5. **Edit the WSGI file** (`/var/www/<username>_pythonanywhere_com_wsgi.py`):
   ```python
   import sys
   sys.path.insert(0, '/home/<username>/points-api')
   from app import app as application
   ```
6. **Reload** the web app.

---

## API Endpoints

| Method | Path                        | Description                              |
| ------ | --------------------------- | ---------------------------------------- |
| GET    | `/api/points`               | Return all points                        |
| POST   | `/api/points`               | Create a new point                       |
| GET    | `/api/points/search?…`      | Query by name, coords, altitude, reports |
| GET    | `/api/points/<id>`          | Get a single point                       |
| PUT    | `/api/points/<id>`          | Update a point (partial)                 |
| DELETE | `/api/points/<id>`          | Delete a point                           |
| POST   | `/api/points/<id>/reports`  | Append a report to a point               |

### Search Parameters

All optional — combine with `&`:

| Param        | Type   | Behaviour                   |
| ------------ | ------ | --------------------------- |
| `name`       | string | Case-insensitive substring  |
| `id`         | int    | Exact match                 |
| `lat`, `lon`, `alt` | float | Exact match          |
| `lat_min` / `lat_max` | float | Range filter         |
| `lon_min` / `lon_max` | float | Range filter         |
| `alt_min` / `alt_max` | float | Range filter         |
| `report_text`| string | Substring in any report     |

---

## Point Schema

```json
{
  "id":      1,
  "name":    "Mount Rainier Summit",
  "lat":     46.8523,
  "lon":     -121.7603,
  "alt":     4392.0,
  "reports": [
    { "time": 1712345678.0, "text": "Clear skies." }
  ]
}
```

---

## Project Files

```
points-api/
├── app.py              # Flask application & API routes
├── seed_db.py          # Populate DB with sample data
├── points_db.json      # TinyDB database (auto-created)
├── templates/
│   └── index.html      # Web dashboard UI
└── README.md
```
