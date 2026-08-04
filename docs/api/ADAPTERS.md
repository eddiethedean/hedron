---
status: implemented
---

# Framework adapter contracts


!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Package maturity (Beta/Alpha) is separate from API level
    (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Beta Supported adapters shipped (`hedron-flask`, `hedron-django`).
Portable contracts live in `hedron-core`.

## Install

```bash
pip install hedron-flask
pip install hedron-django   # Django >=5.2,<6
```

Quickstarts: [Flask](../getting-started/flask.md) · [Django](../getting-started/django.md).

## Portable baseline

Hedron's portable adapter surface represents only semantics that can exist without a raw
framework request or response:

- normalized HTMX request facts and page/fragment/history mode;
- interaction content, status, OOB updates, approved headers, history, and cache policy;
- reverse-URL requests resolved by the host router;
- static/build-manifest asset references;
- authenticated/session-scope signals without session contents;
- lifecycle resource descriptions and sanitized diagnostics; and
- declared capability metadata.

Concrete adapters translate these values to native FastAPI, Flask, or Django objects.
Core contracts never retain a raw request, response, session, dependency, database handle,
or application object.

Every approved HTMX header is revalidated at the adapter boundary; arbitrary header
mappings cannot bypass redirect, selector, cache, or security policy.

## FastAPI (flagship)

| Surface | Role |
|---|---|
| `Hedron` / `HedronRouter` | Application + route registration |
| `interaction_headers` / `InteractionResult` | Typed HTMX responses |
| CSRF cookie + `X-CSRF-Token` | Double-submit on unsafe methods |

## Flask (`hedron_flask`)

| Symbol | Role |
|---|---|
| `HedronFlask` | Thin wrapper; `respond`, `csrf_token`, optional auto CSRF cookie |
| `hedron_route` | Register views returning components / `InteractionResult` (CSRF on unsafe methods) |
| `interaction_response` / `component_response` | Build Flask `Response` values |
| `FlaskUrlReverser` | Path-only `url_for` with `root_path` / `script_name` |

**Raises / status:** CSRF failure → HTTP 403. Unauthorized OOB / fragment region → 403 body.

## Django (`hedron_django`)

| Symbol | Role |
|---|---|
| `HedronDjango` | `respond`, `csrf_token`, auth signal helpers |
| `hedron_view` | Wrap sync/async views; seeds CSRF cookie on safe GETs |
| `interaction_response` / `component_response` | Build `HttpResponse` values |
| `DjangoUrlReverser` | `reverse` with mount prefixes |

**Settings:** Prefer `CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"` for portable `X-CSRF-Token`.
Django floor: `>=5.2,<6`.

## Deferred (not Supported)

| Claim | Notes |
|---|---|
| Official HTMX SSE live transport | Use bounded polling for jobs |
| Django QuerySet DataSource | Bridge QuerySets in app code |
| Hedron-owned Django forms subsystem | Apps may use Django-native forms |

## Capability matrix

Machine-readable records: `hedron_core.adapter.capability_matrix()` /
[COMPATIBILITY](../COMPATIBILITY.md) / [acceptance/ADAPTERS](../acceptance/ADAPTERS.md).
