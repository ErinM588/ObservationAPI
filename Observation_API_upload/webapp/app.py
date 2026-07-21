"""
Observations API — Flask + TinyDB
=================================
A lightweight REST API for managing drone observations: geographic points
with reports, a bounding-box footprint, an observation timestamp, and a
flight number.

Endpoints
---------
GET  /api/health          – True/false health check.
GET  /api/points          – Return every observation in the database.
POST /api/points          – Create a new observation (auto-assigns id).
GET  /api/points/search   – Query observations by any combination of fields.
GET  /api/points/<id>     – Get a single observation by its id.
PUT  /api/points/<id>     – Update an observation (merge-patch style).
DELETE /api/points/<id>   – Delete an observation by id.
POST /api/points/<id>/reports – Append a report to an existing observation.
GET  /api/points/flight/<n>   – Get all observations for a flight number.

PythonAnywhere
--------------
To deploy on PythonAnywhere:
  1. Upload this project to /home/<username>/observations-api/
  2. Create a new Web App → Manual config → Python 3.10+
  3. Set the Source code directory to /home/<username>/observations-api/
  4. In the WSGI config file, add:
       import sys
       sys.path.insert(0, '/home/<username>/observations-api')
       from app import app as application
  5. pip install flask tinydb (via a Bash console)
  6. Reload the web app.
"""

from flask import Flask, jsonify, request, render_template
from tinydb import TinyDB, Query
from tinydb.operations import set as tinydb_set
from datetime import datetime
import time, os

# ---------------------------------------------------------------------------
# App & DB setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "points_db.json")
db = TinyDB(DB_PATH, indent=2)
points_table = db.table("points")

FOOTPRINT_KEYS = ("lat_min", "lat_max", "lon_min", "lon_max")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _next_id() -> int:
    """Return the next available integer id (survives restarts)."""
    existing = points_table.all()
    if existing:
        max_id = max(p.get("id", 0) for p in existing)
        return max_id + 1
    return 1


def _parse_timestamp(value):
    """Accept a Unix timestamp (number) or an ISO date/datetime string.

    Returns a Unix float, or None if the value cannot be parsed.
    """
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(str(value)).timestamp()
    except ValueError:
        return None


def _validate_footprint(fp):
    """Validate a footprint bounding box. Returns (cleaned, errors)."""
    errors = []
    if not isinstance(fp, dict):
        return None, ["'footprint' must be an object with lat_min, lat_max, lon_min, lon_max."]
    cleaned = {}
    for key in FOOTPRINT_KEYS:
        val = fp.get(key)
        if val is None:
            errors.append(f"'footprint.{key}' is required.")
            continue
        try:
            cleaned[key] = float(val)
        except (TypeError, ValueError):
            errors.append(f"'footprint.{key}' must be a number.")
    if not errors:
        if cleaned["lat_min"] > cleaned["lat_max"]:
            errors.append("'footprint.lat_min' must be <= 'footprint.lat_max'.")
        if cleaned["lon_min"] > cleaned["lon_max"]:
            errors.append("'footprint.lon_min' must be <= 'footprint.lon_max'.")
    return (None, errors) if errors else (cleaned, [])


def _validate_point(data: dict, partial: bool = False):
    """Validate incoming observation data. Returns (cleaned, errors)."""
    errors = []
    cleaned = {}

    if not partial or "name" in data:
        name = data.get("name")
        if not name or not isinstance(name, str):
            errors.append("'name' must be a non-empty string.")
        else:
            cleaned["name"] = name.strip()

    for coord in ("lat", "lon", "alt"):
        if not partial or coord in data:
            val = data.get(coord)
            if val is None and not partial:
                errors.append(f"'{coord}' is required.")
            elif val is not None:
                try:
                    cleaned[coord] = float(val)
                except (TypeError, ValueError):
                    errors.append(f"'{coord}' must be a number.")

    # Optional: footprint bounding box of where the observations were made
    if "footprint" in data and data["footprint"] is not None:
        fp, fp_errors = _validate_footprint(data["footprint"])
        if fp_errors:
            errors.extend(fp_errors)
        else:
            cleaned["footprint"] = fp

    # Optional: observation timestamp (Unix float or ISO date string)
    if "observed_at" in data and data["observed_at"] is not None:
        ts = _parse_timestamp(data["observed_at"])
        if ts is None:
            errors.append("'observed_at' must be a Unix timestamp or ISO date string.")
        else:
            cleaned["observed_at"] = ts

    # Optional: flight number
    if "flight_number" in data and data["flight_number"] is not None:
        try:
            cleaned["flight_number"] = int(data["flight_number"])
        except (TypeError, ValueError):
            errors.append("'flight_number' must be an integer.")

    if "reports" in data:
        reps = data["reports"]
        if not isinstance(reps, list):
            errors.append("'reports' must be a list.")
        else:
            cleaned_reports = []
            for r in reps:
                if not isinstance(r, dict):
                    errors.append("Each report must be an object.")
                    break
                cleaned_reports.append({
                    "time": float(r.get("time", time.time())),
                    "text": str(r.get("text", "")),
                })
            cleaned["reports"] = cleaned_reports

    return (None, errors) if errors else (cleaned, [])


