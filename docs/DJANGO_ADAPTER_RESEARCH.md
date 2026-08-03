# Hedron-Django quality and post-freeze feature research

**Status:** planning research

**Reviewed:** 2026-08-03

**Supported upstream baseline:** Django 5.2.16 LTS, asgiref 3.x

**Future-line research baseline:** Django 6.0.7; Django 6.1 is still a release candidate

## Executive decision

`hedron-django` can reach the same product quality as Hedron's FastAPI backend without copying
FastAPI's programming model. The useful parity target is equivalent Hedron rendering, HTMX,
security, assets, diagnostics, testing, documentation, and operational evidence through native
Django mechanisms. FastAPI dependency injection, automatic OpenAPI, Starlette lifespan, and an
always-ASGI request model are not Django parity requirements.

The release boundary is decisive:

1. **0.7 is the completed baseline.** The repository marks the coordinated `0.7.0` train cut-ready
   and `hedron-django` Supported. `ADP-DJG-001` and `003` are Verified; the QuerySet portion of
   `ADP-DJG-002` is intentionally Deferred by D-036.
2. **0.8 hardens the existing adapter without adding features.** The normative roadmap forbids a
   new subsystem, adapter, or transport during this phase. Existing correctness, compatibility,
   security, packaging, documentation, and evidence gaps are in scope.
3. **1.0 stabilizes the frozen surface. Net-new Django conveniences belong after 1.0**, shipped as
   additive minor releases with explicit capability and conformance evidence.

This preserves the commitments in the [roadmap](ROADMAP.md),
[adapter contract](api/ADAPTERS.md), [compatibility policy](COMPATIBILITY.md), and
[adapter acceptance ledger](acceptance/ADAPTERS.md).

## What “same quality” should mean

| Quality dimension | Django target | Deliberate difference from FastAPI |
|---|---|---|
| Components and HTML | Same safe output, render modes, assets, themes, and component packages | Django owns the final `HttpResponse` and middleware processing |
| Routing | Native URLconfs, converters, `include()`, application/instance namespaces, `reverse()`, and class-based views | No `APIRouter`, dependency graph, operation IDs, or automatic OpenAPI |
| HTMX | Same approved headers, OOB rules, history/cache variation, status semantics, and browser behavior | Request facts come from `HttpRequest`; middleware remains authoritative |
| Validation | Native `Form`, `ModelForm`, formsets, widgets, cleaned data, and accessible field/non-field errors | No signature-driven Pydantic request injection; model writes remain application-owned |
| Sessions and CSRF | Native session engines and `CsrfViewMiddleware`, including correct cache and cookie variation | Hedron exposes helpers; it does not replace Django's security implementation |
| Authentication | Translate `request.user` and explicitly selected permissions/tenant facts into `AuthSignal` | Django auth backends and permission policy remain authoritative |
| Async and jobs | Truthful sync/async view behavior under both WSGI and ASGI; durable Hedron jobs and polling | WSGI async uses a one-off loop; full async depends on the whole middleware/ORM path |
| Diagnostics | Native `AppConfig`, system checks, management commands, logging, and sanitized capability reports | No Starlette lifespan or FastAPI route introspection |
| Testing | Shared portable suite plus Django `Client`, `AsyncClient`, database, middleware, staticfiles, and server tests | WSGI and ASGI are separate evidence profiles |
| Operations | Production WSGI/ASGI entry points, proxy prefixes, static collection, health, and degradation proof | Django settings, server, middleware, and database remain deployment authorities |

Parity is measured by truthful contracts, native ergonomics, and evidence—not by reproducing the
same framework-specific names in every adapter.

## Current 0.7 baseline and 0.8 audit targets

The current adapter plus selected shared conformance tests pass on the repository's Django 5.2.16
environment:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run pytest \
  tests/adapters/django \
  tests/conformance/test_portable_interaction.py \
  tests/conformance/test_url_reverse.py \
  tests/unit/test_capability_matrix.py -q
