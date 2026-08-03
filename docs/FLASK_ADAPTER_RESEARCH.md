# Hedron-Flask quality and post-freeze feature research

**Status:** planning research  
**Reviewed:** 2026-08-03  
**Upstream baseline:** Flask 3.1.3, Werkzeug 3.1.8, Waitress 3.0.2

## Executive decision

`hedron-flask` can reach the same product quality as the FastAPI backend, but it should not promise
identical framework capabilities. The useful parity target is equivalent Hedron rendering, HTMX,
security, asset, diagnostics, testing, and documentation quality through native Flask mechanisms.
FastAPI dependency injection, OpenAPI generation, ASGI cancellation, lifespan, and in-process
background tasks are not Flask parity requirements.

The release sequence matters:

1. **0.7 is the completed baseline.** The repository marks the coordinated `0.7.0` train cut-ready
   and the Flask adapter Supported, with `ADP-FLK-001` through `003` recorded as Verified.
2. **0.8 must harden that baseline without adding features.** The normative roadmap explicitly forbids
   a new subsystem, adapter, or transport during 0.8.
3. **1.0 stabilizes the frozen surface; net-new Flask conveniences belong after 1.0**, preferably
   in small minor releases with their
   own capability and conformance evidence.

This preserves the commitments in the [roadmap](ROADMAP.md),
[adapter contract](api/ADAPTERS.md), and [adapter acceptance ledger](acceptance/ADAPTERS.md).

## What “same quality” should mean

| Quality dimension | Flask target | Deliberate difference from FastAPI |
|---|---|---|
| Components and HTML | Same safe output, render modes, assets, themes, and component packages | Flask owns the final `Response` |
| Routing | Native `Blueprint`, `add_url_rule`, endpoint names, converters, `url_for` | No `APIRouter`, `Depends`, operation IDs, or automatic OpenAPI |
| HTMX | Same approved headers, OOB rules, history/cache variation, status semantics, and browser behavior | Request facts come from `flask.request` |
| Validation | Explicit Pydantic form/query/JSON binding with accessible error fragments | No signature-driven FastAPI request injection |
| Sessions and CSRF | Typed state over Flask `session`; same Hedron double-submit token semantics | Flask owns signing, cookie persistence, and session interface |
| Security | Same Hedron profiles plus Flask host, cookie, form, and proxy controls | WSGI server and Flask configuration remain authoritative |
| Async and jobs | Sync views supported; conditional coroutine views through Flask's async extra; durable jobs and polling | No disconnect cancellation, request task group, lifespan, or `BackgroundTasks` |
| Diagnostics | Same sanitized route/component/interaction information and evidence quality | Flask signals, contexts, CLI, and logging are used natively |
| Testing | Shared portable suite plus native client, session, CLI, proxy, server, and clean-install tests | No ASGI client or FastAPI dependency overrides |
| Operations | Production WSGI server, proxy-prefix, static, health, thread/process safety, and degradation proof | No claim that WSGI behaves like ASGI |

Quality is therefore measured by truthful contracts and evidence, not by the number of FastAPI
names reproduced in another package.

## Current 0.7 baseline and 0.8 audit targets

