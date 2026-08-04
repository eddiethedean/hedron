# Why Hedron

Short positioning for evaluators. Deep feature matrices live in the research
appendices linked from the [maintainer docs](maintainers.md).

## What Hedron optimizes for

- **Python-owned UI** for FastAPI (and Supported Flask/Django adapters)
- **Typed components** with ordinary HTML/HTMX—no Node.js, no SPA runtime
- **Secure defaults**: contextual escaping, CSRF, SafeUrl, conservative caches
- **Inspectability**: automatic choices are visible in Explorer, CLI, and diagnostics

## Compared to nearby tools

| If you want… | Prefer | Tradeoff |
|---|---|---|
| Fastest notebook-style dashboards | Streamlit | Rerun model; less FastAPI-native routing/DI |
| Plotly-centric reactive apps | Dash | Callback graph; different security/HTML story |
| Model demos and ML UIs | Gradio | Different product shape; less CRUD/admin focus |
| Full control with templates | Jinja + HTMX by hand | You assemble CSRF, fragments, and contracts yourself |
| Event-loop UI widgets in pure Python | NiceGUI | Different interaction model; less HTMX/fragment-first |
| Full-stack Python with a React compiler | Reflex | Generates a JS client stack; Hedron stays server-rendered HTML |
| Typed components on FastAPI/HTMX | **Hedron** | Learning the component + fragment contracts |

Hedron is **not** an ORM, identity provider, client SPA framework, or whole-script
rerun engine. It is closer to “FastAPI + HTMX with typed components” than to
Streamlit’s script-rerun model—`Auto` and data extras cover common object display,
not every Streamlit widget.

## When Hedron is a poor fit

- You need a pure client-rendered SPA with a separate JS build
- You require every Streamlit/Dash widget on day one (see [public roadmap](roadmap.md))
- You cannot accept `0.x` Beta pinning and upgrade notes

## Next

[What’s ready today](whats-ready.md) · [Quickstart](../getting-started/quickstart.md) ·
[Architecture](../ARCHITECTURE.md)
