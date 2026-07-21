# Observations API

A lightweight REST API and web dashboard for storing and searching drone
observations, built for the [Kashmir World Foundation](https://www.kashmirworldfoundation.org/).
Each observation records a geographic point (lat/lon/altitude), the bounding-box
**footprint** of where the observations were made, an observation timestamp, a
**flight number**, and timestamped text reports.

Backed by Flask + TinyDB (a single JSON file — no database server needed), and
designed to deploy on PythonAnywhere. Ships with an
[Agno](https://docs.agno.com/skills/overview) skill so AI agents can use the
API directly.

## Repository layout

```
.
├── webapp/                    # The Flask application
│   ├── app.py                 #   API routes & validation
│   ├── seed_db.py             #   Seed sample data (wipes the DB!)
│   ├── test_api.py            #   Smoke test (Flask test client, no server needed)
│   ├── templates/index.html   #   KWF-themed web dashboard
│   └── README.md              #   Full API docs + PythonAnywhere deploy guide
├── observations-api-skill/    # Agno skill for AI agents
│   ├── SKILL.md               #   Agent-facing instructions
│   ├── scripts/               #   Runnable API client scripts
│   └── references/            #   Full endpoint spec & worked examples
├── requirements.txt
└── LICENSE
```

## Quick start (local)

```bash
pip install -r requirements.txt
cd webapp
python seed_db.py    # optional: 5 sample observations
python app.py        # → http://127.0.0.1:5000
```

Run the smoke test with `python test_api.py` (re-seeds the database).

## API at a glance

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET    | `/api/health`              | True/false health check |
| GET    | `/api/points`              | All observations |
| POST   | `/api/points`              | Create an observation |
| GET    | `/api/points/search?…`     | Search by name, date range, footprint box, flight number, altitude, report text |
| GET    | `/api/points/flight/<n>`   | Observations by flight number |
| GET    | `/api/points/<id>`         | One observation |
| PUT    | `/api/points/<id>`         | Partial update |
| DELETE | `/api/points/<id>`         | Delete |
| POST   | `/api/points/<id>/reports` | Append a report |

Full endpoint documentation: [webapp/README.md](webapp/README.md) and
[observations-api-skill/references/api-reference.md](observations-api-skill/references/api-reference.md).

## Deploying to PythonAnywhere

Step-by-step instructions are in [webapp/README.md](webapp/README.md).
In short: upload `webapp/` to `/home/<username>/observations-api/`,
`pip install --user flask tinydb`, point a Manual-config web app's WSGI file
at `from app import app as application`, and reload.

## Using the Agno skill

Point it at your deployment and drop the folder where your agent loads skills:

```bash
export OBSERVATIONS_API_URL="https://<username>.pythonanywhere.com"
python observations-api-skill/scripts/health_check.py
```

See [observations-api-skill/README.md](observations-api-skill/README.md).

## License

[MIT](LICENSE)