The repository records the adapter as implemented and Supported. Its current native suite passes:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/adapters/flask -q
.......                                                                  [100%]
7 passed
```

The research therefore treats 0.7 as complete. The table below identifies existing public behavior
that deserves deeper 0.8 hardening evidence; these are defect/compatibility targets, not proposals
to reopen 0.7 or add a 0.8 subsystem.

| Existing 0.7 surface | 0.8 hardening target |
|---|---|
| Wheel metadata, `py.typed`, and import-boundary test | Build and install both wheel and sdist in isolated environments. Confirm package data, license, classifiers, exact train dependencies, and no FastAPI/Starlette transitive import. |
| `HedronFlask(import_name).flask` wrapper and reference factory | Verify the documented WSGI object/factory entry points with `flask --app` and `waitress-serve --call`. The current example's `create_app()` returns the wrapper, so the documented invocation must either target `.flask` or the example should return the WSGI app as a compatibility fix. |
| `component_response` and `interaction_response` | Expand the portable corpus for cache `Vary`, status codes, OOB authorization/selection, fragment regions, existing headers, locale/theme context, and Flask response interoperability. |
| `hedron_route(app, ...)` | Lock down ordinary string/tuple/Response behavior and explicitly reject or support coroutine views. A spot check of a coroutine route currently produces a 500 and an un-awaited-coroutine warning, so this needs either an `ensure_sync` fix or a documented synchronous-only diagnostic. |
| `FlaskUrlReverser` | Add request-context, no-`SERVER_NAME`, parameter, Unicode, query, `SCRIPT_NAME`, and proxy-prefix cases. A spot check outside a request currently requires `SERVER_NAME`; ensure that matches the public contract or fix the existing behavior. |
| CSRF and auth helpers | Add adversarial cookie/header/form, secure-cookie, rotation, session-interface, and missing-session tests. A spot check found `auth_signal` reading `request.session`, which Flask does not expose; this is an existing-function defect to correct in 0.8. |
| Reference slice and capability record | Tie each claimed route, request-context, session/CSRF, error, asset, URL, and WSGI capability to a specific test rather than relying on the three roll-up IDs alone. |

These spot checks do not change the declared phase status. They are exactly the kind of compatibility
and correctness fixes the feature-frozen 0.8 phase is intended to catch before the 1.0 API promise.

## Upstream findings that affect the design

### Prefer the Flask extension and application-factory model for a post-1.0 ergonomic layer

The frozen 0.7 API constructs and exposes a native Flask app through `HedronFlask.flask`; 0.8 should
stabilize that behavior rather than replace it. For a later ergonomic layer, Flask's documented
extension pattern is the strongest fit:

```python
from flask import Flask
from hedron_flask import HedronBlueprint, HedronFlask

hedron = HedronFlask()
ui = HedronBlueprint("ui", __name__)

@ui.page("/")
def home():
    return HomePage()

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_prefixed_env()
    hedron.init_app(app)
    app.register_blueprint(ui)
    return app
