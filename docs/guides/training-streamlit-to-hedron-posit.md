# Hands-on training: Streamlit to Hedron on Posit

Use this instructor-ready guide to run a **3.5-hour workshop** for Python developers who
currently build Streamlit apps and want to build Hedron applications in Posit
Workbench and publish them to Posit Connect.

Participants finish with a migrated sales dashboard that has validated URL filters, a
server-rendered component tree, an allowlisted HTMX fragment, HTTP-level tests, and one
application object that adapts to local, Workbench, and Connect environments.

This workshop targets the Hedron **0.67.x** train (`hedron>=0.67.0,<0.68`) and Python
**3.11–3.14** so it matches the current `hedron-posit` adapter. Before scheduling it, check the
current [capability matrix](whats-ready.md) and
[compatibility guide](../COMPATIBILITY.md) against your Posit versions and internal package mirror.

## Training at a glance

| Item | Plan |
|---|---|
| Audience | Software developers comfortable with Python and basic web concepts |
| Prior Hedron knowledge | None |
| Duration | 3 hours 30 minutes, including a 10-minute break |
| Delivery | Instructor demonstration followed by individual or paired labs |
| Development target | Local machine or Posit Workbench |
| Publishing target | A non-production Posit Connect space |
| Final artifact | A tested Hedron sales dashboard prepared for Connect |
| Recommended ratio | One facilitator or helper for every 10–12 participants |

