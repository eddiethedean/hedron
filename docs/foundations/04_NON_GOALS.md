# Non-goals

Hedron is not:

- a client-rendered SPA runtime or universal replacement for React;
- a virtual DOM, hydration system, or client-side state manager;
- a proprietary transport that replaces HTML and HTTP;
- an ORM, transaction manager, database migration system, or query language;
- an authentication provider, authorization policy engine, or session implementation;
- a chart grammar or replacement for Plotly, Altair, Matplotlib, or ECharts;
- an HTML sanitizer, cryptographic library, durable job queue, or distributed cache;
- a JavaScript build tool or reason to require Node.js;
- a Streamlit-style whole-script rerun engine;
- a visual application builder in the initial product;
- a guarantee that arbitrary React applications can be transpiled to a Hedron declarative format;
- ownership of a custom template language without demonstrated advantage over typed Python or an
  established optional engine;
- a cross-language *application* runtime that replaces Python as the Supported flagship (experimental
  Java/Node conformance runtimes may participate under D-048 without fragmenting contracts);
- a Rust-first project; optional native acceleration requires profiling evidence (D-048);
- a framework that silently exposes components, grants permissions, trusts markup, or persists data;
- a wrapper that hides FastAPI, HTMX, HTML, CSS, or browser behavior from developers.

## Explicitly deferred

The following remain optional or later-phase: route-level CSS splitting, collaborative DataEditor,
visual builders, evidence-backed declarative-authoring migration assistance, and WASM/Pyodide
sandbox work (phase 0.16). Language-neutral conformance, experimental Java/Node runtimes, and
optional Rust acceleration shipped in **0.14** under D-048.

Live transport on the FastAPI flagship (official HTMX SSE, focused streaming, page/session
WebSocket channels, and related contracts) shipped in **0.10** — see
[live interaction](../guides/live-interaction.md). Official HTMX SSE on Flask/Django remains
Deferred (polling is the Supported fallback).