```

If introduced after 1.0, `HedronFlask.init_app(app)` should store only per-application state in
`app.extensions["hedron"]`. The extension object must not retain an app. This supports multiple app
instances, test factories, and normal extension composition. `HedronBlueprint` should own
`page`, `component`, `action`, and `include_component` registration using `Blueprint` and
`add_url_rule`; route wrappers should call `current_app.ensure_sync(view)` so optional coroutine
views follow Flask's supported dispatch path.

This should be additive or follow a normal deprecation window; it must not silently invalidate the
existing constructor API. An optional `Hedron(Flask)` convenience subclass may also be considered.
It should not be the primary path. An explicit `html_response(value, ...)` helper should be
the interoperability path for ordinary `@app.route` views. Globally monkey-patching
`Flask.make_response` from an extension would be surprising and likely to conflict with other
extensions.

### Blueprints are construction plans, not routers already bound to an app

Blueprints can be nested and registered multiple times. Hedron route metadata must therefore be
finalized at blueprint registration, when the actual endpoint name, prefix, subdomain, and app are
known. A route's identity cannot be only the function name and decorator-time path. Repeated mounts
need distinct mount identities while retaining one component logical identity.

Blueprint-specific handlers also have precedence only after Flask has matched a route. A blueprint
cannot reliably own application-level 404 handling, so the adapter needs app-level semantic error
handlers for routing failures and may add more specific blueprint handlers for matched views.

### Request and application contexts are the native boundary

Use `request`, `session`, `g`, and `current_app`; do not add another request `ContextVar`. Raw Flask
objects stay inside `hedron_flask`. Only sanitized `HtmxContext`, `AuthSignal`, `RenderContext`, URL
requests, and diagnostics cross into `hedron-core`.

`teardown_appcontext` is usually run when a request's app context is popped. It is suitable for
request-scoped resources such as database connections, not process-global startup/shutdown. Flask
has no ASGI-style lifespan contract. Plugin resources that require process lifecycle must use an
explicit app-factory initialization contract, a server hook, or an external service and must be
reported as such in the capability matrix.

### Flask async support is useful but is not ASGI parity

Flask can run coroutine views, hooks, and error handlers when installed with its `async` extra, but
each request still occupies a WSGI worker. Flask starts an event loop for the request, and tasks
spawned by a view are cancelled when the view completes. The supported declaration should be:

- synchronous endpoints: supported;
- coroutine endpoints: supported only with an explicit `hedron-flask[async]` or documented
  `flask[async]` installation and native tests;
- disconnect cancellation, persistent request event loop, WebSockets, and in-view background tasks:
  unsupported;
- durable work: shared `JobBackend` plus bounded polling, with optional post-1.0 Celery/RQ bridges.

Serving Flask through `WsgiToAsgi` does not turn its application and request model into a native
ASGI adapter. If native ASGI becomes a product requirement, evaluate a separate Quart adapter
instead of silently changing `hedron-flask` claims.

### Modern Flask security features justify a narrower tested floor

The current [compatibility policy](COMPATIBILITY.md) says Flask and Werkzeug `>=3.0,<4`. During 0.8,
test and strongly consider raising the minimums to Flask `>=3.1.3` and Werkzeug `>=3.1.8` as an
approved compatibility/security correction:

- Flask 3.1 added `TRUSTED_HOSTS`, request/form resource limits, partitioned session cookies, and
  `SECRET_KEY_FALLBACKS` for key rotation.
- Flask 3.1.1 fixed fallback signing-key selection; Flask 3.1.3 fixed session access tracking.
- Werkzeug 3.1.4 through 3.1.6 fixed Windows `safe_join` device-path issues, and 3.1.7/3.1.8
  strengthened Host parsing.

If compatibility with Flask 3.0 remains important, the adapter must feature-detect these controls,
publish a reduced capability record for 3.0, and reproduce equivalent protection where feasible.
It must not advertise 3.1 security behavior across the full range.

Waitress 3.0.2 remains a reasonable cross-platform reference server, but its published metadata
does not claim Python 3.14 and its Flask deployment documentation notes that it buffers complete
request bodies and uses one process with multiple threads. Python 3.14 and request-limit behavior
must be promoted only after native evidence, not inferred from a version range.

## Required 0.7C implementation floor

These are release prerequisites, not post-freeze ideas.

### FLK-001 — package, factory, and state isolation

- Create a separately buildable `hedron-flask` wheel and sdist with `py.typed`, license, changelog,
  static assets, Flask classifier, and no `hedron`, FastAPI, Starlette, or ASGI dependency.
- Re-export the framework-neutral beginner component surface from `hedron-core` without importing
  optional data/chart packages eagerly.
- Implement `HedronFlask.init_app` with idempotent or explicitly rejected double initialization,
  `app.extensions["hedron"]` state, prefixed config keys, and multi-app isolation tests.
- Keep development/Explorer bridges optional and prove that installing them does not pull FastAPI.

### FLK-002 — native response and request adapters

- Convert `Component`, `HTML`, `RenderResult`, `InteractionResult`, and already-created Flask
  `Response` values inside Hedron view wrappers.
- Preserve normal Flask tuple behavior `(body, status, headers)` where the Hedron body is supported;
  pass ordinary strings, bytes, dicts, lists, generators, and WSGI responses back to Flask.
- Derive locale, theme, authenticated signal, HTMX facts, host reverse, and asset references from the
  active Flask request without retaining proxies in core values.
- Add an explicit `html_response` helper for existing ordinary Flask routes.
- Use Flask's response class and conditional/file response utilities rather than importing
  Starlette response types.

### FLK-003 — `HedronBlueprint` and route identity

- Implement `page`, `component`, `action`, and `include_component` over documented Blueprint and
  `add_url_rule` APIs.
- Preserve converters, defaults, strict slashes, subdomains, endpoint names, automatic `HEAD` and
  `OPTIONS`, decorator ordering, and Flask class-based view compatibility.
- Finalize registry entries at registration time; test nested and repeated blueprint mounts with
  unique names and prefixes.
- Reverse through `url_for`, including query parameters, Unicode, anchors, `_external`, subdomains,
  `SCRIPT_NAME`, and proxy prefixes. Never concatenate URL strings in the adapter.

### FLK-004 — complete HTMX interaction conversion

- Reuse the portable header allowlist, OOB authorization, page/fragment selection, declared target
  regions, history, cache policy, and status policies.
- Preserve `Vary: HX-Request, HX-History-Restore-Request` and add `HX-Target` only for declared
  target-dependent variants. Merge existing `Vary` values rather than overwriting them.
- Prove 202, 204, 3xx, 401, 403, 409, 422, 429, and 5xx behavior for HTMX and ordinary requests.
- Include DELETE query parameters, boosted navigation, history restore, focus, OOB ordering, and
  bounded polling in the shared browser corpus.

### FLK-005 — explicit typed input and accessible errors

- Provide explicit Pydantic helpers or a clearly named decorator for form, query, and JSON models.
  Do not infer a FastAPI-like dependency graph from every function signature.
- Preserve Werkzeug `MultiDict` semantics, repeated form fields, uploads, malformed bodies, and
  content types. Define whether unknown fields are rejected per model/policy.
- Translate adapter-owned `ValidationError` values into the shared accessible 422 fragment for HTMX
  and a documented ordinary Flask response for non-HTMX requests.
- Do not blanket-catch `Exception`; preserve Werkzeug `HTTPException`, Flask debug propagation,
  app/blueprint handler precedence, logging, and observability hooks.

### FLK-006 — sessions, CSRF, headers, and redirects

- Implement typed `SessionState[T]` over the active Flask `session`, including assignment,
  clearing, validation failure, custom `SessionInterface`, and cookie-size tests.
- Document that Flask's default session cookie is signed, not encrypted; secrets and large values do
  not belong in it.
- Apply the existing double-submit CSRF policy with one request-scoped token, constant-time compare,
  header and form-field support, safe methods, secure cookie attributes, and useful 403 fragments.
- Map Hedron profiles to `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`,
  `SESSION_COOKIE_SAMESITE`, `TRUSTED_HOSTS`, request/form limits, CSP, referrer, frame, MIME, and
  authenticated cache controls without weakening explicit stricter app settings.
- Support `SECRET_KEY_FALLBACKS` and publish a key-rotation rehearsal. Refuse the development secret
  in strict/production mode.
- Use request-aware local redirect checks; external redirects remain an explicit policy opt-in.

### FLK-007 — static and compiled assets under real mounts

- Remove adapter-visible hard-coded `/hedron-static` and `/hedron-assets` URLs. Resolve them through
  Flask endpoints and `url_for` so `SCRIPT_NAME`, blueprint prefixes, and external static hosts work.
- Serve packaged assets through a dedicated blueprint or safe endpoint; serve build assets with
  safe joined paths, conditional responses, ETags, correct MIME types, immutable fingerprint cache
  policy, and no directory exposure.
- Define route-collision behavior with an application's own `static` endpoint.
- Prove offline/no-Node startup, manifest replacement, stale/missing build failure, CSP, and exact
  asset digest/license inventory.

### FLK-008 — diagnostics, CLI, Explorer, and observability

- Add factory-aware `flask hedron routes`, `flask hedron check`, and build/asset inspection commands
  or a documented bridge to the existing `hedron` CLI.
- Mount Explorer through an optional Flask blueprint with development/secured/off modes and native
  authorization hooks. Production development mode must fail closed as it does in the flagship.
- Use Flask request/error signals or native hooks for sanitized timing, route, HTMX, cache, and error
  traces. Signals are preferable for passive metrics; request hooks remain appropriate when they
  must affect a response.
- Keep telemetry exporters optional and never record cookies, CSRF tokens, session contents, form
  bodies, or authorization headers.

### FLK-009 — native reference slice, deployment, and evidence

- Build the required team-admin Flask slice with auth signal, typed create/edit/delete form,
  validation fragments, CSRF/session, reverse URLs, static/build assets, an addressable component,
  and one shared data/chart component.
- Test with Flask's `test_client`, `session_transaction`, request/app contexts, and
  `test_cli_runner`; add real Waitress HTTP tests for behavior the in-process client cannot prove.
- Test exact proxy trust counts with `ProxyFix`, `X-Forwarded-Prefix`, `SCRIPT_NAME`, Host attacks,
  direct-backend bypass, HTTPS cookie behavior, and prefix-aware assets/redirects.
- Run a clean environment matrix across supported Python, Flask, Werkzeug, Waitress, OS, and wheel /
  sdist combinations. A range is Supported only when the matching cells are green.
- Add thread-safety and multiple-app tests for extension state, registries, caches, route metadata,
  CSRF values, and diagnostics.

## Phase 0.8 hardening plan

No item below creates a new public feature.

1. **Freeze and classify the API.** Mark every exported symbol, config key, diagnostic record,
   rendered markup contract, endpoint name, and capability value public or private. Exercise the
   deprecation policy from 0.7 artifacts.
2. **Run the full compatibility matrix.** Minimum and latest supported Flask/Werkzeug patch,
   Waitress, Python 3.11–3.14, supported platforms, clean wheels/sdists, and dependency-minimum jobs.
3. **Complete security evidence.** Threat model, secret rotation, hostile Host/proxy headers,
   cookie flags, CSRF replay/rotation, request/form/file limits, path corpus, header injection,
   cache separation, SBOM, vulnerabilities, licenses, and provenance.
4. **Complete browser and accessibility evidence.** Chromium, Firefox, and WebKit for HTMX history,
   focus, OOB, races, errors, CSRF, reduced motion, keyboard behavior, and non-JavaScript fallback.
5. **Set and enforce performance budgets.** Cold factory initialization, route registration,
   page/fragment rendering, Pydantic form binding, session serialization, static conditional GET,
   concurrency under Waitress threads, and proxy deployment. Compare against plain Flask and the
   FastAPI adapter without claiming WSGI/ASGI throughput equivalence.
6. **Rehearse published artifacts.** Install, upgrade, key rotation, deployment, rollback, and
   removal from published `1.0.0rcN` artifacts. Retain immutable evidence tied to the lockfile and
   source revision.

## Post-1.0 Flask feature candidates

These are ordered by expected value and architectural fit. They should not be pulled into 0.8.

### 1.1 — native ecosystem bridges

1. **Jinja interoperability.** A safe `render_component(...)` Jinja global/filter and an explicit
   trusted-template-to-Hedron boundary, with autoescape and CSP tests.
2. **Flask-Login bridge.** Convert `current_user` to `AuthSignal` and provide Explorer/job
   authorization helpers without making Flask-Login required or owning identity.
3. **Authlib Flask helper.** Mirror the flagship convenience through Authlib's Flask client while
   leaving provider configuration, claims, callback security, and sessions to the app.
4. **Flash-message bridge.** Render Flask `flash()` categories as accessible Hedron alerts/toasts,
   with consume-once and non-HTMX behavior.

### 1.2 — richer typed Flask ergonomics

1. **`MethodView` component support.** Reusable page/component/action class views that preserve
   decorators, per-request instance rules, and method discovery.
2. **Typed binding policies.** Aliases, repeated values, file metadata, nested JSON/form conventions,
   partial PATCH models, and field-to-control error mapping, all explicit rather than implicit DI.
3. **Endpoint-aware links.** Typed wrappers around Flask endpoint names and converters with static
   analysis support, while keeping `url_for` authoritative.
4. **Server-side session adapters.** Documented compatibility with custom `SessionInterface`
   implementations plus size, serialization, expiry, and failure conformance.

### 1.3 — operations and jobs integrations

1. **Celery and RQ `JobBackend` bridges.** Pass identifiers and tenant/auth scope rather than Flask
   request objects; execute tasks under an explicit app context; retain the shared polling UI.
2. **Structured logging and OpenTelemetry bridge.** Optional Flask signal instrumentation with
   trace-context propagation and privacy budgets.
3. **Additional WSGI server profiles.** Gunicorn on supported POSIX platforms and a production
   topology matrix, without demoting Waitress's cross-platform reference role.
4. **External static serving recipes.** `X-Sendfile`, CDN/reverse-proxy build assets, and prefix-aware
   URL building with the same manifest integrity contract.

### Later or separate-adapter work

- Quart/native ASGI support should be a separate adapter decision.
- SSE remains subordinate to the already selected bounded-polling baseline.
- WebSockets do not belong in `hedron-flask` without a new accepted transport RFC.
- Automatic OpenAPI generation is low priority. If requested, integrate a Flask-native schema
  package behind an optional bridge; do not recreate FastAPI's dependency and schema engine.
- Streaming component rendering should remain experimental until headers, sessions, CSRF, assets,
  error behavior, and partial-output failure semantics have a coherent contract.

## Highest-risk implementation traps

1. **Hard-coded asset URLs:** current FastAPI response code embeds root-relative asset paths; Flask
   prefix correctness requires an adapter-neutral resolver before the first route is shipped.
2. **Premature Supported labels:** the current capability scaffold calls Flask Supported before its
   package and evidence exist. Keep it Planned/Experimental until `ADP-FLK-001` through `003` are
   Verified.
3. **Using app-context teardown as process shutdown:** this can close shared resources after every
   request.
4. **Async wrappers that call coroutines directly:** every adapter decorator must use
   `current_app.ensure_sync` and test the missing-async-extra diagnostic.
5. **Route metadata captured too early:** blueprint prefixes and endpoint names are incomplete until
   registration; repeated mounts make decorator-time global registration wrong.
6. **Session misconceptions:** Flask client sessions are readable by users, have browser cookie size
   limits, and need explicit key rotation and cookie policy.
7. **Proxy trust shortcuts:** `ProxyFix` counts are security boundaries. Never enable every forwarded
   header or trust arbitrary proxy depth by default.
8. **Over-broad error handlers:** a generic exception-to-fragment handler can swallow debugging,
   observability, or application-specific error behavior.
9. **Accidental FastAPI dependency:** importing `hedron` for cache, auth, CLI, or Explorer helpers
   violates the distribution boundary even when the import occurs only in development tests.
10. **Thread-unsafe globals:** Waitress uses worker threads; global current-request, route-build,
    registry mutation, or CSRF state will leak between requests.

## Release gate additions worth making before implementation

The existing three Flask IDs are too coarse to diagnose quality. Keep them as rollups, but add
stable child requirements for:

- factory/multi-app isolation;
- response return-type matrix;
- blueprint nesting/repeated registration;
- typed binding and semantic errors;
- HTMX/status/cache conformance;
- CSRF/session/security profiles and key rotation;
- asset/prefix/proxy behavior;
- async-extra and explicit WSGI limitations;
- Explorer/CLI/diagnostics isolation;
- thread safety and real Waitress deployment;
- clean-install dependency graph and artifact contents; and
- accessibility, browser, security, and performance evidence.

Each child should have an exact local command, CI job, matrix dimensions, retained artifact, and
owner under the [evidence policy](acceptance/EVIDENCE.md).

## Primary sources

- [Flask changes, including 3.1.3](https://flask.palletsprojects.com/en/stable/changes/)
- [Flask extension development](https://flask.palletsprojects.com/en/stable/extensiondev/)
- [Application factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)
- [Blueprints](https://flask.palletsprojects.com/en/stable/blueprints/)
- [Application and request lifecycle](https://flask.palletsprojects.com/en/stable/lifecycle/)
- [Request context and teardown behavior](https://flask.palletsprojects.com/en/stable/reqcontext/)
- [Async and await limitations](https://flask.palletsprojects.com/en/stable/async-await/)
- [Class-based views](https://flask.palletsprojects.com/en/stable/views/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
- [Security considerations](https://flask.palletsprojects.com/en/stable/web-security/)
- [ProxyFix deployment guidance](https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/)
- [Waitress deployment guidance](https://flask.palletsprojects.com/en/stable/deploying/waitress/)
- [Streaming constraints](https://flask.palletsprojects.com/en/stable/patterns/streaming/)
- [Background tasks with Celery](https://flask.palletsprojects.com/en/stable/patterns/celery/)
- [Werkzeug changes, including 3.1.8](https://werkzeug.palletsprojects.com/en/stable/changes/)
- [Waitress 3.0.2 package metadata and changelog](https://pypi.org/project/waitress/)