If Connect access is unavailable, complete [Labs 0–4](#lab-4--test-the-http-contracts) and demonstrate
[Lab 5](#lab-5--prepare-and-publish-to-posit-connect) from one facilitator account. The learning
objectives do not depend on every participant publishing their own copy.

## Learning objectives

By the end of the workshop, participants can:

1. explain how Hedron's request/response model differs from Streamlit's execution model;
2. decide whether a Streamlit workflow is a good Hedron migration candidate;
3. turn Streamlit widgets and callbacks into explicit page, fragment, and action boundaries;
4. choose an owner for URL, request, session, durable, cached, and browser state;
5. run one `HedronPosit` app locally and through Posit Workbench's path prefix;
6. test full pages, input validation, HTMX fragments, and target rejection;
7. prepare and publish a FastAPI/ASGI bundle to Posit Connect without putting secrets in
   source control.

## Scope and expectations

Hedron is a server-rendered component framework on FastAPI. HTMX requests replace
declared HTML regions without a Node frontend or a full application-script rerun. It is a
strong fit for maintained CRUD tools, admin applications, forms, and dashboards that need
stable URLs, explicit write boundaries, FastAPI integration, and conventional tests.

Hedron is not a call-for-call Streamlit compatibility layer, an ORM, an identity provider,
or a hosted service. Streamlit remains a good choice when the notebook-style execution loop
is the primary benefit or the app depends on Streamlit-specific components with no suitable
replacement. Modern Streamlit also supports forms and fragments; the meaningful difference
is that a Hedron interaction is always an explicit HTTP request with a validated input and an
explicit response. See [Should you migrate?](streamlit-migration.md#should-you-migrate).

## Facilitator preparation

Complete this checklist several days before the session.

- Verify Python 3.11–3.14 and that participants can create and activate a project `venv`.
- If `python3.11` is unavailable, use the [Python 3.11 pyenv fallback](../getting-started/first-app-posit-workbench.md#python-311-fallback)
  before creating the virtual environment. When finished, return to [Facilitator preparation](#facilitator-preparation).
- Confirm that the environment can install `hedron>=0.67.0,<0.68` and optional packages
  from PyPI or your approved internal package index.
- On Workbench, verify that `RS_SERVER_URL` is present and `rserver-url` is executable.
- Run the complete workshop once from the same Workbench IDE participants will use.
- If using Connect, confirm the server is in the current Hedron Supported matrix, create a
  non-production publishing space, and pre-provision publisher access.
- Preconfigure a saved `rsconnect` server name such as `training-connect`, or document your
  organization's approved registration process. Never distribute an API key in the guide,
  source tree, chat, or slides.
- Decide how `HEDRON_SESSION_SECRET` will be set on Connect. Give each deployment a distinct
  value through Connect's environment settings or your organization's secret workflow.
- Confirm participants can open proxied web servers from Workbench and can view Connect
  deployment logs.
- Have pairs share one environment if package downloads, ports, or Connect publisher seats
  are constrained.

The Hedron Workbench launcher handles `root_path` discovery and path-scoped cookies. This
encapsulates the prefix handling described in Posit's
[Workbench proxy guidance](https://docs.posit.co/ide/server-pro/user/vs-code/guide/proxying-web-servers.html).
Do not ask participants to hard-code a Workbench `/s/.../p/...` URL; it changes with the
session.

## Participant prework

Send participants these commands before the workshop:

If a participant needs the Python fallback, send the [Python 3.11 pyenv fallback](../getting-started/first-app-posit-workbench.md#python-311-fallback)
with these commands. When finished, return to [Participant prework](#participant-prework).

```bash
python3.11 --version
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install "hedron>=0.67.0,<0.68"
hedron --version
```

Expected results:

- Python reports a version from 3.11 through 3.14;
- `hedron` prints its version without an import or network error;
- on Workbench, `test -n "$RS_SERVER_URL"` succeeds.

Ask participants to bring one small Streamlit workflow they may want to migrate. It should
contain no production data or secrets. They will use the supplied sales dashboard during the
lab and their own app only during the closing planning exercise.

## Agenda

| Time | Topic | Outcome |
|---:|---|---|
| 0:00–0:15 | Welcome and preflight | Everyone can install and run the CLI |
| 0:15–0:35 | Mental-model demonstration | Participants can name the page/fragment/action boundary |
| 0:35–1:00 | Lab 1: first app on Workbench | A scaffold runs through the correct Posit prefix |
| 1:00–1:45 | Lab 2: migrate a Streamlit dashboard | A reviewable Hedron candidate runs locally |
| 1:45–1:55 | Break | — |
| 1:55–2:25 | Lab 3: Posit facade and HTMX | The dashboard has an independently refreshed region |
| 2:25–2:50 | Lab 4: test the contracts | Page, validation, fragment, and rejection tests pass |
| 2:50–3:20 | Lab 5: prepare and publish | The app passes checks and is published or deploy-ready |
| 3:20–3:30 | Assessment and next steps | Each participant has a migration plan |

## The mental model to teach

Draw one browser, one route, and one response on a whiteboard. Add the Streamlit mapping
only after the HTTP flow is clear.

| Streamlit habit | Hedron design |
|---|---|
| A widget call returns its current value | A validated route parameter receives a query or form value |
| An interaction reruns code | A browser sends a GET or an unsafe-method request to one route |
| UI appears as the script executes | A route returns an explicit component tree |
| `if st.button(...)` performs a write | A CSRF-protected POST action authorizes and performs the write |
| `st.fragment` reruns part of the script | A fragment route returns HTML for an allowlisted page region |
| `st.session_state` owns mixed state | URL, request, session, database, cache, and browser state have distinct owners |
| `st.cache_resource` owns a shared client | FastAPI lifespan and dependency injection own long-lived resources |
| `streamlit run` starts the app | Uvicorn or `hedron-posit run` serves the ASGI application |

Use this request sequence during the demonstration:

```text
Browser GET /?region=North
  -> FastAPI validates region
  -> @app.page builds Python components
  -> Hedron renders a full HTML document

Browser HTMX GET /freshness, HX-Target: #freshness
  -> @app.view checks the declared region
  -> Hedron returns only replacement HTML
  -> HTMX swaps #freshness

Browser POST /orders/42/approve
  -> CSRF + authentication + authorization + validation
  -> @app.action performs the write
  -> response redirects with 303 or returns an allowed fragment
```

Emphasize one rule throughout the workshop: **safe GET routes render or read; writes belong
in explicit unsafe-method actions**.

## Lab 0 — Preflight the environment

**Time:** 15 minutes

Create a workshop directory and verify the target tools:

```bash
mkdir hedron-training
cd hedron-training
python3.11 --version
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install "hedron>=0.67.0,<0.68"
hedron --version
```

On Workbench, also run:

```bash
test -n "$RS_SERVER_URL"
command -v rserver-url || test -x /usr/lib/rstudio-server/bin/rserver-url
```

### Checkpoint

Do not continue until every participant has a supported Python version and can resolve the
Hedron package. Pair anyone blocked by package-index access with a working environment while
the facilitator records the infrastructure issue.

## Lab 1 — Run a first Hedron app on Posit Workbench

**Time:** 25 minutes

### 1. Scaffold the app

From `hedron-training/`:

```bash
hedron new hello-hedron
cd hello-hedron
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install -e . "hedron-posit>=0.67.0"
```

Add `"hedron-posit>=0.67.0",` to the `dependencies` list in `pyproject.toml` so a fresh
environment can reproduce the adapter installation.

Open `app.py`. Replace `Hedron` in the import and constructor with `HedronPosit`:

```python
from hedron import Page, RefreshButton, Stack, Text, html, swap
from hedron_posit import HedronPosit

app = HedronPosit(
    title="Hedron App",
    security="standard",
    explorer="off",
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET", "replace-in-production"
    ),
)
```

Keep the generated page, status region, and fragment below the constructor unchanged.
The fallback secret is acceptable only for this local lab; Lab 5 removes it.

### 2. Inspect the resolved Posit mode

```bash
hedron-posit check --discover --format json
```

Outside Posit, expect `product` to be `inactive`. In Workbench, expect `product` to be
`workbench` and a non-empty `browser_mount` discovered for this session.

### 3. Run it

```bash
hedron-posit run app:app --port 8000 --reload
```

Locally, open `http://127.0.0.1:8000`. In Workbench, open port 8000 from the Proxied
Servers view. Select **Refresh status** and confirm the timestamp changes without a full
page reload.

### Pair discussion

Find these four pieces in `app.py`:

1. the region declaration;
2. the full page route;
3. the control that names the target region;
4. the fragment route that returns the swap.

Explain to your partner why a made-up `HX-Target` should be rejected instead of updated.

### Checkpoint

The greeting renders, the status button works through the Workbench prefix, and the browser
network panel shows a small `/status` response rather than a full document.

Stop the server with Ctrl+C, then return to the workshop root:

```bash
cd ..
source .venv/bin/activate
```

Activating the workshop environment automatically switches from the app environment, so you do
not need to run `deactivate`.

## Lab 2 — Migrate a Streamlit dashboard

**Time:** 45 minutes

The migration assistant performs static analysis. It does not import or execute the
Streamlit app, does not modify the source, and does not claim behavioral equivalence. Its
output is a candidate for developer review.

### 1. Create the supplied Streamlit source

Create `streamlit-source/streamlit_app.py` in your editor:

```python title="streamlit-source/streamlit_app.py"
import pandas as pd
import streamlit as st


@st.cache_data
def load_sales() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"month": "Jan", "region": "North", "revenue": 3200, "orders": 32},
            {"month": "Feb", "region": "North", "revenue": 4100, "orders": 38},
            {"month": "Mar", "region": "North", "revenue": 4600, "orders": 41},
            {"month": "Jan", "region": "South", "revenue": 2800, "orders": 29},
            {"month": "Feb", "region": "South", "revenue": 3600, "orders": 34},
            {"month": "Mar", "region": "South", "revenue": 4300, "orders": 39},
        ]
    )


sales = load_sales()

st.title("Sales dashboard")
region = st.sidebar.selectbox("Region", ["All", "North", "South"])
minimum = st.sidebar.slider("Minimum revenue", 0, 5000, 0, step=500)

filtered = sales[
    ((sales["region"] == region) | (region == "All"))
    & (sales["revenue"] >= minimum)
]

revenue, orders = st.columns(2)
revenue.metric("Revenue", f"${filtered['revenue'].sum():,}")
orders.metric("Orders", int(filtered["orders"].sum()))

st.line_chart(filtered, x="month", y="revenue")
st.dataframe(filtered, width="stretch")
```

You do not need to install Streamlit or pandas for the analyzer.

### 2. Analyze before generating

From `hedron-training/`:

```bash
hedron migrate streamlit \
  streamlit-source/streamlit_app.py \
  --analyze-only \
  --format text
```

Review the dispositions for the title, select box, slider, metrics, chart, table, and cache.
Ask which mappings are direct components and which require an architectural decision.

### 3. Generate into a new directory

```bash
hedron migrate streamlit \
  streamlit-source/streamlit_app.py \
  --out sales-hedron
cd sales-hedron
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install -e .
```

The command refuses to overwrite a non-empty destination. Inspect these files before
running the app:

| File | Review question |
|---|---|
| `migration/REVIEW.md` | Which findings need a developer decision? |
| `migration/report.json` | What did the analyzer inventory? |
| `migration/source-map.json` | Which generated boundary came from each source call? |
| `app.py` | Where did widget values become validated route parameters? |
| `tests/test_migration_smoke.py` | Which generated behavior is already checked? |

### 4. Run and compare outcomes

```bash
uvicorn app:app --port 8000 --reload
```

Verify these outcomes:

- the default revenue is `$22,600` and the default order count is `213`;
- selecting North with a minimum of 4000 produces `$8,700` and 79 orders;
- the submitted filter is visible in the URL;
- `/?minimum=9000` receives a 422 validation response;
- the generated summary table is an intentional conservative replacement for the chart,
  not a promise of visual parity.

### Debrief

The important migration is not `st.selectbox` to `Select`. It is the move from an implicit
widget value to a validated, bookmarkable GET contract. The same principle applies to writes:
the target is an explicit POST action, not a translated button callback.

Use the [component matrix](streamlit-migration-matrix.md) for API lookup and
[execution and state](streamlit-execution-state.md) for architecture decisions.

## Lab 3 — Make the dashboard Posit-aware and add a fragment

**Time:** 30 minutes

### 1. Use the unified Posit facade

Stop the server. Add `"hedron-posit>=0.67.0",` to the `dependencies` list in
`pyproject.toml`, then install the updated project:

```bash
python3.11 -m pip install -e .
```

In `app.py`, replace the imported `Hedron` class and constructor:

```python
from hedron_posit import HedronPosit

# Keep the existing title, security, explorer, and session_secret arguments.
app = HedronPosit(
    title="Sales dashboard",
    security="standard",
    explorer="off",
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET", "local-migration-demo-only"
    ),
)
```

Remove `Hedron` from the `from hedron import (...)` block. `HedronPosit` defaults to product
auto-detection and native Connect cookie handling, so this same object behaves as ordinary
Hedron locally, discovers Workbench through the launcher, and recognizes Connect's protected
runtime marker when published.

### 2. Add an independently refreshed region

Add these imports:

```python
from datetime import UTC, datetime

from hedron import RefreshButton, Text, swap
```

After the `app = HedronPosit(...)` constructor, add:

```python
freshness = app.region("freshness", description="Dashboard refresh time")


def freshness_panel():
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"Dashboard checked at {stamp}"),
        id=freshness.id,
        role="status",
        aria={"live": "polite"},
    )
```

Inside the existing `content = Stack(...)`, place these two children after the main heading:

```python
freshness_panel(),
RefreshButton.for_region(
    freshness,
    href="/freshness",
    label="Refresh dashboard time",
),
```

After the page route, add:

```python
@app.view("/freshness", fragment_regions=(freshness,))
def refresh_freshness():
    return swap(freshness_panel())
```

### 3. Run through the Posit launcher

```bash
hedron-posit check --discover --format json
hedron-posit run app:app --port 8000 --reload
```

Open the app and refresh only the dashboard time. Confirm that filters still use a full GET
page request while the time control uses an HTMX fragment request. These are two deliberate
interaction choices in one application.

### Checkpoint

The application has exactly one `HedronPosit` object, no hard-coded Workbench mount, and one
fragment whose returned root element has `id="freshness"`.

## Lab 4 — Test the HTTP contracts

**Time:** 25 minutes

Stop the development server and add test dependencies:

```bash
python3.11 -m pip install "pytest>=8.3" "httpx>=0.28"
```

Replace the generated `tests/test_migration_smoke.py` with the following focused suite. The
module-scoped client starts the application's plugin lifecycle once and shares it across these
read-only requests:

```python title="tests/test_migration_smoke.py"
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


def test_default_totals(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "$22,600" in response.text
    assert ">213<" in response.text


def test_typed_filter_and_validation(client: TestClient) -> None:
    filtered = client.get("/?region=North&minimum=4000")
    invalid = client.get("/?minimum=9000")

    assert filtered.status_code == 200
    assert "$8,700" in filtered.text
    assert invalid.status_code == 422


def test_declared_fragment(client: TestClient) -> None:
    response = client.get(
        "/freshness",
        headers={"HX-Request": "true", "HX-Target": "#freshness"},
    )

    assert response.status_code == 200
    assert "Dashboard checked at" in response.text
    assert "<html" not in response.text


def test_fragment_rejects_unknown_target(client: TestClient) -> None:
    response = client.get(
        "/freshness",
        headers={"HX-Request": "true", "HX-Target": "#other-panel"},
    )

    assert response.status_code == 403
```

Run the workshop tests:

```bash
python3.11 -m pytest
```

### Extension for fast pairs

Add a test proving that `/?region=East` receives 422. Then write down how you would test a
state-changing action: start with a safe GET to seed CSRF state, submit the form, assert the
write once, and assert a 303 redirect or allowed fragment response.

### Checkpoint

The suite proves a user outcome, invalid-input rejection, a successful partial response, and
fail-closed target authorization. It does not assert the entire generated HTML document.

## Lab 5 — Prepare and publish to Posit Connect

**Time:** 30 minutes

This lab assumes a facilitator-provided Connect server registration and a non-production
publishing destination. The `rsconnect` command is Posit's publishing tool; Connect server
administration, publisher access, and publishing automation are outside Hedron's support
boundary. Refer to Posit's current [FastAPI publishing guide](https://docs.posit.co/connect/user/fastapi/)
and [CLI guide](https://docs.posit.co/connect/user/publishing-cli/) for your server.

### 1. Remove the development secret fallback

Change the constructor to require the deployment environment value:

```python
app = HedronPosit(
    title="Sales dashboard",
    security="standard",
    explorer="off",
    session_secret=os.environ["HEDRON_SESSION_SECRET"],
)
```

Set `HEDRON_SESSION_SECRET` in the Connect content environment, never in `app.py`,
`requirements.txt`, or an `.env` file committed to Git. Connect documents secret environment
handling in its [content settings guide](https://docs.posit.co/connect/user/content-settings/).

For this disposable training deployment, create a temporary value in the current shell. The
deployment command below passes the variable by name so its value does not appear in the
command line:

```bash
export HEDRON_SESSION_SECRET="$(python3.11 -c 'import secrets; print(secrets.token_urlsafe(32))')"
```

Use your organization's secret manager for real applications. A production session secret
must remain stable across normal redeployments and all workers, with a planned rotation
procedure.

### 2. Build and diagnose

```bash
hedron --app app:app check
hedron build
hedron-posit doctor app:app --live --format json
```

Confirm `.hedron/build/manifest.json` exists. If your organization enables
`HEDRON_ENV=production` on Connect, the build manifest must be present in the deployed bundle
or startup fails closed.

### 3. Export reproducible dependencies

Build the deployment requirements in a clean environment outside the application directory. This
keeps editable project paths and workshop-only test packages out of the Connect bundle:

```bash
python3.11 -m venv ../sales-hedron-deploy-venv
../sales-hedron-deploy-venv/bin/python3.11 -m pip install --upgrade pip
../sales-hedron-deploy-venv/bin/python3.11 -m pip install -e .
../sales-hedron-deploy-venv/bin/python3.11 -m pip freeze --exclude-editable > requirements.txt
```

Inspect the file and confirm it contains the Hedron, data, Posit, FastAPI, and Uvicorn
dependencies needed by `app.py`, with no local `-e` path. The deployment environment is a sibling
of the application directory and therefore is not part of the bundle. Do not move it into the app.
When targeting the minimum supported Connect 2025.06 lane, follow the
[Posit deployment guide](posit.md#native-connect) for its additional setuptools constraint.

Posit Connect uses `requirements.txt` when it is present to reconstruct the Python
environment. The server also needs a compatible Python version.

### 4. Publish

Assuming the facilitator registered a server named `training-connect`:

```bash
rsconnect deploy fastapi \
  -n training-connect \
  --entrypoint app:app \
  --environment HEDRON_SESSION_SECRET \
  --environment HEDRON_ENV=production \
  .
```

After the deployment completes, remove the disposable local value with
`unset HEDRON_SESSION_SECRET`. Connect retains the environment setting for the content item.

If your organization uses Git-backed publishing, a manifest workflow, a private package
index, or an approval pipeline, substitute that approved process. The important Hedron
contract is that Connect imports `app:app` as an ASGI application and includes the built
assets and dependencies.

### 5. Smoke-test the published app

Through the final Connect URL, verify:

- the default page and a filtered, bookmarkable URL;
- the freshness fragment and its static assets under the Connect content prefix;
- one invalid query producing validation rather than an unhandled error;
- no doubled content prefix in links, forms, redirects, or HTMX requests;
- the content environment contains the secret while logs and source do not;
- Connect's access settings match the intended audience.

`POSIT_PRODUCT=CONNECT` is supplied by Connect and causes `HedronPosit` to select Connect
mode. Connect credentials or user-session headers are not Hedron authentication and must not
be treated as application authorization.

### Checkpoint

The content starts successfully, all browser requests stay beneath the Connect content URL,
and no application secret appears in the deployment source or logs.

## Assessment

Use this ten-point exit check. A participant is ready to migrate a small read-only workflow
independently at **8/10**, provided they earn both security points.

| Point | Evidence |
|---:|---|
| 1 | Explains page versus fragment responses |
| 1 | Maps a safe filter to a validated GET parameter |
| 1 | Maps a write to a POST action rather than a GET/render side effect |
| 1 | Assigns a former Session State key to a deliberate owner |
| 1 | Runs the app through `hedron-posit` without a hard-coded Workbench prefix |
| 1 | Explains why an unknown HTMX target returns 403 |
| 1 | Writes a user-outcome HTTP test |
| 1 | Preserves a bounded Hedron version pin and deployment dependency list |
| 1 | Keeps CSRF enabled and puts writes behind authorization and validation |
| 1 | Keeps session and service secrets outside source control |

Finish with a two-minute teach-back: each participant chooses one real Streamlit screen and
states its route, state owners, first acceptance test, and largest migration risk.

## Migration planning worksheet

Copy one row for each workflow in the participant's real app:

| Current behavior | Hedron boundary | HTTP method | State owner | Dependency/extra | Acceptance proof | Risk/owner |
|---|---|---|---|---|---|---|
| Region filter | Page query parameter | GET | URL | `hedron[data]` | Same totals for fixture | Low / team |
| Approve order button | `@app.action` | POST | Database | application service | Authorized write once | High / service owner |
| Export progress | Job status fragment | GET polling | Shared job backend | chosen queue | Survives worker change | Medium / platform |

Require teams to migrate one workflow at a time. Keep the Streamlit and Hedron entrypoints as
separate processes over shared framework-free domain functions until acceptance and rollback
are proven. Follow the [production cutover checklist](streamlit-cutover.md) before moving
traffic.

## Troubleshooting during the workshop

| Symptom | Likely cause | Action |
|---|---|---|
| `hedron` is not found | CLI is not installed on PATH | From the current project directory, activate `.venv`, then run `python3.11 -m pip install -e .` |
| `ModuleNotFoundError: hedron_posit` | Posit adapter was not installed | Run `python3.11 -m pip install "hedron-posit>=0.67.0"` and add it to `pyproject.toml` |
| Workbench page loads without styles or links break | App was started without prefix discovery | Use `hedron-posit run`; do not hard-code the session URL |
| `rserver-url` diagnostic fails | Workbench binary/path or session environment is unavailable | Confirm `RS_SERVER_URL`, the binary path, and platform configuration with the administrator |
| Port 8000 is busy | A previous server is still running | Stop it or choose another port |
| Fragment returns 403 | `HX-Target` differs from the route's declared region | Compare the region id, selector, control, and decorator |
| Query returns 422 | Query validation rejected the value | Correct the control or bounds; keep server-side validation |
| POST returns 403 | CSRF cookie/token pair is missing or mismatched | Start from a safe page GET and use `CsrfField`; do not disable CSRF |
| Migrator refuses output | Destination is non-empty | Choose a fresh directory; the refusal protects existing work |
| Connect cannot import `app:app` | Entrypoint, dependencies, or Python version differ | Check the bundle, requirements, server Python, and deployment logs |
| Connect production startup reports `HED-BUILD-0003` | Build manifest is absent | Run `hedron build` and include `.hedron/build/manifest.json` |
| Reload with multiple workers fails | Development reload and worker supervision conflict | Use reload for development or multiple workers for serving, not both |

## Facilitator answer key

Listen for these conclusions during the debrief:

- The filter form uses GET because it is safe and the URL is valuable state.
- FastAPI rejects out-of-range input before the dashboard function performs work.
- `HedronPosit` changes deployment handling, not the component or route programming model.
- A fragment is a separate HTTP endpoint with an allowed target, not a mutable placeholder.
- A 403 for the wrong target is expected security behavior.
- The migration report is an inventory and scaffold; the developer remains responsible for
  state, writes, authorization, caches, custom components, and acceptance equivalence.
- Workbench URLs are session-scoped; durable shared links belong on Connect or another stable
  external base URL.
- A public cache is valid only for truly public data. User- or tenant-dependent results need
  explicit dimensions and the correct scope.
- Connect access control does not remove the application's responsibility for authorization at
  mutation and data boundaries.

## After the workshop

Within one week, hold a 45-minute migration clinic. Ask each team to bring its completed
worksheet and one extracted framework-free function with fixed test data. Select a read-only
workflow first, compare outcomes in Streamlit and Hedron side by side, and add writes only
after the GET and testing boundaries are understood.

Continue with:

- [Streamlit migration walkthrough](streamlit-migration.md)
- [Streamlit execution and state](streamlit-execution-state.md)
- [Forms and actions](forms-and-actions.md)
- [Test your UI](testing.md)
- [Posit deployments](posit.md)
- [Ship a Hedron app](ship.md)
