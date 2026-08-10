# Move a Streamlit app to Hedron production

This checklist covers the operational part of migration: running both applications,
validating equivalent workflows, moving secrets and dependencies, deploying the ASGI app,
and retaining a rollback path.

If you are still translating UI code, begin with
[Migrate a Streamlit app](streamlit-migration.md). If state ownership is unclear, resolve
that first in [Execution and state](streamlit-execution-state.md).

## The deployment model changes

Streamlit Community Cloud is a managed product that understands a Streamlit entrypoint,
dependency files, and `secrets.toml`. Hedron produces a portable FastAPI/ASGI application;
you run it on an ASGI-capable platform or in a container.

Official Streamlit references:
[Community Cloud deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app) ·
[dependencies](https://docs.streamlit.io/deploy/concepts/dependencies) ·
[secrets](https://docs.streamlit.io/deploy/concepts/secrets).

| Streamlit deployment | Hedron deployment |
|---|---|
| `streamlit run streamlit_app.py` | `uvicorn app:app` |
| Entrypoint script | Importable ASGI object, normally `app:app` |
| `requirements.txt` or supported environment file | `pyproject.toml`/lockfile or pinned requirements |
| `.streamlit/secrets.toml` / Cloud secrets UI | Environment variables or platform secret manager |
| Streamlit server configuration | Uvicorn/ASGI process and proxy configuration |
| Community Cloud health/runtime management | Your platform's health checks, workers, TLS, and logs |
| Streamlit static/runtime assets | Hedron build manifest plus `/hedron-static/` and `/hedron-assets/` |

Hedron does not include a managed hosting service. Confirm where the ASGI process will run
before scheduling a cutover.

## 1. Inventory the existing app

Record these before editing deployment files:

- Streamlit entrypoints and multipage files;
- Python and system dependencies;
- `st.secrets` keys and `st.connection` resources—names only, never secret values;
- authentication and viewer-access rules;
- `st.session_state` keys and their intended lifetimes;
- `st.cache_data` / `st.cache_resource` functions and invalidation assumptions;
- local files, uploads, downloads, and generated artifacts;
- scheduled work, background threads, fragments, and timers;
- custom/community components and their browser assets;
- current URLs, bookmarks, embeds, and external links;
- the five to ten user workflows that must survive the migration.

Classify each dependency as **carry over**, **replace**, or **remove**. The
[component matrix](streamlit-migration-matrix.md) helps with UI APIs; the migration should
also account for operational features that are not components.

## 2. Preserve behavior with tests

Before replacing the app, use Streamlit's
[AppTest](https://docs.streamlit.io/develop/concepts/app-testing) for critical current
behavior. Capture representative input fixtures and expected domain outputs outside the UI.

Build the Hedron suite in layers:

1. ordinary unit tests for extracted data and business functions;
2. `TestClient` tests for pages, typed query validation, actions, redirects, and fragments;
3. `AppScenario` tests for cookie-retaining multi-step workflows;
4. a small browser suite for JavaScript swaps, focus, uploads, and accessibility;
5. smoke tests against the deployed proxy, not only localhost.

Do not require byte-for-byte HTML or pixel identity. Require equivalent data, decisions,
permissions, navigation, and accessible user outcomes.

## 3. Move configuration and secrets

Replace `st.secrets` access with explicit settings loaded from environment variables or
your platform's secret manager. Never copy `.streamlit/secrets.toml` into an image or commit
it to source control.

```python title="app.py"
import os

from hedron import Hedron

app = Hedron(
    title="Sales dashboard",
    security="standard",
    explorer="off",
    session_secret=os.environ["HEDRON_SESSION_SECRET"],
)

database_url = os.environ["DATABASE_URL"]
```

`HEDRON_SESSION_SECRET` is an adopter convention: Hedron does not read it automatically.
Your application must pass the value into `Hedron(...)`. Use distinct secrets per
environment and document rotation.

## 4. Pin and simplify dependencies

Start with a clean environment and remove Streamlit only after the Hedron app no longer
imports it.

```bash
uv add "hedron[data]>=0.26.0,<0.27" "uvicorn[standard]"
uv remove streamlit
uv lock
```

If the two apps temporarily share a repository, keep separate dependency groups or
deployable directories so removing Streamlit from the Hedron environment cannot break the
fallback. Preserve explicit pandas, NumPy, plotting, database, and model dependencies even
if Streamlit previously installed some transitively.

!!! note "Hedron 0.26 chart floor"

    Install `hedron[charts]>=0.26.0,<0.27`; this requires the compatible
    `hedron-charts>=0.1.6,<0.2` satellite. See
    [Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

## 5. Build the production artifact

Development discovers assets dynamically. Production requires a sealed build manifest:

```bash
hedron build
HEDRON_ENV=production \
  uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

The runtime image must contain the generated `manifest.json`. Production startup fails
closed when it is absent. Keep `/hedron-static/` and `/hedron-assets/` reachable through
the proxy.

Use the maintained guidance in [Ship a Hedron app](ship.md) and the Docker/proxy details
in [Deployment](deployment.md); do not invent a deployment from this short mapping alone.

## 6. Revisit state for multiple workers

A Streamlit app may have relied on one process's memory, session connection, cached
singleton, or background thread. A production ASGI deployment may run multiple workers.

Before adding workers, verify:

- durable records live in a database;
- job state uses a shared backend when workers must see the same job;
- session policy is compatible with the chosen worker/process model;
- cache keys include tenant/user dimensions and the backend matches sharing requirements;
- uploads and generated files use durable/shared storage when another worker must read them;
- no module-level mutable collection is acting as a database;
- long-running work does not block a request worker.

Prefer polling for job status. Hedron's FastAPI SSE/WebSocket helpers are experimental and
require your own proxy, reconnect, and backpressure proof.

## 7. Run side by side

Use a staged URL or route during acceptance:

```text
app.example.com          → current Streamlit app
next.app.example.com     → Hedron candidate
```

Exercise identical fixtures and user roles. Compare:

- default results and filtered results;
- create/update/delete behavior and duplicate-submit handling;
- authentication, authorization, and session expiry;
- empty, loading, validation, permission-denied, and server-error states;
- bookmarks, back/forward navigation, downloads, and refresh behavior;
- keyboard access, screen-reader labels, focus after updates, and reduced motion;
- response time, query volume, cache hit/miss behavior, and memory;
- logs, health checks, readiness, and alert routing.

Do not send real writes to both production systems unless the data architecture explicitly
supports dual writes and reconciliation. A read-only shadow is safer.

## 8. Plan URL and data cutover

For each old page, choose one outcome:

- preserve the same public path at the proxy;
- redirect permanently to a new stable path;
- keep a temporary compatibility landing page;
- retire it with an owner-approved message and date.

Back up data before any schema change. Use reversible schema migrations where possible.
If Streamlit Session State held important user work, decide whether it must be persisted
before cutover; session memory cannot be assumed to transfer between runtimes.

## 9. Define rollback before launch

Write down:

- the rollback trigger and decision owner;
- how traffic returns to Streamlit;
- whether database writes made by Hedron remain backward-compatible;
- how long the Streamlit deployment and environment will be retained;
- which logs and metrics determine success;
- how users report migration-specific problems.

A rollback is credible only if it has been rehearsed against the production routing and
data shape.

## Go-live checklist

- [ ] Critical workflows pass in both applications with the same fixtures.
- [ ] Every former `st.session_state` key has an explicit owner.
- [ ] Every former cache/resource has reviewed scope, lifetime, and concurrency behavior.
- [ ] Writes use unsafe HTTP methods with authorization, validation, and CSRF.
- [ ] Secrets are supplied outside source control and default development secrets are gone.
- [ ] The production build manifest is present and startup succeeds with `HEDRON_ENV=production`.
- [ ] Static assets and one representative HTMX fragment work through the real proxy.
- [ ] Health/readiness checks and logs are connected to operations.
- [ ] Accessibility and empty/error states have been exercised.
- [ ] URLs and redirects are documented.
- [ ] Backup, cutover, and rollback have named owners.
- [ ] The Streamlit fallback has a time-bounded retirement plan.

## Next

[Ship checklist](ship.md) · [Deployment deep dive](deployment.md) ·
[Security](security.md) · [Observability](observability.md) ·
[Streamlit migration home](streamlit-migration.md)
