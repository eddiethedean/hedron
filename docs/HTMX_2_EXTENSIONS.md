# HTMX 2 extension evaluation (phase 0.10)

**Status:** Official SSE and head-support pinned for phase 0.10 (D-044 / RFC-0032)
**Date:** 2026-08-04

Hedron's fragment asset/head policy:

1. PAGE responses inject required shell assets (HTMX core, build CSS/JS, disclosed modules).
2. FRAGMENT responses do **not** invent `<head>` script tags; they assume the shell already
   loaded required runtimes unless registered head management (`htmx-ext-head-support`) is enabled.
3. Optional HTMX extensions are independently versioned browser assets and are never implied by
   the core HTMX pin (2.0.10). See `hedron_core.htmx_extensions.ExtensionAsset`.

## Evaluations

| Extension | Decision | Rationale |
|---|---|---|
| Official SSE (`htmx-ext-sse`) | **Experimental (API); asset Supported** | Pinned local asset; job/region observation with auth/reconnect; polling remains Supported fallback under 0.24 `polling_only` (ops IDs Superseded — helpers stay experimental). |
| `head-support` | **Supported (optional)** | Locally served with digest/CSP/load order for registered fragment head merge. |
| Idiomorph | **Deferred (opt-in later)** | Morphing helps preserve custom-element state, but form/focus/CE lifecycle harnesses are not yet green enough to ship a pinned default. |
| `response-targets` | **Deferred** | Core `HX-Retarget` / `HX-Reselect` plus `InteractionResult` status policies cover declared error/validation targets without another extension. |
| View Transitions | **Deferred** | Progressive enhancement only; requires `prefers-reduced-motion` gating and focus stability evidence reserved for later browser-matrix work. |

## Conformance notes

- Custom elements that register `htmx_lifecycle=True` must tolerate swap/settle/teardown.
- Prefer stable hosts and targeted descendant swaps; use `hx-preserve` only where identity and
  teardown are proven.
- Explorer interaction simulation reports `assets: predeclared-shell` for routes.
- Removed HTMX 1 attributes remain rejected.
