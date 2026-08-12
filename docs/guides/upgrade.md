# Upgrade to Hedron 0.29

This guide covers an application upgrade from **0.28.x** to the **0.30.x** train
(current tip **`v0.30.0`**). New applications should use
[Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.30.x ships production-grade `hedron-workbench` (D-057 / RFC-0062): an
optional Posit Workbench / RStudio Server adapter. Existing FastAPI Hedron apps
run unchanged by switching the launch command. Cookie `Path` is still
construction-time (`HEDRON_ROOT_PATH` or `Hedron(root_path=...)`).
New applications can import `HedronWorkbench` in place of `Hedron`; the subclass
retains ordinary Hedron behavior outside Workbench.

No Supported CRUD/admin API removal is listed. Polling remains the production
recommendation for live status. SSE, WebSocket, streaming, and navigation preload
remain experimental. Flask/Django adapters are untouched.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on `hedron>=0.28.2,<0.29` (or an earlier 0.28-compatible pin).
3. If you deploy on Posit Workbench, plan to install `hedron[workbench]` and
   switch the session launch command. Application source does not need to import
   `hedron_workbench`.

Alternatively, change only the app class for an explicit Workbench-aware source
surface:

```python
from hedron_workbench import HedronWorkbench

app = HedronWorkbench(...)
```

## Install

```bash
python -m pip install -U "hedron>=0.30.0,<0.31"
# Optional Workbench adapter:
python -m pip install -U "hedron-workbench>=0.30.0,<0.31"
```

Local development is unchanged:

```bash
uvicorn app:app --reload
```

Workbench / RStudio Server:

```bash
hedron-workbench run app:app
```

Uninstalling `hedron-workbench` restores the 0.28 launch command.

## Cookie Path / reverse proxies

`Hedron(root_path=...)` now wins over `HEDRON_ROOT_PATH`. Uvicorn `--root-path`
alone still does **not** scope session/CSRF cookies. Export `HEDRON_ROOT_PATH`
before constructing the app, or pass `root_path=` to `Hedron()`.

## Rollback

Pin `hedron>=0.28.2,<0.29` and remove `hedron-workbench`. Application source that
never imported the adapter needs no code rollback.
