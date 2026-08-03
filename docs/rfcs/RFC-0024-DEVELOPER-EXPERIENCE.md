# RFC-0024: Developer experience

**Status:** Accepted

## Learning ladder

1. Use built-in components and `Auto()`.
2. Configure props, variants, layout, actions, and slots.
3. Compose reusable Python components.
4. Inspect or eject HDN and scoped styles.
5. Add Web Components, integrations, and plugins.

The first tutorial includes no AST, compiler, Rust, portable specification, or mandatory HDN. Errors identify the component, source, invalid value category, and next action without leaking sensitive values.

## Intelligent rendering

`Auto(value)` uses a deterministic renderer registry for Hedron components, dataframe-like objects, chart objects, Markdown, images, mappings, and sequences. The Data Intelligence Layer may analyze schema, size, cardinality, datetime and geospatial columns, but automatic selection follows explicit application policy and is explainable.

Beginner components include forms, tables, editor, metrics, uploads, downloads, code and JSON viewers, progress, status, toast, expander, tabs, sidebar, and explicit grid layouts. Hedron adopts Streamlit’s friction reduction, not its rerun or global-state model.

## Acceptance criteria

- Common Python objects render without manual serialization.
- Ambiguous matches have deterministic precedence and an explicit override.
- Onboarding usability and error-message quality are tested with documented tasks.

