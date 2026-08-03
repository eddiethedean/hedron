# Chart APIs

**Status:** Accepted

```python
LineChart(
    data,
    x="month",
    y="revenue",
    title="Monthly revenue",
    description="Revenue increased during the period.",
)

PlotlyChart(figure, description="Revenue by region")
MatplotlibChart(figure, alt="Revenue by month")
```

Beginner charts expose backend-neutral contracts for common plots. Familiar-library components accept upstream objects without hiding the chosen backend.

Every chart declares title, description or alt text, output mode, data policy, and optional tabular fallback. Interactive adapters register browser assets once and serialize specifications as non-executable data. Raw JavaScript callbacks and unapproved remote assets are rejected by default.

Adapters implement a public `VisualizationAdapter` capability contract but may keep backend compilation types internal. Missing optional dependencies produce a precise installation command. Payload limits and server-transform policies are explicit and visible in Explorer.

Hedron does not promise that changing the configured beginner backend produces pixel-identical charts; it promises stable input semantics, accessibility requirements, security policy, and lifecycle behavior.