def _boxes_intersect(fp: dict, box: dict) -> bool:
    """True if two lat/lon bounding boxes overlap (inclusive edges)."""
    return (fp["lat_min"] <= box["lat_max"] and fp["lat_max"] >= box["lat_min"]
            and fp["lon_min"] <= box["lon_max"] and fp["lon_max"] >= box["lon_min"])


def _in_box(point: dict, box: dict) -> bool:
    """True if the observation falls inside the query box: its footprint
    overlaps the box, or (if it has no footprint) its lat/lon is inside."""
    fp = point.get("footprint")
    if isinstance(fp, dict) and all(k in fp for k in FOOTPRINT_KEYS):
        return _boxes_intersect(fp, box)
    lat, lon = point.get("lat"), point.get("lon")
    if lat is None or lon is None:
        return False
    return (box["lat_min"] <= lat <= box["lat_max"]
            and box["lon_min"] <= lon <= box["lon_max"])


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

# ── 0) Health check ───────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    """True/false recall: verify the API and database are working."""
    try:
        count = len(points_table)
        return jsonify({"ok": True, "observations": count})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── 1) GET all observations ───────────────────────────────────────────────
@app.route("/api/points", methods=["GET"])
def get_all_points():
    """Return every observation in the database."""
    return jsonify({"count": len(points_table), "points": points_table.all()})


