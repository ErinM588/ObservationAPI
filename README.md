# Points API Skill

An [Agno Skill](https://docs.agno.com/skills/overview) that lets an AI agent
use a deployed Points API — a Flask + TinyDB REST service for managing
geographic points with lat/lon/altitude and timestamped reports.

## Contents

```
points-api-skill/
├── SKILL.md                    # Agent-facing instructions
├── README.md                   # This file
├── scripts/                    # Executable scripts the agent runs
│   ├── _common.py              # Shared HTTP helper
│   ├── get_points.py
│   ├── get_point.py
│   ├── create_point.py
│   ├── search_points.py
│   ├── add_report.py
│   └── delete_point.py
└── references/                 # Loaded on demand
    ├── api-reference.md        # Full endpoint spec
    └── examples.md             # Worked examples
```

## Install

1. Drop this folder into a directory your Agno agent loads skills from
   (e.g. `~/agno-skills/points-api-skill/`).

2. Set the API URL:

   ```
   export POINTS_API_URL="https://yourname.pythonanywhere.com"
   ```

3. Load the skill in your agent. Consult the
   [Agno docs](https://docs.agno.com/skills/loading-skills) for the current
   API; at the time of writing it is:

   ```python
   from agno.agent import Agent
   from agno.skills import Skills, LocalSkills

   agent = Agent(
       model=<your-model>,
       skills=Skills(loaders=[LocalSkills("~/agno-skills")]),
   )
   ```

## Testing standalone

The scripts work without Agno — you can run them directly:

```
export POINTS_API_URL="https://yourname.pythonanywhere.com"
python scripts/get_points.py
python scripts/search_points.py name=mount
python scripts/create_point.py "Test Peak" 40.0 -105.0 3000
```

Each prints JSON to stdout and exits non-zero on failure.

## Customizing

If your deployment differs:

- `SKILL.md` — update schema if you changed point fields.
- `scripts/_common.py` — change default URL; add auth headers here if the
  API is protected.
- `references/api-reference.md` — keep endpoint docs in sync.

## License

MIT.
