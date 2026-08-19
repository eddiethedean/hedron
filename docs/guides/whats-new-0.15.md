# What’s new in 0.15

Phase **0.15** completes the high-value data-app surface — typed controls, media, maps,
browser context, and scenario testing — without Streamlit-style whole-script reruns.

## Highlights

- **AppScenario harness** (`hedron.testing.app`) for navigate / submit / fragment assert flows.
- **HTMX InteractionResult asserts** for redirects, push URL, retarget/reswap, OOB, Toast.
- **Maps / GeoJSON** — first-party map and layer components (RFC-0033).
- **Media delivery** — download and range-friendly media helpers (RFC-0034).
- **Surface chrome** — AppShell-adjacent layout patterns (RFC-0035).
- **Scenario marks** and richer testing helpers (RFC-0036).
- **Interaction ergonomics** — `region` / `@fragment` / `swap` authoring (RFC-0039).

## Upgrade notes

!!! note "Historical phase"

    This page describes **0.15**. The current published train is **0.50.x** (last `v0.50.1`) —
    see [What’s new in 0.28](whats-new-0.28.md) and the [upgrade guide](upgrade.md).

Pin `hedron>=0.15.0,<0.16` when staying on the 0.15 line.

Runnable phase exit sample:
[`examples/data-app-0.15`](https://github.com/eddiethedean/hedron/tree/main/examples/data-app-0.15)
(quarantined as version-stamped maintainer evidence, not a product tutorial).
