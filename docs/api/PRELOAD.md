---
status: experimental
---

# Navigation preload


!!! note "Stability"

    Classifications live in [STABILITY.md](STABILITY.md). Opt-in navigation preload is
    **experimental** (`hedron.experimental`) under Accepted 0.24 **`polling_only`**
    ([LIVE_DISPOSITION](LIVE_DISPOSITION.md)); default remains off.

**Status:** Shipped in `0.10.0` (experimental)

Types: `NavigationPreloadPolicy`, `HX_PRELOADED` (header name). Helpers:
`evaluate_preload_request`, `apply_preload_headers` — import from `hedron.experimental`.
Decision logic lives in `hedron_core.preload`.

## `NavigationPreloadPolicy`

Construct with `enabled=True` before any speculative work. Fields:

| Field | Default | Description |
|---|---|---|
| `enabled` | `False` | Master switch |
| `max_concurrent` | `2` | Concurrent preload cap |
| `max_per_navigation` | `4` | Speculative requests per navigation |
| `only_same_origin` | `True` | Reject cross-origin |
| `respect_private_cache` | `True` | Honor private cache directives |
| `cancel_on_navigation` | `True` | Cancel when navigation changes |

## `evaluate_preload_request(request, policy, …)`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `request` | Starlette `Request` | required | Incoming request |
| `policy` | `NavigationPreloadPolicy` | required | Explicit policy |
| `speculative_count` | `int` | `0` | Speculative requests already in flight |
| `concurrent` | `int` | `0` | Concurrent preload count |
| `navigation_cancelled` | `bool` | `False` | Cancel outstanding preload |

Returns a `PreloadDecision` (`allowed`, `header_value`, `cache_control`, …).

## `apply_preload_headers(response, decision, …)`

Writes `HX-Preloaded` (via `HX_PRELOADED`), optional `Cache-Control`, and
`X-Hedron-Preload-Cancel` when the decision requires it.

## Errors / rejection

When the policy denies preload, `decision.allowed` is false and no preload header is set.
Cross-origin requests fail closed relative to the request host.

## See also

[Live interaction guide](../guides/live-interaction.md) · [Upgrade](../guides/upgrade.md)
