# HTMX 2 extension evaluation (phase 0.6)

**Status:** Evaluated for phase 0.6; default remains predeclared page-shell assets  
**Date:** 2026-08-03

Hedron's fragment asset/head policy for 0.6:

1. PAGE responses inject required shell assets (HTMX core, build CSS/JS, disclosed modules).
2. FRAGMENT responses do **not** invent `<head>` script tags; they assume the shell already
   loaded required runtimes.
3. Optional HTMX extensions are independently versioned browser assets and are never implied by
   the core HTMX pin (2.0.10).

## Evaluations

| Extension | Decision | Rationale |
|---|---|---|
| `head-support` | **Deferred** | Predeclared shell assets cover first-party chart/content hosts; adopting head mutation needs CSP, ordering, and duplicate-load conformance not required for the 0.6 exit gate. |
| Idiomorph | **Deferred (opt-in later)** | Morphing helps preserve custom-element state, but form/focus/CE lifecycle harnesses are not yet green enough to ship a pinned default. Applications may experiment with a locally served Idiomorph build; Hedron does not bundle it in 0.6. |
| `response-targets` | **Deferred** | Core `HX-Retarget` / `HX-Reselect` plus `InteractionResult` status policies cover declared error/validation targets without another extension. |
| View Transitions | **Deferred** | Progressive enhancement only; requires `prefers-reduced-motion` gating and focus stability evidence reserved for later browser-matrix work. |

## Conformance notes

- Custom elements that register `htmx_lifecycle=True` must tolerate swap/settle/teardown.
- Prefer stable hosts and targeted descendant swaps; use `hx-preserve` only where identity and
  teardown are proven.
- Explorer interaction simulation reports `assets: predeclared-shell` for 0.6 routes.
