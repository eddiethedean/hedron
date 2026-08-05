---
status: implemented
---

# Framework adapter contracts


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Package maturity (Beta/Alpha) is separate from API level
    (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Beta Supported adapters shipped (`hedron-flask`, `hedron-django`).
Portable contracts live in `hedron-core`. Flask `init_app` / `HedronBlueprint` and
Django forms + QuerySet DataSource are Supported (D-046; current train **0.13.0**).

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
| `HedronFlask` | Constructor or `init_app(app)` factory; `respond`, CSRF cookie |
| `HedronBlueprint` | Blueprint with `page` / `component` / `action` / `include_component` |
| `hedron_route` | Register views returning components / `InteractionResult` (CSRF on unsafe methods) |
| `wrap_hedron_view` | Public CSRF + InteractionResult conversion wrapper |
| `interaction_response` / `component_response` | Build Flask `Response` values |
| `FlaskUrlReverser` | Path-only `url_for` with `root_path` / `script_name` |

**Raises / status:** CSRF failure → HTTP 403. Unauthorized OOB / fragment region → 403 body.

## Django (`hedron_django`)

| Symbol | Role |
|---|---|
| `HedronDjango` | `respond`, `csrf_token`, auth signal helpers |
| `HedronDjangoConfig` | Installable AppConfig + `hedron.*` system checks |
| `hedron_view` | Wrap sync/async views; seeds CSRF cookie on safe GETs |
| `form_to_nodes` / `validation_interaction` | Django Form / ModelForm / formset bridge |
| `DjangoQuerySetDataSource` (`hedron-data`) | Bounded QuerySet source (deny-by-default allowlists) |
| `interaction_response` / `component_response` | Build `HttpResponse` values |
| `DjangoUrlReverser` | `reverse` with mount prefixes |

**Settings:** Prefer `CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"` for portable `X-CSRF-Token`.
Django floor: `>=5.2,<6`.

## Live transport (FastAPI vs adapters)

Official HTMX SSE, focused streaming, and page/session WebSocket channels are **experimental**
(`hedron.experimental`) on the FastAPI flagship until Deferred ops gates close (see
[live interaction](../guides/live-interaction.md) and [STABILITY](STABILITY.md)). Flask and
Django adapters keep **bounded polling** as the Supported live-status fallback; they do not
ship the FastAPI SSE/WebSocket helpers.

## Errors

| Situation | Host | Behavior |
|---|---|---|
| CSRF missing/invalid on unsafe method | Flask `hedron_route` / `respond` | HTTP 403 |
| CSRF missing/invalid | Django (middleware + portable header) | HTTP 403 (Django CSRF) |
| Unauthorized fragment / OOB region | Flask / Django | HTTP 403 body |
| Invalid approved HTMX header values | All adapters | Rejected at adapter boundary |
| FastAPI SSE helpers imported on Flask/Django | N/A | Not shipped — use polling |

## Deferred (not Supported)

| Claim | Notes |
|---|---|
| Capture UI (camera/mic) | Assigned to 0.15 (D-045) |
| Full adapter live browser matrix | Owned Deferred `LIVE-011-BROWSER` → 0.11.x |

## Capability matrix

Machine-readable records: `hedron_core.adapter.capability_matrix()` /
[COMPATIBILITY](../COMPATIBILITY.md) / [acceptance/ADAPTERS](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/ADAPTERS.md).
