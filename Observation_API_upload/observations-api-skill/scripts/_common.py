"""Shared helpers for Observations API scripts."""
import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = os.environ.get(
    "OBSERVATIONS_API_URL",
    os.environ.get("POINTS_API_URL", "http://127.0.0.1:5000"),
).rstrip("/")


def api_call(method: str, path: str, body: dict | None = None) -> dict:
    """Make an HTTP request to the Observations API and return parsed JSON.

    Exits non-zero with a message on stderr if the call fails.
    """
    url = f"{BASE_URL}{path}"
    data = None
    headers = {"Accept": "application/json"}

    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} from {method} {url}", file=sys.stderr)
        print(body_text, file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Could not reach {url}: {e.reason}", file=sys.stderr)
        print("Is POINTS_API_URL set correctly?", file=sys.stderr)
        sys.exit(1)


def qs(params: dict) -> str:
    """Build a query string from non-empty params."""
    clean = {k: v for k, v in params.items() if v not in (None, "")}
    return "?" + urllib.parse.urlencode(clean) if clean else ""


def pretty(obj) -> None:
    """Print JSON with 2-space indent."""
    print(json.dumps(obj, indent=2, ensure_ascii=False))
