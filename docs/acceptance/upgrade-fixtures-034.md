# Upgrade fixtures — phase 0.34 (`hedron-gradio`)

Baseline: Published **`v0.34.0`**. Cut: **`v0.34.0`** / `hedron-gradio` **`0.2.0` Beta**.

## Goldens

- `tests/upgrade/goldens_0_33_0/gradio_adapter_disabled.json` — disabled adapter snapshot
- `tests/upgrade/test_0_33_to_0_34_gradio.py` — version bump and preloaded endpoint parity

## Pin migration

| Before | After |
|---|---|
| `hedron-gradio>=0.1.0,<0.2` | `hedron-gradio>=0.2.0,<0.3` |
| `hedron[gradio]>=0.34.0,<0.35` | `hedron[gradio]>=0.34.0,<0.35` at train cut |

## Behavior notes

- Remote calls now require allowlisted destinations via `GradioRemoteConfig`
- Artifact transport is bounded; job ids are scope-isolated
- Alpha instant in-memory job completion replaced with scoped job manager semantics
