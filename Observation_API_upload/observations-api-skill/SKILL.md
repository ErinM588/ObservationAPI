---
name: observations-api
description: Interact with the Observations API — a Flask + TinyDB REST service for managing drone observations with lat/lon/altitude, a bounding-box footprint, observation timestamps, flight numbers, and timestamped text reports. Use this skill when the user asks to list, search, create, update, or annotate observations, check API health, or look up observations by flight number, date, or footprint.
license: MIT
metadata:
  version: "2.0.0"
  tags: ["geospatial", "rest-api", "drone"]
---

# Observations API Skill

Interact with a deployed Observations API: a Flask + TinyDB REST service that
stores drone observations — geographic points with a bounding-box footprint,
an observation timestamp, a flight number, and timestamped text reports. The
database is pre-seeded with five US landmarks:

| id | name | lat | lon | alt (m) | flight |
| -- | ---- | --- | --- | ------- | ------ |
| 1 | Mount Rainier Summit       | 46.8523 | -121.7603 | 4392.0 | 101 |
| 2 | Grand Canyon South Rim     | 36.0544 | -112.1401 | 2100.0 | 101 |
| 3 | Yellowstone Old Faithful   | 44.4605 | -110.8281 | 2240.0 | 102 |
| 4 | Denali Base Camp           | 63.0695 | -151.0074 | 2195.0 | 103 |
| 5 | Key West Southernmost Point| 24.5465 |  -81.7986 |    0.5 | 104 |

## When to Use

- Check whether the API is working (true/false health check).
- List or browse observations in the database.
- Create a new observation with a name, latitude, longitude, altitude, and
  optionally a footprint bounding box, observation date, and flight number.
- Search by name, coordinate ranges, altitude ranges, observation date range,
  footprint box, flight number, or report text.
- Fetch all observations for a given flight number.
- Add a report (observation note, condition note) to an existing observation.
- Get, update, or delete an observation by its integer id.

## Configuration

Set `OBSERVATIONS_API_URL` to the deployed site root before running any script
(the legacy `POINTS_API_URL` is also accepted):

```
export OBSERVATIONS_API_URL="https://yourname.pythonanywhere.com"
```

If unset, scripts default to `http://127.0.0.1:5000` for local dev.

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
    { "time": 1712345678.0, "text": "Clear skies, winds calm at summit." }
  ]
}
```

- `id` is assigned by the server on creation — do not supply it.
- `lat`, `lon`, `alt` are floats. Altitude is in meters.
- `footprint` (optional) is the bounding box of where the observations were
  made: `{lat_min, lat_max, lon_min, lon_max}` floats.
- `observed_at` is a Unix timestamp; defaults to creation time. When creating,
  you may also send an ISO date string (e.g. `2026-07-19`).
- `flight_number` (optional) is an integer identifying the drone flight.
- `reports` is a list of `{time, text}` objects. `time` is a Unix timestamp.

## Available Scripts

| Script | Purpose |
| --- | --- |
| `scripts/health_check.py` | True/false API health check. No args; exits 0 iff ok. |
| `scripts/get_points.py` | Fetch every observation. No args. |
| `scripts/get_point.py` | Fetch one observation. Args: `<id>`. |
| `scripts/get_flight.py` | Fetch all observations for a flight. Args: `<flight_number>`. |
| `scripts/create_point.py` | Create an observation. Args: `<name> <lat> <lon> <alt>` plus optional `flight_number=`, `observed_at=`, `footprint=lat_min,lat_max,lon_min,lon_max`. |
| `scripts/search_points.py` | Search by fields. Args: `key=value ...` |
| `scripts/add_report.py` | Add a report. Args: `<id> "<text>"`. |
| `scripts/delete_point.py` | Delete an observation. Args: `<id>`. |

Each script prints the JSON response to stdout and exits non-zero on HTTP or
validation errors (error detail on stderr).

## Search Parameters

- `name=<substring>` — case-insensitive
- `id=<int>` — exact match
- `flight_number=<int>` — exact match
- `lat`, `lon`, `alt` — exact float match
- `lat_min` / `lat_max`, `lon_min` / `lon_max`, `alt_min` / `alt_max` — ranges
  on the observation point
- `observed_from` / `observed_to` — observation date range; Unix timestamp or
  ISO date (e.g. `2026-07-19`)
- `fp_lat_min` / `fp_lat_max` / `fp_lon_min` / `fp_lon_max` — footprint search
  box; returns observations whose footprint overlaps the box (or whose lat/lon
  is inside it if they have no footprint). All four must be given together.
- `report_text=<substring>` — searches inside all reports

Multiple parameters combine with AND. Full spec in `references/api-reference.md`.
Worked examples in `references/examples.md`.

## Notes

- Scripts validate lat ∈ [-90, 90] and lon ∈ [-180, 180] before sending.
- Timestamps are Unix floats; convert with `datetime.fromtimestamp(t)` when
  presenting to a user.
- If a call fails unexpectedly, run `scripts/health_check.py` first to
  distinguish an API outage from a bad request.
