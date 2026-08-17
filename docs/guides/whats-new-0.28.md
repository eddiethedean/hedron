# What’s new in 0.28

!!! note "Current train is 0.48"

    Pin `hedron>=0.48.0,<0.49` for new apps. The pin below is historical for the 0.28 train only.
    See [What’s new in 0.41](whats-new-0.41.md).

**Published** as `v0.28.2`. Historical pin: `hedron>=0.28.2,<0.29`.

Phase **0.28** (D-056 / RFC-0059) graduates `hedron-charts` and `hedron-native` to
**production-grade for their declared Supported inventories**.

## Highlights

- **Charts (Beta `0.1.11` tip; floor `>=0.1.10`):** Matplotlib/static beginner Line/Bar/Area/Scatter charts are
  production-grade with a11y alternatives, CSP-safe local assets, payload budgets, and
  browser/print evidence.
- **Interactive quarantine:** Plotly/Altair and optional adapters remain **Experimental**
  and are excluded from production Auto defaults (`as_=` opt-in).
- **Native (Beta `0.1.2`):** Optional Rust escape acceleration with Supported wheel tags
  built by `native-wheels.yml` (confirm Supported tags on PyPI), `HEDRON_NATIVE_DISABLE`,
  and Python-reference fallback parity.

## Upgrade

From `0.27.x`:

```bash
python -m pip install -U "hedron>=0.28.2,<0.29"
python -m pip install -U "hedron-charts>=0.2.0,<0.3" "hedron-native>=0.1.2,<0.2"
```

Details: [RELEASE_0_28](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_28.md) · [upgrade guide](upgrade.md).
