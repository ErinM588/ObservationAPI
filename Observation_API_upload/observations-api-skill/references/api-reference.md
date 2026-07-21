# Observations API — Full Reference

## Base URL

All endpoints are relative to the deployed site root, e.g.
`https://yourname.pythonanywhere.com`. Scripts read this from the
`OBSERVATIONS_API_URL` environment variable (legacy `POINTS_API_URL` also
accepted).

## Authentication

None. The API is currently open. Deploy behind an auth proxy if you need
access control.

## Content Types

All request bodies are `application/json`. All responses are
`application/json` except for the root `/` which serves the HTML dashboard.

---

## Endpoints

### `GET /api/health`

True/false health check: confirms the API and database are working.

**Response 200**

```json
{ "ok": true, "observations": 5 }
```

**Response 500** — `{ "ok": false, "error": "..." }` if the database cannot
be read.

---

### `GET /api/points`

Return every observation in the database.

**Response 200**

```json
{
  "count": 5,
  "points": [
    {
      "id": 1,
      "name": "Mount Rainier Summit",
      "lat": 46.8523,
      "lon": -121.7603,
      "alt": 4392.0,
      "flight_number": 101,
      "observed_at": 1712345678.0,
      "footprint": {
        "lat_min": 46.83, "lat_max": 46.87,
        "lon_min": -121.78, "lon_max": -121.74
      },
      "reports": [
        { "time": 1712345678.0, "text": "Clear skies." }
      ]
    }
  ]
}
```

---

### `POST /api/points`

Create a new observation. The server auto-assigns `id`.

**Request body**

```json
{
  "name": "Mount Hood",
  "lat":  45.3735,
  "lon":  -121.6959,
  "alt":  3429.0,
  "flight_number": 105,
  "observed_at": "2026-07-19",
  "footprint": {
    "lat_min": 45.36, "lat_max": 45.39,
    "lon_min": -121.71, "lon_max": -121.68
  }
}
```

- `name`, `lat`, `lon`, `alt` are required.
- `flight_number` (integer), `observed_at` (Unix timestamp or ISO date
  string), and `footprint` (all four bounds, floats, min <= max) are optional.
- `observed_at` defaults to the creation time.
- Optional: include a `reports` array to seed initial reports.

**Response 201**

```json
{
  "message": "Observation created.",
  "point": {
    "id": 6,
    "name": "Mount Hood",
    "lat": 45.3735,
    "lon": -121.6959,
    "alt": 3429.0,
    "flight_number": 105,
    "observed_at": 1784419200.0,
    "footprint": {
      "lat_min": 45.36, "lat_max": 45.39,
      "lon_min": -121.71, "lon_max": -121.68
    },
    "reports": []
  }
}
```

**Response 400** — validation failure. Body includes `error` and `details` array.

---

### `GET /api/points/search`

Filter observations by any combination of query-string parameters. All
filters combine with AND semantics.

| Parameter | Type | Behaviour |
| --- | --- | --- |
| `name` | string | case-insensitive substring match |
| `id` | int | exact match |
| `flight_number` | int | exact match |
| `lat`, `lon`, `alt` | float | exact numeric match |
| `lat_min`, `lat_max` | float | latitude range on the observation point (inclusive) |
| `lon_min`, `lon_max` | float | longitude range on the observation point (inclusive) |
| `alt_min`, `alt_max` | float | altitude range (inclusive) |
| `observed_from`, `observed_to` | date | observation date range; Unix timestamp or ISO date (e.g. `2026-07-19`) |
| `fp_lat_min`, `fp_lat_max`, `fp_lon_min`, `fp_lon_max` | float | footprint search box; returns observations whose footprint overlaps the box, or whose lat/lon falls inside it if they have no footprint. All four required together. |
| `report_text` | string | substring within any report's text |

At least one parameter is required.

**Response 200**

```json
{
  "count": 2,
  "points": [ /* matching observations */ ]
}
```

**Response 400** — no parameters supplied, malformed date, or incomplete
footprint box.

---

### `GET /api/points/flight/<flight_number>`

Return every observation recorded on the given flight.

**Response 200**

```json
{
  "flight_number": 101,
  "count": 2,
  "points": [ /* observations on flight 101 */ ]
}
```

Returns `count: 0` with an empty list if no observations match.

---

### `GET /api/points/<id>`

Get a single observation by its integer id.

**Response 200** — `{ "point": {...} }`
**Response 404** — observation does not exist.

---

### `PUT /api/points/<id>`

Partial update. Only include the fields you want to change (including
`footprint`, `observed_at`, `flight_number`). Returns the updated observation.

**Request body**

```json
{ "name": "New Name", "alt": 3500, "flight_number": 106 }
```

**Response 200** — `{ "message": "Observation updated.", "point": {...} }`
**Response 400** / **404** — on validation/missing id.

---

### `DELETE /api/points/<id>`

Delete an observation and all its reports.

**Response 200** — `{ "message": "Observation N deleted." }`
**Response 404** — observation does not exist.

---

### `POST /api/points/<id>/reports`

Append a report to an existing observation. The server stamps `time` with the
current Unix timestamp unless the body supplies one.

**Request body**

```json
{ "text": "Trail closed above 3000 m due to ice." }
```

Optional: supply `time` to backdate.

**Response 201** — returns the full updated observation (useful for
confirming the report was added).
**Response 400** — missing `text`.
**Response 404** — observation does not exist.

---

## Error Format

All error responses are JSON:

```json
{ "error": "Short reason.", "details": ["optional", "list"] }
```

## Validation Rules

- `name`: non-empty string, trimmed.
- `lat`, `lon`, `alt`: must coerce to `float`.
- `flight_number`: must coerce to `int`.
- `observed_at`: Unix timestamp (number) or ISO date/datetime string.
- `footprint`: object with all four of `lat_min`, `lat_max`, `lon_min`,
  `lon_max` as numbers, with each min <= its max.
- Client-side convention (not enforced by server): `-90 ≤ lat ≤ 90`,
  `-180 ≤ lon ≤ 180`. Scripts in this skill enforce these ranges.

## Rate Limits

None. If deployed on PythonAnywhere free tier, the site may cold-start
after inactivity (first request takes a few extra seconds).
