# Upgrade to Hedron 0.28

This guide covers an application upgrade from **0.27.x** to the published **0.28.x**
train. New applications should use [Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.28.0 graduates `hedron-charts` and `hedron-native` to production-grade for
their declared Supported inventories (D-056 / RFC-0059). Matplotlib/static beginner
charts and optional native escape acceleration are the Supported scopes. Plotly/Altair
and optional visualization adapters remain Experimental and are not production Auto
defaults.

No Supported CRUD/admin API removal is listed. Polling remains the production
recommendation for live status. SSE, WebSocket, streaming, and navigation preload
remain experimental.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on `hedron>=0.27.0,<0.28` (or an earlier 0.27-compatible pin).
3. If you use charts, note whether you rely on Auto-selected Plotly/Altair — those
   backends now require explicit `as_=` or chart components.

## Install

```bash
python -m pip install -U "hedron>=0.28.0,<0.29"
python -m pip install -U "hedron-charts>=0.1.8,<0.2" "hedron-native>=0.1.1,<0.2"
```

## Charts Auto defaults

Production Auto no longer selects Plotly/Altair without an explicit renderer name:

```python
from hedron_core.auto import Auto

Auto(figure, as_="plotly")  # Experimental opt-in
```

Matplotlib remains the Supported Auto chart path when `hedron-charts` is installed.

## Native disable

Force the pure-Python escape path (ops / parity drills):

```bash
export HEDRON_NATIVE_DISABLE=1
```

Absence of `hedron-native` continues to fall back without semantic drift.

## After upgrading

1. Run your test suite and any HTMX/browser checks that cover chart fragments.
2. Confirm Explorer / plugin loads succeed under `0.28.0` (`hedron_version` pins).
3. Read [What’s new in 0.28](whats-new-0.28.md) and [What’s ready](whats-ready.md).

Prior 0.26→0.27 notes remain in [What’s new in 0.27](whats-new-0.27.md).
