# Framework adapter acceptance

These requirements own roadmap gates 0.7A, 0.7C, 0.7D, and the portable portion of 0.7E. Evidence
follows [the release evidence policy](EVIDENCE.md).

## Portable foundation

| ID | Requirement | Required evidence | State |
|---|---|---|---|
| ADP-001 | Adapter-neutral interaction, URL, asset/build, auth/session signal, lifecycle, and diagnostic contracts live outside concrete framework packages. | Import-boundary test with FastAPI, Flask, Django, Starlette, and WSGI/ASGI implementations absent from the core environment. | Verified |
| ADP-002 | Portable page/fragment, safe-header, OOB, status, history, cache, and error semantics pass one shared conformance suite. | Shared suite executed against every supported adapter. | Verified |
| ADP-003 | Capability matrix labels every guarantee portable, ASGI, WSGI, or framework-specific. | Published matrix plus native test ID for each supported claim. | Verified |
| ADP-004 | Request-aware URLs preserve parameters, encoding, mounts, ASGI `root_path`, WSGI `SCRIPT_NAME`, and proxy prefixes. | Cross-adapter URL corpus behind prefixed deployment fixtures. | Verified |
| ADP-005 | Explorer/adapter dependencies are acyclic and adapter installation does not require FastAPI. | Wheel metadata and clean-environment import graph. | Verified |

## Flask

| ID | Requirement | Required evidence | State |
|---|---|---|---|
| ADP-FLK-001 | Routing, request context, errors, URL reversal, sessions, CSRF integration, and static assets remain Flask-native. | Native Flask reference slice and conformance report. | Verified |
| ADP-FLK-002 | WSGI limitations, including disconnect cancellation and lifespan behavior, are explicit. | Capability documentation matched to reference WSGI server tests. | Verified |
| ADP-FLK-003 | Wheel/sdist install without FastAPI and include typing, licenses, and required assets. | Clean-install packaging jobs across the supported Python/platform matrix. | Verified |

## Django

| ID | Requirement | Required evidence | State |
|---|---|---|---|
| ADP-DJG-001 | URL configuration, middleware, errors, reverse URLs, sessions, CSRF, and static assets remain Django-native. Apps may use Django-native forms; Hedron does **not** claim a verified forms/validation subsystem. | Native Django reference slice and conformance report. | Verified (forms: Deferred) |
| ADP-DJG-002 | ASGI and WSGI capability differences are explicit; QuerySet data-source support is implemented or formally deferred. | Mode-specific matrix and owning data-source decision/test. | Deferred |
| ADP-DJG-003 | Wheel/sdist install without FastAPI and include typing, licenses, and required assets. | Clean-install packaging jobs across the supported Python/platform matrix. | Verified |
| ADP-DJG-004 | First-party Django forms bridge (widgets, CSRF field helpers, error rendering) | Not implemented in 0.8; apps own Django forms. | Deferred |

## Exit

Every advertised adapter is labeled `supported`, `experimental`, or `deferred`. Only `supported`
adapters contribute to the 0.7 and 1.0 compatibility promise, and every supported claim is
`Verified` rather than inferred from the portable suite.
