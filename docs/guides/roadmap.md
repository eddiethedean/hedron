# Roadmap (public)

Capability phases for adopters. The full phase tables, gates, and RFC ownership live
in the [maintainer roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).

| Phase | Theme | Status |
|---|---|---|
| **0.10** | Live interaction on FastAPI (SSE, streaming, WebSockets, Chat/Dialog, preload) | Published (`v0.10.x`) |
| **0.11** | Native Flask/Django depth; bounded QuerySet integration | **Published** (`v0.11.0`) |
| **0.12+** | Data/visualization scale and later phases — see maintainer roadmap | Planned |

## What this means for you

- Pin `hedron` (and extras) in production; `0.x` may still take breaking changes under the
  [compatibility policy](../COMPATIBILITY.md).
- Package maturity is **Beta** for the flagship and most adapters; charts remain **Alpha**.
- No `1.0` phase is scheduled (D-038). Public APIs are catalogued as `beta` until promoted.

## Honest gaps on 0.11

- Full multi-engine adapter live browser matrix → owned `0.11.x` Deferred (`LIVE-011-BROWSER`)
- Full multi-engine FastAPI live browser matrix / some Explorer live traces → owned `0.10.x` Deferred

The first-party live sample
([`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction))
addresses FastAPI live learning paths. Flask/Django ship capability-labeled live helpers with
polling as the Supported fallback.
Details: [What's ready today](whats-ready.md) · [Production readiness](production-readiness.md).
