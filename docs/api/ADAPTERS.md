---
status: implemented
---

# Framework adapter contracts


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Package maturity (Beta/Alpha) is separate from API level
    (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Adapters shipped (`hedron-flask`, `hedron-django`). Capability readiness:
**Supported** for Blueprint/`init_app`, AppConfig, forms bridge, and bounded QuerySet
DataSource. Package maturity remains **Beta** on PyPI — pin versions.
Portable contracts live in `hedron-core`. Living train: **0.36.x** (last published **v0.36.0**).

Autodoc signatures: [Autodoc — Framework adapters](AUTODOC.md#framework-adapters). Quickstarts:
[Flask](../getting-started/flask.md) · [Django](../getting-started/django.md).

## Install

```bash
pip install "hedron-flask>=0.36.0,<0.37"
pip install "hedron-django>=0.36.0,<0.37"   # Django >=5.2,<6
```

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

Full constructor contract: [Hedron](HEDRON.md).

## Flask (`hedron_flask.HedronFlask`)

Construct with an `import_name` to own a Flask app, or construct without an app and call
`init_app` for application-factory composition.

```python
from flask import Flask
from hedron_flask import HedronFlask
from hedron_core import Page, Text

hf = HedronFlask()
app = Flask(__name__)
hf.init_app(app, security="standard")


@hf.page("/")
def home():
    return Page(Text("Hello"), title="Home")
```

### Constructor

| Parameter | Type | Default | Description |
|---|---|---|---|
| `import_name` | `str \| None` | `None` | When set, creates `Flask(import_name, **kwargs)` and calls `init_app` |
| `csrf_cookie_name` | `str` | `"hedron_csrf"` | CSRF cookie name |
| `auto_csrf_cookie` | `bool` | `True` | Seed CSRF cookie on safe responses |
| `csrf_protect` | `bool` | `True` | Validate CSRF on unsafe methods in `respond` / wrapped views |
| `csrf_cookie_secure` | `bool \| None` | `None` | `True` always Secure; `None` follows request/`FLASK_ENV`; `False` never |
| `security` | profile name \| `SecurityPolicy` | `"standard"` | Portable security profile |
| `**kwargs` | — | — | Passed to `Flask(...)` when `import_name` is set |

### Methods

| Method | Returns | Description |
|---|---|---|
| `init_app(app, *, security=None)` | `Flask` | Bind extension (idempotent for the same app) |
| `page(rule, **options)` | decorator | Register a page view; supports `fragment_regions`, `methods` |
| `respond(value, request, *, context=None, mode=None, extra_headers=None, fragment_regions=None, allow_undeclared_targets=False)` | Flask `Response` | Render `NodeLike` / `InteractionResult`; CSRF on unsafe methods when enabled |
| `auth_signal(request=None)` | `AuthSignal` | Flask-Login / session-derived auth signal (no session body to core) |
| `csrf_token(request)` | `str` | Current CSRF token for forms / headers |
| `attach_csrf_cookie(response, request, token=None)` | `str` | Set CSRF cookie on a response |

Also: `HedronBlueprint`, `hedron_route`, `wrap_hedron_view`, `interaction_response`,
`component_response`, `FlaskUrlReverser` — see role table below and Autodoc.

| Symbol | Role |
|---|---|
| `HedronBlueprint` | Blueprint with `page` / `component` / `action` / `include_component` |
| `hedron_route` | Register views returning components / `InteractionResult` (CSRF on unsafe methods) |
| `wrap_hedron_view` | Public CSRF + InteractionResult conversion wrapper |
| `interaction_response` / `component_response` | Build Flask `Response` values |
| `FlaskUrlReverser` | Path-only `url_for` with `root_path` / `script_name` |

**Raises / status:** CSRF failure → HTTP 403. Unauthorized OOB / fragment region → 403 body.
Calling `page` / `route` before `init_app` → `RuntimeError`.

## Django (`hedron_django.HedronDjango`)

Thin helper for native Django views. Install AppConfig for system checks; wrap views with
`hedron_view` or call `respond` from your own views.

```python
from hedron_django import HedronDjango
from hedron_core import Page, Text

hd = HedronDjango()


def home(request):
    return hd.respond(Page(Text("Hello"), title="Home"), request)
```

### Constructor

| Parameter | Type | Default | Description |
|---|---|---|---|
| *(none)* | — | — | `HedronDjango()` takes no constructor args; create one helper per process |

### Methods

| Method | Returns | Description |
|---|---|---|
| `render(value, request, *, context=None, mode=None)` | `str` | HTML body only |
| `respond(value, request, *, context=None, mode=None, extra_headers=None, fragment_regions=None, allow_undeclared_targets=False)` | `HttpResponse` | Render component or `InteractionResult`; seeds CSRF cookie on safe GETs |
| `auth_signal(request)` | `AuthSignal` | Django `request.user` / session tenant signal |
| `csrf_token(request)` | `str` | Portable CSRF token for `X-CSRF-Token` |

| Symbol | Role |
|---|---|
| `HedronDjangoConfig` | Installable AppConfig + `hedron.*` system checks |
| `hedron_view` | Wrap sync/async views; seeds CSRF cookie on safe GETs |
| `interaction_response` / `component_response` | Build `HttpResponse` values |
| `DjangoUrlReverser` | `reverse` with mount prefixes |

**Settings:** Prefer `CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"` for portable `X-CSRF-Token`.
Django floor: `>=5.2,<6`.

### Django forms bridge (`hedron_django.forms`)

| Function | Returns | Description |
|---|---|---|
| `form_to_nodes(form, *, request=None, include_csrf=True)` | `list[NodeLike]` | Optional CSRF hidden input, non-field errors, then field nodes |
| `formset_to_nodes(formset, *, request=None, include_csrf=True)` | `list[NodeLike]` | Management form + each form’s fields |
| `validation_interaction(form, *, request=None, explanation=...)` | `InteractionResult` | Invalid-form fragment for HTMX / non-HTMX parity |

CSRF: pass `request` when `include_csrf=True` so the portable hidden field is included.
Prefer Django’s CSRF middleware + portable `X-CSRF-Token` header for unsafe methods.

### `DjangoQuerySetDataSource` (`hedron_data`)

Bounded QuerySet `DataEditorSource`. **Deny-by-default:** omitted sort/filter allowlists
mean no client refinements. The constructor never calls `.objects.all()` — you supply an
already authorized/tenant-scoped QuerySet.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `base_queryset` | QuerySet | required | Application-scoped queryset (must be a `*QuerySet`) |
| `key_field` | `str` | `"pk"` | Row key field |
| `schema` | sequence of `ColumnSchema` | `()` | Column catalog |
| `allowlisted_sort_fields` | `frozenset[str] \| None` | `None` → empty | Client sort allowlist |
| `allowlisted_filter_fields` | `frozenset[str] \| None` | `None` → empty | Client filter allowlist |
| `search_fields` | sequence of `str` | `()` | Search fields |
| `max_page_size` | `int` | `100` | Page size ceiling |
| `query_budget` | `int` | `25` | Max ORM queries per fetch (`QueryBudgetExceeded`) |
| `row_mapper` | callable \| `None` | `None` | Map model → JSON row |
| `apply_changes` | callable \| `None` | `None` | Persist editor changes |
| `transaction_owner` | `str` | `"application"` | Who owns DB transactions |

**Raises:** `TypeError` if `base_queryset` is not a QuerySet; `QueryBudgetExceeded` when
the fetch exceeds `query_budget`.

## Live transport (FastAPI vs adapters)

Official HTMX SSE, focused streaming, and page/session WebSocket channels are **experimental**
(`hedron.experimental`) on the FastAPI flagship under Accepted 0.24 **`polling_only`** (see
[LIVE_DISPOSITION](LIVE_DISPOSITION.md), [live interaction](../guides/live-interaction.md), and
[STABILITY](STABILITY.md)). Flask and
Django adapters keep **bounded polling** as the Supported live-status fallback; they do not
ship the FastAPI SSE/WebSocket helpers (import adapter live helpers from
`hedron_flask.experimental` / `hedron_django.experimental` when needed).

## Errors

| Situation | Host | Behavior |
|---|---|---|
| Invalid QuerySet type for `DjangoQuerySetDataSource` | Django data | `TypeError` |
| Query count over budget | Django data | `QueryBudgetExceeded` |
| CSRF missing/invalid on unsafe method | Flask `hedron_route` / `respond` | HTTP 403 |
| CSRF missing/invalid | Django (middleware + portable header) | HTTP 403 (Django CSRF) |
| Unauthorized fragment / OOB region | Flask / Django | HTTP 403 body |
| Invalid approved HTMX header values | All adapters | Rejected at adapter boundary |
| FastAPI SSE helpers imported on Flask/Django | N/A | Not shipped — use polling |
| `page`/`route` before `init_app` | Flask | `RuntimeError` |

## Not Supported (superseded or Deferred)

| Claim | Notes |
|---|---|
| Full adapter live browser matrix | **Superseded** in 0.24 (`LIVE-011-BROWSER` / `BROWSER-024`); polling Supported; live helpers remain Experimental |
| Load/proxy backpressure proof for SSE/WS | **Superseded** in 0.24 (`PERF-10-001` / `PERF-024`); prefer polling |
| Explorer live traces | Deferred `EXPLORER-10-001` on `0.10.x` (not re-homed to 0.24) |

CameraCapture / MicrophoneCapture ship as **Supported** on the FastAPI flagship (with
permission/retention policy) — see [What’s ready](../guides/whats-ready.md).

## Capability matrix

Machine-readable records: `hedron_core.adapter.capability_matrix()` /
[COMPATIBILITY](../COMPATIBILITY.md) / [acceptance/ADAPTERS](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/ADAPTERS.md).


## ASGI prepare (`respond_async`)

Sync `respond()` / `_maybe_prepare` **fail closed** when an event loop is already running —
unprepared trees are not rendered silently. On Django ASGI (and Flask async callers), use
`await HedronDjango.respond_async(...)` / `await HedronFlask.respond_async(...)` so
`prepare_tree` is awaited before render. Direct `component_response` callers under a running
loop must await `prepare_tree` themselves and pass `skip_prepare=True`.
