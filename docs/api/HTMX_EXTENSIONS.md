---
status: mixed
---

# HTMX extension integration

Phase 0.48 (D-080 / D-083 / RFC-0075) makes HTMX extensions a declared Hedron
capability. Pages and components name what they need; rendering injects
only pinned local assets, emits `hx-ext`, and exposes the same facts to CSP,
manifests, adapters, and tests. SSE and preload **helpers** remain experimental
under `polling_only`; declared extension **assets** are Supported when pinned.

## Declaration

Closed public ids: `hedron`, `sse`, `head-support`, `preload`, and conditionally
`morph`. Asset files stay named `htmx-ext-*`. `hx-ext` uses the public id.

```python
from hedron_core.builtins import Page

Page(content, htmx_extensions={"sse", "preload"})
```

Unset `htmx_extensions` keeps the 0.47 PAGE default (pinned `sse` and
`head-support` after HTMX core) with a compatibility diagnostic. Empty
`htmx_extensions=()` opts out. Non-empty declarations are demand-driven
only; `preload` and `morph` never ride the default.

`HtmxExtension` / `ExtensionSet` live in `hedron-core`. HDJ continues to
use `ExtensionEvidence`; writing `hx-ext` alone never installs an
extension.

## SSE

`SseRegion` and `SseTrigger` wrap existing `SseEvent` /
`job_status_sse_response` helpers. `sse-connect` is a validated
same-origin URL. Event names are closed tokens. Polling remains the
Supported fallback. SSE APIs stay experimental.

## Head-support

Registered pages may merge a controlled `<head>` from admitted `AssetRef`
values. Fragment responses still never invent executable assets.

## Preload

Preload is a GET-only authoring value on links and `hx-get` controls, with
closed initiation modes `mousedown`, `mouseover`, and `touchstart`. It maps
to the existing `HX-Preloaded` / `decide_preload` path. It is not a type
named `Preload` (that name is `PreloadDecision`). Preload never changes
authorization, CSRF, cache partitioning, or availability.

## Morph

Idiomorph ships only if `MORPH-048` verifies form, focus, custom-element,
chart, map, OOB, accessibility, and three-engine lifecycle evidence.
Otherwise it is explicitly Deferred or excluded. `safe_hx_swap` does not
admit morph today.

## Compatibility

- HTMX 2 (`>=2,<3`) only.
- `InteractionResult`, `HX-Retarget`, OOB, indicators, and polling stay
  authoritative.
- `response-targets`, multi-swap, loading-states, CDN extensions, and the
  HTMX WebSocket extension are not in the 0.48 inventory.
