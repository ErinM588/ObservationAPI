# Worked Examples

Each example uses the real seeded dataset (5 US landmarks — see the table in
`SKILL.md`). Results shown here match what the live API returns.

## Health check (true/false recall)

```
python scripts/health_check.py
```

Prints `{"ok": true, "observations": 5}` and exits 0 when the API and
database are working; exits non-zero otherwise. Run this first if any other
call fails unexpectedly.

## List everything

```
python scripts/get_points.py
```

Returns `count: 5` with all seeded observations. When presenting to a user,
summarize in natural language — don't dump the raw JSON.

## Search by name (substring, case-insensitive)

```
python scripts/search_points.py name=mount
```

Matches id 1 — Mount Rainier Summit.

```
python scripts/search_points.py name=canyon
```

Matches id 2 — Grand Canyon South Rim.

## Search by altitude range

```
python scripts/search_points.py alt_min=3000
```

Matches id 1 only (Mount Rainier at 4392 m is the only observation above
3000 m in the seed data).

```
python scripts/search_points.py alt_max=100
```

Matches id 5 — Key West (0.5 m).

## Search by observation date

```
python scripts/search_points.py observed_from=2026-07-01 observed_to=2026-07-31
```

Matches every observation whose `observed_at` falls in that range. Values may
be ISO dates or Unix timestamps. Note `observed_to=2026-07-31` means midnight
at the start of the 31st — use the following day to include the whole day.

## Search by footprint (bounding box)

```
python scripts/search_points.py fp_lat_min=44 fp_lat_max=47 fp_lon_min=-122 fp_lon_max=-110
```

Matches ids 1 and 3 — observations whose footprint overlaps the box covering
the northwestern US. All four `fp_*` parameters must be supplied together.
Combine with a date range to answer "what was observed in this area during
this period":

```
python scripts/search_points.py observed_from=2026-07-01 fp_lat_min=44 fp_lat_max=47 fp_lon_min=-122 fp_lon_max=-110
```

## Search by flight number

```
python scripts/search_points.py flight_number=101
```

Matches ids 1 and 2 — both recorded on flight 101.

## Get all observations for a flight

```
python scripts/get_flight.py 101
```

Returns `flight_number: 101, count: 2` with Mount Rainier Summit and Grand
Canyon South Rim.

## Search report text

```
python scripts/search_points.py report_text=icy
```

Matches id 1 — Mount Rainier has a report containing "icy conditions".

```
python scripts/search_points.py report_text=eruption
```

Matches id 3 — Yellowstone Old Faithful has a report about the eruption
interval.

## Combined search (AND)

```
python scripts/search_points.py name=mount alt_min=3000
```

Matches id 1 — both conditions true.

```
python scripts/search_points.py name=canyon alt_min=3000
```

Returns `count: 0` — Grand Canyon South Rim is below 3000 m. If the user
expected a result, relax one filter at a time.

## Get a single observation

```
python scripts/get_point.py 3
```

Returns Yellowstone Old Faithful with both of its reports.

## Add a new observation

Check for duplicates first, then create (footprint is
`lat_min,lat_max,lon_min,lon_max`):

```
python scripts/search_points.py name=hood
python scripts/create_point.py "Mount Hood" 45.3735 -121.6959 3429 flight_number=105 observed_at=2026-07-19 footprint=45.36,45.39,-121.71,-121.68
```

The server assigns id 6 (next available).

## Add a report to an existing observation

```
python scripts/add_report.py 3 "Boardwalk repairs completed, full access restored."
```

The report is appended to Yellowstone Old Faithful with the current
Unix timestamp. Response returns the full updated observation.

## Delete an observation

Confirm with the user first:

```
python scripts/get_point.py 6
python scripts/delete_point.py 6
```

## Error handling

- **URL unreachable** — `OBSERVATIONS_API_URL` is wrong or the server is
  down. Run `health_check.py` to confirm.
- **HTTP 404** — id doesn't exist. Run `get_points.py` to list valid ids
  (seeded ids are 1–5; new observations get 6, 7, … as they're created).
- **HTTP 400** — validation failed. The response's `details` array lists
  which fields were invalid. For footprint searches, all four `fp_*`
  parameters must be present.
