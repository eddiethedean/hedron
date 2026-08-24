# Phase 0.63 visualization presentation contract

`resolve_visualization_theme()` is the shared semantic palette for SVG,
client-side chart elements, print output, and tabular fallbacks. It resolves
series, axis, grid, label, selection, focus, surface, and tooltip roles from a
`Theme`, while every series also receives a pattern and marker.

The `forced-colors` mode uses system colors but retains non-color encodings;
the `print` mode uses ink-safe values. Reduced transparency removes decorative
backdrop treatment. Consumers should read the role contract rather than
reimplementing theme or accessibility decisions in individual adapters.

The chart compiler emits the same `chart.*` role tokens into its `ChartPlan`,
so exported SVG and semantic/table fallbacks share the resolved values.