.................                                                        [100%]
17 passed in 0.33s
```

This research treats 0.7 as complete. The following are deeper tests or corrections to public 0.7
behavior, not proposals to reopen that phase or add a 0.8 subsystem.

| Existing 0.7 surface | 0.8 hardening target |
|---|---|
| Wheel metadata, `py.typed`, import boundary, and exact core dependency | Build and install wheel and sdist in isolated environments. Verify license, classifiers, package data, exact train dependency, and absence of FastAPI/Starlette imports. |
| `component_response` and `interaction_response` | Expand the shared corpus for existing headers, `Vary`, status codes, authorized OOB regions/selectors, fragment extraction, locale/theme context, streaming rejection, and normal Django response interoperability. |
| `@hedron_view` | Preserve sync and async callable identity and return conversion. A spot check shows that wrapping `async def` currently yields `wrapped_is_async=False`; Django therefore cannot dispatch the existing helper correctly as an async view. |
| `DjangoUrlReverser` | Prove nested namespaces, positional/keyword arguments, Unicode, query/fragment policy, `current_app`, `FORCE_SCRIPT_NAME`, WSGI `SCRIPT_NAME`, ASGI `root_path`, and proxy prefixes. Avoid manual prefix concatenation when Django's resolver already owns the script prefix. |
| CSRF and auth helpers | Test real middleware ordering, rotated CSRF cookies, header/form tokens, cache variation, anonymous/authenticated/custom users, permission mapping, sessions without a database, and a missing middleware path with an actionable diagnostic. |
| Advertised WSGI and ASGI modes | Give the reference slice both `application` entry points and run native clients/server smoke tests. The current reference slice exposes WSGI only and omits `AuthenticationMiddleware`, forms, staticfiles, and deployment checks. |
| Native forms/validation and assets already claimed by ADP-DJG-001 | Tie each claim to a concrete reference-slice test. Current adapter tests cover basic page, fragment, and interaction responses but do not exercise `Form`/`ModelForm`, validation errors, `collectstatic`, or static URL resolution. |
| Deferred QuerySet DataSource | Keep `QUERYSET_DATASOURCE_DEFERRED=True` and capability metadata consistent through 1.0. Do not let accepting a raw `QuerySet` accidentally become an undocumented lazy data path. |

The async wrapper is the clearest existing-function defect. Fixing it during a feature freeze does
not imply support for async transactions, Channels, WebSockets, or any other new capability.

## Upstream findings that affect the design

### The supported Django floor should become the 5.2 LTS line

The package currently declares `django>=5,<6`. As of this review, Django's official download page
lists 5.0 and 5.1 as unsupported, Django 5.2.16 as the supported LTS line through April 2028, and
Django 6.0.7 as the current feature release. Django recommends the newest patch in a supported
series. The 0.8 compatibility/security correction should therefore narrow the supported range to
`Django>=5.2,<6` and test the latest 5.2 patch. Supporting already-unsupported 5.0/5.1 would weaken
the adapter's security promise.

Django 6.x belongs in a post-1.0 compatibility release. It is outside the frozen dependency cap,
and its Python floor and deprecations must be reconciled with Hedron's Python matrix. Do not widen
to `<7` based on an import smoke test; run the complete adapter, reference, packaging, forms,
staticfiles, WSGI, and ASGI matrices first.

Sources: [official Django downloads and support table](https://www.djangoproject.com/download/),
[Django 5.2 release notes](https://docs.djangoproject.com/en/5.2/releases/5.2/).

### A reusable Django app is the right post-1.0 integration shape

A future ergonomic layer should make `hedron_django` an ordinary installable Django app with an
`AppConfig`. `AppConfig.ready()` is appropriate for idempotent registration of system checks and
signals, but never for database queries, registry evaluation, asset building, or remote I/O. Django
runs app initialization for management commands as well as servers, and tests can invoke `ready()`
more than once.

The first native diagnostics should be system checks rather than a custom import-time validator:

- compatibility checks for supported Django/asgiref versions;
- configuration checks for required middleware and ordering;
- URL namespace and duplicate route/component identity checks;
- staticfiles/template installation checks when those optional bridges are enabled;
- deployment-only security checks registered for `check --deploy`.

This gives projects normal `manage.py check` behavior and avoids another lifecycle model.

Sources: [Django applications and `AppConfig`](https://docs.djangoproject.com/en/5.2/ref/applications/),
[system check framework](https://docs.djangoproject.com/en/5.2/topics/checks/),
[deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).

### URLconfs and namespaces must remain authoritative

Hedron route identity should be based on the final namespaced Django view name, not only a function
name or path string. Reusable apps can be mounted multiple times with distinct instance namespaces,
and nested application namespaces are normal. The post-1.0 convenience layer should expose a small
`app_name = "hedron"` URLconf or URL-pattern factory; it should not maintain a second router.

Django 5.2 added `query` and `fragment` arguments to `reverse()`/`reverse_lazy()`. Hedron's portable
URL contract should either map to those explicitly or document why query/fragment composition stays
in core. Prefix behavior should be tested through configured script prefixes and request/server
fixtures, not reproduced with string concatenation.

Source: [Django URL reversing](https://docs.djangoproject.com/en/5.2/ref/urlresolvers/).

### Async quality requires two honest deployment profiles

Django detects async views with `asgiref.sync.iscoroutinefunction`; a decorator that returns a
coroutine must preserve or mark that identity. Under WSGI, an async view runs in a one-off event loop
and receives no full async-stack benefit. Under ASGI, one synchronous middleware can reintroduce a
thread per request. Sync/async transitions also carry measurable overhead.

The correct claims are:

- synchronous views under WSGI: Supported;
- synchronous views under ASGI: Supported, with adaptation cost recorded;
- asynchronous views under WSGI: Supported only as Django supports them, with a one-off loop and no
  ASGI scalability claim;
- asynchronous views under ASGI: Supported only when `@hedron_view`, middleware, and invoked code
  pass native async tests;
- async ORM calls: use Django's `a*` methods or `async for`;
- transactions: remain synchronous and should be isolated in one function via `sync_to_async()`;
- persistent database connections in async mode: not a Hedron promise;
- WebSockets and long-lived live transport: not part of the Django adapter claim.

Sources: [Django asynchronous support](https://docs.djangoproject.com/en/5.2/topics/async/),
[async QuerySet guidance](https://docs.djangoproject.com/en/5.2/topics/db/queries/#asynchronous-queries),
[middleware sync/async behavior](https://docs.djangoproject.com/en/5.2/topics/http/middleware/#asynchronous-support).

### Forms should be adapted, not replaced

Django Forms already own binding, field coercion, validation, widgets, rendering, files, formsets,
and field/non-field errors. `ModelForm` also owns model validation and save semantics. A future
Hedron bridge should translate a bound `Form` into Hedron controls and translate its error data into
accessible fragments while leaving `is_valid()`, `cleaned_data`, and `save()` explicit in the view.

Django 5.2's `BoundField` customization and `aria-describedby` support make a native rendering
bridge especially attractive. The adapter must preserve prefixes, formsets, `MultiValueField`,
uploaded files, disabled fields, localization, custom widgets, model constraints, and non-field
errors. It must not silently convert a `ModelForm` into a Pydantic model or auto-save it.

Sources: [working with forms](https://docs.djangoproject.com/en/5.2/topics/forms/),
[creating forms from models](https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/),
[Django 5.2 form and accessibility changes](https://docs.djangoproject.com/en/5.2/releases/5.2/#forms).

### Middleware order is part of the adapter contract

Session, authentication, message, CSRF, cache, locale, compression, and security middleware have
ordering rules. Hedron should inspect and report the effective configuration, not install global
middleware automatically. In particular, authentication follows sessions; message middleware
depends on sessions; CSRF must run before view middleware that assumes protection; and cache order
affects CSRF cookie and `Vary` behavior.

If a later Hedron middleware is necessary, it should be dual sync/async, narrowly responsible for
sanitized render context or diagnostics, and declare its ordering constraints through system checks.
Rendering and response conversion should remain usable without it.

Sources: [Django middleware](https://docs.djangoproject.com/en/5.2/topics/http/middleware/),
[CSRF guidance](https://docs.djangoproject.com/en/5.2/howto/csrf/),
[messages framework](https://docs.djangoproject.com/en/5.2/ref/contrib/messages/).

### Static assets belong to `staticfiles`

An installed-app integration can ship namespaced assets under `hedron_django/static/hedron/` and
resolve them through Django's `static` machinery. Production still requires the application's
chosen `STORAGES["staticfiles"]` backend, `collectstatic`, and an external server/CDN or suitable
deployment middleware. Hedron must publish hashes/version metadata and CSP requirements without
pretending to be the production static server.

Sources: [managing static files](https://docs.djangoproject.com/en/5.2/howto/static-files/),
[deploying static files](https://docs.djangoproject.com/en/5.2/howto/static-files/deployment/).

## Phase 0.8 hardening plan

No item below creates a new public feature.

1. **Freeze and classify the API.** Mark every export, setting, capability value, rendered markup
   contract, header, and diagnostic record public or private. Exercise the deprecation policy from
   the published 0.7 artifacts.
2. **Correct the supported dependency range.** Test Django 5.2.16 and subsequent 5.2 security
   patches with supported asgiref and Python 3.11–3.14 combinations. Narrow the declaration from all
   5.x releases to the supported LTS line through the compatibility-change process.
3. **Close existing correctness/evidence gaps.** Make `hedron_view` preserve sync/async identity;
   settle resolver-owned prefix behavior; add both WSGI and ASGI reference entry points; and prove
   the existing forms, sessions, CSRF, URL, static asset, and error-response claims.
4. **Deepen portable interaction conformance.** Run the complete status, OOB, authorized-target,
   history, cache-variation, redirect, validation/error, and non-HTMX fallback corpus through the
   Django adapter with one evidence ID per behavior cluster.
5. **Complete native security evidence.** Run `check --deploy` against production settings; test
   hostile Host/proxy headers, cookie flags, CSRF replay/rotation, request/file/field limits, cache
   separation, header injection, trusted HTML/URL boundaries, SBOM, vulnerabilities, and licenses.
6. **Complete browser and accessibility evidence.** Chromium, Firefox, and WebKit for HTMX history,
   focus, OOB, races, errors, CSRF, reduced motion, keyboard operation, form errors, and useful
   non-JavaScript fallback.
7. **Set and enforce performance budgets.** App initialization, URL registration/reversal,
   page/fragment rendering, interaction conversion, CSRF token access, middleware transitions,
   WSGI concurrency, ASGI sync/async paths, and reference deployment. Compare with plain Django and
   the FastAPI adapter without claiming identical concurrency models.
8. **Rehearse artifacts and deployments.** Clean wheel/sdist install, `manage.py check`,
   `collectstatic`, migrations-with-no-Hedron-models, WSGI/ASGI startup, prefixed proxy deployment,
   upgrade, rollback, and removal from published `1.0.0rcN` artifacts.

## Post-1.0 Django feature candidates

These candidates are ordered by expected value and architectural fit. They should not be pulled
into 0.8.

### 1.1 — Django-native integration and authoring

1. **Installable app and system checks.** Add `HedronDjangoConfig` with idempotent, no-I/O
   registration and useful `hedron.*` check IDs for version, middleware, URL, template, and
   staticfiles configuration.
2. **Dual sync/async view adaptation.** A stable decorator and class-view mixin that preserve
   coroutine identity, await the underlying view, convert the same Hedron return types, and compose
   with Django's auth/cache/HTTP decorators.
3. **Namespaced URL helpers.** Reusable URL patterns for explicitly exposed components/actions,
   mounted through `include()` with application and instance namespaces; Django `reverse()` remains
   the only resolver.
4. **Django Form bridge.** Render `Form`, `ModelForm`, and formset fields as Hedron components while
   preserving bound values, widgets, prefixes, media, uploaded files, cleaned data, and accessible
   field/non-field errors. Saving stays explicit.
5. **Template interoperability.** A safe `{% hedron_component %}` tag and optional block tag for
   ordinary Django templates. Autoescape, `SafeString`, CSP, context processors, and duplicate
   rendering must have adversarial tests.
6. **Staticfiles integration.** Namespaced core/extension assets with manifest hashes, offline
   resolution, external-host support, `collectstatic` checks, and no assumption about the serving
   backend.

### 1.2 — QuerySet DataSource

This is the highest-value Django-specific data feature and the highest-risk candidate. Superseding
D-036 requires a new accepted design decision and a security/performance evidence plan.

1. **Explicit source construction.** Accept an application-supplied, already-authorized base
   `QuerySet`; never discover a model or call `.objects.all()` from user input.
2. **Bounded server-side operations.** Allowlisted ordering, filtering, projection, searching, and
   page sizes. Tenant/auth scoping must occur before any client-controlled refinement and remain
   impossible to remove.
3. **Stable pagination.** Require deterministic ordering. Offer ordinary `Paginator` behavior for
   bounded sets and an explicit cursor/keyset mode for large or mutable sets; Django warns that
   high offset pages can become slow.
4. **Evaluation contract.** Never evaluate a lazy QuerySet during component import, app startup,
   diagnostics, schema description, or after the request's database context has ended. Make count
   strategy and query budgets visible.
5. **ORM efficiency.** Application hooks for `select_related()`, `prefetch_related()`, annotations,
   values/projection, and database routing; query-count and N+1 regression tests.
6. **Sync/async split.** Native async iteration and `a*` evaluation where supported; transactional
   mutations stay in a bounded synchronous function. Do not pass connection-bound objects across
   threads.
7. **Database matrix.** SQLite for fast semantics plus PostgreSQL as the production reference;
   document backend-sensitive null ordering, collations, search, composite keys, and isolation.

Sources: [QuerySet laziness and async queries](https://docs.djangoproject.com/en/5.2/topics/db/queries/),
[Django paginator behavior and large-offset warning](https://docs.djangoproject.com/en/5.2/ref/paginator/).

### 1.3 — Django ecosystem bridges

1. **Authentication and permissions bridge.** Map `request.user`, explicitly selected permissions,
   and application-owned tenant facts into `AuthSignal`; integrate with function decorators and
   `AccessMixin` without making Hedron an identity provider.
2. **Messages bridge.** Render `django.contrib.messages` as accessible alerts/toasts while
   preserving levels, tags, consume-once behavior, sessions/cookies, and non-HTMX redirects.
3. **Class-based view mixins.** Component-aware `TemplateView`/`FormView`-style mixins with normal
   method resolution, `dispatch()`, decorators, and async rules; avoid a parallel CBV hierarchy.
4. **Admin coexistence.** Document Hedron pages alongside Django admin and optionally provide
   field-display components. Do not theme or monkey-patch the admin by default.
5. **Cache backend bridge.** Implement Hedron cache contracts over Django cache aliases with
   explicit serialization, namespace/version keys, tenant scope, timeouts, stampede behavior, and
   backend conformance.
6. **Job backend bridge.** A later Celery or Django-native queue integration may implement Hedron's
   existing `JobBackend`; the core adapter should not enqueue work implicitly from a response.

### 1.4 — operations and developer experience

1. **Management commands.** `manage.py hedron_check`, `hedron_routes`, and optionally
   `hedron_assets` for sanitized inventory and deterministic validation; commands should use normal
   Django output/check APIs and remain safe without database access unless explicitly requested.
2. **Production deployment profiles.** Tested Gunicorn WSGI and Uvicorn/Daphne ASGI examples,
   reverse-proxy prefix handling, static-host separation, health/readiness, graceful shutdown, and
   worker/thread/database guidance.
3. **Observability hooks.** Django logging and OpenTelemetry-compatible spans around component
   rendering, interactions, data queries, jobs, and cache operations, with bounded labels and no
   raw props, session data, query parameters, or SQL values.
4. **Reusable-app test kit.** Shared fixtures for Django `Client`, `AsyncClient`, middleware
   variants, URL namespaces, SQLite/PostgreSQL, `StaticLiveServerTestCase`, clean settings, and
   system checks.

### Later or separate evaluation

- Django 6.x support after a complete compatibility RFC and matrix.
- Django Channels/WebSockets as an optional transport package, not an implicit adapter capability.
- SSE only under the existing transport decision process.
- Optional Django REST Framework or django-ninja interop only if a real mixed HTML/API use case is
  demonstrated; neither is required for native Django quality.
- Streaming component responses only after deterministic rendering, middleware, disconnect,
  compression, caching, and error semantics are designed explicitly.

## Highest-risk implementation traps

1. **A sync decorator around an async view.** It breaks Django's callable detection and can leak an
   un-awaited coroutine. Use distinct sync/async wrappers and test both request stacks.
2. **A second router or manual prefixing.** It will diverge from URL namespaces,
   `FORCE_SCRIPT_NAME`, locale patterns, custom converters, and reverse-proxy deployment.
3. **Global work in `AppConfig.ready()`.** Database queries, network calls, builds, or non-idempotent
   registration run in management commands and can corrupt tests/startup behavior.
4. **Automatic middleware insertion.** Ordering changes security and cache semantics. Report
   requirements; let the application own `MIDDLEWARE`.
5. **Evaluating arbitrary QuerySets.** Lazy evaluation can cross async/thread/request boundaries,
   produce unbounded queries, leak tenants, and create N+1 loads.
6. **Treating permissions as display hints.** Authorization must occur before query/mutation and
   again at the operation boundary; hiding a component is not authorization.
7. **Bypassing CSRF for HTMX.** HTMX requests are normal unsafe HTTP requests. Never normalize
   adoption with `csrf_exempt` or a second token scheme.
8. **Converting `ModelForm.save()` implicitly.** Commit behavior, transactions, `save_m2m()`, model
   constraints, and optimistic concurrency belong in explicit application code.
9. **Serving production assets from Django.** `staticfiles` discovery and `collectstatic` do not
   make the adapter a CDN or production file server.
10. **Leaking diagnostics.** Route kwargs, form data/errors, model representations, SQL, settings,
    session keys, user fields, and component props require sanitization and bounded cardinality.

## Recommended release sequence

| Release | Django work | Gate |
|---|---|---|
| 0.8 | Existing-surface hardening only: supported 5.2 floor, async decorator correction, resolver/prefix proof, native-claim evidence, security, packaging, browser, accessibility, performance | No new public subsystem or convenience layer |
| 1.0 RCs | Clean install/upgrade/rollback and published-artifact rehearsals for both WSGI and ASGI profiles | All Supported claims traced to immutable evidence |
| 1.0 | Freeze truthful native adapter surface; QuerySet remains Deferred | Same quality bar as flagship, not the same framework features |
| 1.1 | Installable app, checks, dual-mode views, URL helpers, Forms bridge, templates/staticfiles | Additive API, native Django conformance, migration guide |
| 1.2 | QuerySet DataSource, if its RFC and evidence pass | Tenant isolation, query budgets, stable paging, DB and sync/async matrices |
| 1.3+ | Auth/messages/CBV/cache/jobs/operations bridges | Each optional integration independently installable and evidenced |

## Definition of done for post-1.0 Django features

Every feature above must include:

- a precise capability record and stability label;
- native Django tests plus the applicable shared portable suite;
- WSGI/ASGI behavior stated separately where relevant;
- sync/async, middleware, database, cache, and deployment constraints;
- threat model, tenant/authorization boundaries, CSRF/cache/header tests, and sanitized diagnostics;
- keyboard, screen-reader, error, focus, reduced-motion, and non-JavaScript behavior;
- clean wheel/sdist installation without FastAPI and correct optional dependencies;
- performance/query budgets and graceful degradation evidence;
- reference application coverage, API docs, migration notes, and upgrade/rollback proof.

That standard—not matching FastAPI's feature count—is what will bring `hedron-django` up to the
same quality level as Hedron's flagship backend.

## Primary Django sources

- [Supported releases and current versions](https://www.djangoproject.com/download/)
- [Django 5.2 LTS release notes](https://docs.djangoproject.com/en/5.2/releases/5.2/)
- [Applications and `AppConfig`](https://docs.djangoproject.com/en/5.2/ref/applications/)
- [System check framework](https://docs.djangoproject.com/en/5.2/topics/checks/)
- [URL reversing](https://docs.djangoproject.com/en/5.2/ref/urlresolvers/)
- [Middleware](https://docs.djangoproject.com/en/5.2/topics/http/middleware/)
- [Asynchronous support](https://docs.djangoproject.com/en/5.2/topics/async/)
- [Forms](https://docs.djangoproject.com/en/5.2/topics/forms/)
- [`ModelForm`](https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/)
- [QuerySets](https://docs.djangoproject.com/en/5.2/topics/db/queries/)
- [Pagination](https://docs.djangoproject.com/en/5.2/ref/paginator/)
- [Testing overview](https://docs.djangoproject.com/en/5.2/topics/testing/overview/)
- [Advanced testing and ASGI request factories](https://docs.djangoproject.com/en/5.2/topics/testing/advanced/)
- [CSRF protection](https://docs.djangoproject.com/en/5.2/howto/csrf/)
- [Staticfiles development integration](https://docs.djangoproject.com/en/5.2/howto/static-files/)
- [Staticfiles deployment](https://docs.djangoproject.com/en/5.2/howto/static-files/deployment/)
- [Deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Custom management commands](https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/)
