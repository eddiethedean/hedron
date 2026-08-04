# Why Hedron

Short positioning for evaluators.

## What Hedron optimizes for

- **Python-owned UI** for FastAPI (and Supported Flask/Django adapters)
- **Typed components** with ordinary HTML/HTMX—no Node.js, no SPA runtime
- **Secure defaults**: contextual escaping, CSRF, SafeUrl, conservative caches
- **Inspectability**: automatic choices are visible in Explorer, CLI, and diagnostics

## Concrete contrast: Streamlit vs Hedron

Streamlit re-runs the script; Hedron returns typed components from FastAPI routes.

=== "Streamlit"

    ```python
    import streamlit as st

    name = st.text_input("Name")
    if st.button("Save"):
        st.write(f"Saved {name}")
    ```

=== "Hedron"

    ```python
    from fastapi import Form, Request
    from hedron import Hedron, Page, Stack, SubmitButton, Text, TextInput, html
    from hedron.security import csrf_token_for_request

    app = Hedron(title="Demo", security="standard", session_secret="replace-in-production")


    @app.page("/")
    def home(request: Request) -> Page:
        token = csrf_token_for_request(request, request.app.state.hedron_security)
        return Page(
            Stack(
                html.form(
                    html.input(type="hidden", name="csrf_token", value=token),
                    TextInput("name", value=""),
                    SubmitButton("Save"),
                    action="/save",
                    method="post",
                )
            ),
            title="Demo",
        )
    ```

Hedron keeps FastAPI routing, dependency injection, CSRF, and HTMX fragments. Streamlit
optimizes for the fastest notebook-style dashboard loop.

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
