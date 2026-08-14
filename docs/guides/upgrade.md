# Upgrade to Hedron 0.38

This guide covers an application upgrade onto the **0.39.x** train
(current tip **`v0.39.0`**). New applications should use
[Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.39.x ships first-party high-fidelity charts (D-066 / RFC-0069): typed
`ChartSpec` / `ChartPlan`, ABI-conforming `hedron-chart` (SVG default, Canvas for
dense marks), and beginner `LineChart` / `AreaChart` / `BarChart` / `ScatterChart`
compiled to the same grammar. Install with `hedron[charts]` or
`hedron-charts>=0.2.0,<0.3`. Matplotlib remains Supported; Plotly/Altair stay
Experimental.

Prior trains remain in force: Alpha `hedron-elements` form/primitives (0.37),
Web Component ABI (0.36), MCP (`hedron-mcp` `0.2.x`), Workbench ASGI
(`fastapi-workbench` `1.x`), and Posit (`hedron[posit]` / `HedronPosit`). Polling
remains the production recommendation for live status. SSE, WebSocket, streaming,
and navigation preload remain experimental.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on a recent pin (`hedron>=0.29.0,<0.30` through `>=0.37.0,<0.38`,
   or the tip pin already).
3. If you use charts, plan to install `hedron[charts]>=0.39.0,<0.40` (or
   `hedron-charts>=0.2.0,<0.3`).
4. If you use Posit Workbench or Connect, prefer `hedron[posit]` / `HedronPosit`.
5. Optional: keep `hedron[elements]` for Alpha form-associated hosts from 0.37.

## Install

```bash
python -m pip install -U "hedron>=0.39.0,<0.40"
python -m pip install -U "hedron[charts]>=0.39.0,<0.40"
# independent charts satellite:
python -m pip install -U "hedron-charts>=0.2.0,<0.3"
# optional Alpha elements:
python -m pip install -U "hedron[elements]>=0.39.0,<0.40"
# Posit / Workbench:
python -m pip install -U "hedron[posit]>=0.39.0,<0.40"
```

## 0.37 → 0.38 notes

- Beginner chart call shapes stay the same; they now compile to `ChartSpec` and
  render `hedron-chart`.
- First-party interactive charts no longer depend on vendor JSON as the Supported
  interactive path. Plotly/Altair remain explicit Experimental adapters.
- Scoped keyboard/AT evidence for charts is verified for engineering honesty; do
  **not** market Supported human AT (`SR-021` remains Planned).

## See also

[Release notes](release-notes.md) · [What’s new in 0.38](whats-new-0.38.md) ·
[What’s ready](whats-ready.md) · [Chart API](../api/CHART.md) ·
[COMPATIBILITY](../COMPATIBILITY.md) · [RELEASE_0_38](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_38.md)
