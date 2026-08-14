# Streamlit migration: sales dashboard

This is the runnable result of the documentation's
[Streamlit migration walkthrough](https://hedron.readthedocs.io/en/latest/guides/streamlit-migration/).
It converts a single-file Streamlit dashboard into a Hedron page with typed query filters,
metrics, a summary table, and a `hedron[data]` data table.

## Run from this repository

From the repository root:

```bash
uv sync
uv run uvicorn app:app --app-dir examples/streamlit-migration --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Select a region, move the minimum
revenue slider, and choose **Apply filters**. The submitted filters appear in the URL.

## Run as a standalone copy

Copy `app.py` into an empty directory, then:

```bash
uv init
uv add "hedron[data]>=0.37.0,<0.38" "uvicorn[standard]"
uv run uvicorn app:app --reload
```

The fallback session secret is only for localhost. Set `HEDRON_SESSION_SECRET` before
sharing or deploying the app.

## Verify without a browser

Create `test_app.py` beside `app.py`:

```python
from fastapi.testclient import TestClient

from app import app


def test_default_totals() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "$22,600" in response.text
    assert ">213<" in response.text


def test_north_filter() -> None:
    with TestClient(app) as client:
        response = client.get("/?region=North&minimum=4000")

    assert response.status_code == 200
    assert "$8,700" in response.text
    assert "$4,100" in response.text
    assert "$4,600" in response.text
    assert "$3,600" not in response.text


def test_invalid_filter_is_rejected() -> None:
    with TestClient(app) as client:
        response = client.get("/?minimum=9000")

    assert response.status_code == 422
```

Run `uv run pytest`. Next, add a state-changing workflow using an explicit POST action;
do not put a write in the GET page route. Continue with
[Execution and state](https://hedron.readthedocs.io/en/latest/guides/streamlit-execution-state/).
