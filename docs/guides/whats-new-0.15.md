# What’s new in 0.15

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and published 1.0 status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

Phase **0.15** completes the high-value data-app surface — controls, media, maps,
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

Pin `hedron>=0.15.0,<0.16` when staying on the 0.15 line.

Runnable phase exit sample:
[`examples/data-app-0.15`](https://github.com/eddiethedean/hedron/tree/main/examples/data-app-0.15)
(quarantined as version-stamped maintainer evidence, not a product tutorial).
