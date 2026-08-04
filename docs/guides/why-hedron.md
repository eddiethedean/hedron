# Why Hedron

Short positioning for evaluators. Deep feature matrices live in the research
appendices linked below.

## What Hedron optimizes for

- **Python-owned UI** for FastAPI (and Supported Flask/Django adapters)
- **Typed components** with ordinary HTML/HTMX—no Node.js, no SPA runtime
- **Secure defaults**: contextual escaping, CSRF, SafeUrl, conservative caches
- **Inspectability**: inference is explainable; Explorer shows routes and findings

## Compared to nearby tools

| If you want… | Prefer | Tradeoff |
|---|---|---|
| Fastest notebook-style dashboards | Streamlit | Rerun model; less FastAPI-native routing/DI |
| Plotly-centric reactive apps | Dash | Callback graph; different security/HTML story |
| Model demos and ML UIs | Gradio | Different product shape; less CRUD/admin focus |
| Full control with templates | Jinja + HTMX by hand | You assemble CSRF, fragments, and contracts yourself |
| Typed components on FastAPI/HTMX | **Hedron** | Learning the component + fragment contracts |

Hedron is **not** an ORM, identity provider, client SPA framework, or whole-script
rerun engine.

## When Hedron is a poor fit

- You need a pure client-rendered SPA with a separate JS build
- You require every Streamlit/Dash widget on day one (see roadmap phases)
- You cannot accept `0.x` Beta pinning and upgrade notes

## Research appendices

- [Streamlit cross-check](../STREAMLIT_FEATURE_CROSSCHECK.md)
- [streamlit-extras cross-check](../STREAMLIT_EXTRAS_FEATURE_CROSSCHECK.md)
- [Plotly Dash cross-check](../PLOTLY_DASH_FEATURE_CROSSCHECK.md)
- [Gradio cross-check](../GRADIO_FEATURE_CROSSCHECK.md)

## Next

[What’s ready today](whats-ready.md) · [Quickstart](../getting-started/quickstart.md) ·
[Architecture](../ARCHITECTURE.md)
