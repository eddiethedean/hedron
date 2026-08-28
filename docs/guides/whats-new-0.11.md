# What's new in 0.11

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and 1.0 candidate status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

Published coordinated train **`0.11.0`** (`v0.11.0`, 2026-08-04). Deepens Flask/Django
integration and closes the QuerySet / forms deferrals from D-036 via **D-046**. Full detail:
[What's ready](whats-ready.md) · [Upgrade](upgrade.md) · [Adapters](../api/ADAPTERS.md).

## Highlights

- Flask **`init_app`** / **`HedronBlueprint`** application-factory patterns beside the
  constructor helper
- Django **`HedronDjangoConfig`**, system checks, and first-party **forms bridge**
- Bounded **`DjangoQuerySetDataSource`** (deny-by-default allowlists; app-owned base QS)
- Portable **`hedron.testing.adapters`** harness (FastAPI / Flask / Django PAGE+FRAGMENT)
- HDJ dynamic dependency manifests, foreign namespaces, and **CSP fail-closed** inventory
- Celery / RQ **`JobBackend`** bridges; capability-labeled Flask/Django live helpers
- Explorer `/inventory` and `hedron check` HDJ inventory summaries

## Still Deferred / honest gaps

- Full multi-engine adapter live browser matrix → owned `0.11.x` (`LIVE-011-BROWSER`)
- Capture UI → **0.15**
- FastAPI live browser matrix / load-proxy evidence → owned `0.10.x` rows

## Upgrade path

1. Pin packages to **`0.11.0`**.
2. Prefer `HedronFlask().init_app(app)` + `HedronBlueprint` for factories; constructor
   remains supported.
3. Install `hedron_django.apps.HedronDjangoConfig`; use `form_to_nodes` /
   `DjangoQuerySetDataSource` instead of ad-hoc bridges.
4. Never pass an unauthorized base QuerySet; omit allowlists means deny client refinements.

Install: `pip install -U "hedron>=0.11.0"` (or `uv add "hedron>=0.11.0"`).