# ── 2) POST a new observation ─────────────────────────────────────────────
@app.route("/api/points", methods=["POST"])
def create_point():
    """Create a new observation. JSON body: name, lat, lon, alt required;
    footprint, observed_at, flight_number, reports optional."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    cleaned, errors = _validate_point(data)
    if errors:
        return jsonify({"error": "Validation failed.", "details": errors}), 400

    cleaned.setdefault("reports", [])
    cleaned.setdefault("observed_at", time.time())
    cleaned["id"] = _next_id()

    points_table.insert(cleaned)
    return jsonify({"message": "Observation created.", "point": cleaned}), 201


# ── 3) SEARCH / query observations ────────────────────────────────────────
@app.route("/api/points/search", methods=["GET"])
def search_points():
    """
    Query observations by any combination of query-string parameters.

    Supported filters (all optional, combine with &):
      name=<substring>        case-insensitive substring match
      lat=<value>             exact numeric match
      lon=<value>             exact numeric match
      alt=<value>             exact numeric match
      lat_min / lat_max       range filter on latitude
      lon_min / lon_max       range filter on longitude
      alt_min / alt_max       range filter on altitude
      id=<int>                exact id match
      flight_number=<int>     exact flight number match
      report_text=<substring> search inside report texts
      observed_from / observed_to
                              observation date range; Unix timestamp or
                              ISO date (e.g. 2026-07-19)
      fp_lat_min / fp_lat_max / fp_lon_min / fp_lon_max
                              footprint search box: returns observations
                              whose footprint overlaps the box (or whose
                              lat/lon falls inside it if no footprint).
                              All four must be supplied together.

    Example: /api/points/search?observed_from=2026-07-01&fp_lat_min=34&fp_lat_max=35&fp_lon_min=74&fp_lon_max=75
    """
    Point = Query()
    conditions = []
    args = request.args

    # Substring match on name
    if "name" in args:
        needle = args["name"].lower()
        conditions.append(Point.name.test(lambda n: needle in n.lower()))

    # Exact numeric matches
    for field in ("lat", "lon", "alt"):
        if field in args:
            try:
                val = float(args[field])
                conditions.append(Point[field] == val)
            except ValueError:
                pass

    # Range filters
    for field in ("lat", "lon", "alt"):
        lo_key, hi_key = f"{field}_min", f"{field}_max"
        if lo_key in args:
            try:
                lo = float(args[lo_key])
                conditions.append(Point[field] >= lo)
            except ValueError:
                pass
        if hi_key in args:
            try:
                hi = float(args[hi_key])
                conditions.append(Point[field] <= hi)
            except ValueError:
                pass

    # Exact id
    if "id" in args:
        try:
            conditions.append(Point.id == int(args["id"]))
        except ValueError:
            pass

    # Exact flight number
    if "flight_number" in args:
        try:
            conditions.append(Point.flight_number == int(args["flight_number"]))
        except ValueError:
            pass

    # Observation date range
    if "observed_from" in args:
        ts = _parse_timestamp(args["observed_from"])
        if ts is None:
            return jsonify({"error": "'observed_from' must be a Unix timestamp or ISO date."}), 400
        conditions.append(Point.observed_at.test(lambda t, lo=ts: t is not None and t >= lo))
    if "observed_to" in args:
        ts = _parse_timestamp(args["observed_to"])
        if ts is None:
            return jsonify({"error": "'observed_to' must be a Unix timestamp or ISO date."}), 400
        conditions.append(Point.observed_at.test(lambda t, hi=ts: t is not None and t <= hi))

    # Footprint search box (applied as a post-filter below)
    box = None
    fp_args = [f"fp_{k}" for k in FOOTPRINT_KEYS]
    fp_present = [k for k in fp_args if k in args]
    if fp_present:
        if len(fp_present) != 4:
            return jsonify({"error": "Footprint search requires all of: "
                                     + ", ".join(fp_args) + "."}), 400
        try:
            box = {k: float(args[f"fp_{k}"]) for k in FOOTPRINT_KEYS}
        except ValueError:
            return jsonify({"error": "Footprint search parameters must be numbers."}), 400
        if box["lat_min"] > box["lat_max"] or box["lon_min"] > box["lon_max"]:
            return jsonify({"error": "Footprint box min values must be <= max values."}), 400

    # Search inside reports
    if "report_text" in args:
        needle = args["report_text"].lower()
        conditions.append(
            Point.reports.test(
                lambda reports: any(needle in r.get("text", "").lower() for r in reports)
            )
        )

    if not conditions and box is None:
        return jsonify({"error": "Provide at least one search parameter."}), 400

    if conditions:
        combined = conditions[0]
        for c in conditions[1:]:
            combined = combined & c
        results = points_table.search(combined)
    else:
        results = points_table.all()

    if box is not None:
        results = [p for p in results if _in_box(p, box)]

    return jsonify({"count": len(results), "points": results})


# ── 4) GET observations by flight number ──────────────────────────────────
@app.route("/api/points/flight/<int:flight_number>", methods=["GET"])
def get_by_flight(flight_number):
    """Return every observation recorded on the given flight."""
    Point = Query()
    results = points_table.search(Point.flight_number == flight_number)
    return jsonify({"flight_number": flight_number,
                    "count": len(results), "points": results})


# ── 5) GET single observation ─────────────────────────────────────────────
@app.route("/api/points/<int:point_id>", methods=["GET"])
def get_point(point_id):
    Point = Query()
    result = points_table.search(Point.id == point_id)
    if not result:
        return jsonify({"error": f"Observation {point_id} not found."}), 404
    return jsonify({"point": result[0]})


# ── 6) UPDATE an observation ──────────────────────────────────────────────
@app.route("/api/points/<int:point_id>", methods=["PUT"])
def update_point(point_id):
    Point = Query()
    if not points_table.search(Point.id == point_id):
        return jsonify({"error": f"Observation {point_id} not found."}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    cleaned, errors = _validate_point(data, partial=True)
    if errors:
        return jsonify({"error": "Validation failed.", "details": errors}), 400

    for key, val in cleaned.items():
        points_table.update(tinydb_set(key, val), Point.id == point_id)

    updated = points_table.search(Point.id == point_id)[0]
    return jsonify({"message": "Observation updated.", "point": updated})


# ── 7) DELETE an observation ──────────────────────────────────────────────
@app.route("/api/points/<int:point_id>", methods=["DELETE"])
def delete_point(point_id):
    Point = Query()
    if not points_table.search(Point.id == point_id):
        return jsonify({"error": f"Observation {point_id} not found."}), 404
    points_table.remove(Point.id == point_id)
    return jsonify({"message": f"Observation {point_id} deleted."})


# ── 8) POST a report to an observation ────────────────────────────────────
@app.route("/api/points/<int:point_id>/reports", methods=["POST"])
def add_report(point_id):
    Point = Query()
    results = points_table.search(Point.id == point_id)
    if not results:
        return jsonify({"error": f"Observation {point_id} not found."}), 404

    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "'text' field is required."}), 400

    report = {
        "time": float(data.get("time", time.time())),
        "text": str(data["text"]),
    }

    existing = results[0]
    existing["reports"].append(report)
    points_table.update(tinydb_set("reports", existing["reports"]), Point.id == point_id)

    return jsonify({"message": "Report added.", "point": points_table.search(Point.id == point_id)[0]}), 201


# ---------------------------------------------------------------------------
# Web UI (serves the single-page dashboard)
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
