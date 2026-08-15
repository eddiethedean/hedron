# Why Hedron

Short positioning for evaluators.

## What Hedron optimizes for

- **Typed components on FastAPI** (Flask/Django adapters available) with HTMX fragments
- **Secure defaults**: contextual escaping, CSRF profiles, SafeUrl, conservative caches
- **Contracts you would otherwise assemble**: fragment regions, interaction results, job polling
- **Inspectability**: Explorer, CLI, and diagnostics for automatic choices

## Concrete contrast: Streamlit vs Hedron

By default, Streamlit reruns the script on widget interaction; forms batch inputs and
`st.fragment` can rerun a portion. Hedron keeps FastAPI routing: each interaction is an
explicit HTTP request, and it may swap a **typed HTML fragment** into a declared region
(the Hello “Refresh status” demo).

=== "Streamlit"

    ```python
    import streamlit as st

    st.write("Hello")
    if st.button("Refresh"):
        st.write("updated")  # full script rerun
    ```

=== "Hedron"

    ```python
    from datetime import UTC, datetime
    from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

    app = Hedron(title="Demo", security="standard", session_secret="dev", explorer="off")
    status = app.region("status")


    def panel():
        stamp = datetime.now(UTC).strftime("%H:%M:%S")
        return html.div(Text(f"ok · {stamp}"), id=status.id)


    @app.page("/")
    def home() -> Page:
        return Page(
            Stack(Text("Hello"), panel(), RefreshButton.for_region(status, href="/status")),
            title="Demo",
        )


    @app.fragment("/status", region=status)
    def refresh():
        return swap(panel())  # HTMX swaps only this region
    ```

Hedron keeps FastAPI dependency injection, OpenAPI, and CSRF-ready forms.
Streamlit optimizes for the fastest notebook-style dashboard loop.

Forms and CSRF are a short next step after Hello — see
[HTMX interactions](htmx-interactions.md) then [Minimal form POST](minimal-form.md).
Streamlit users should start with the [migration center](streamlit-migration.md).

## Compared to nearby tools

| If you want… | Prefer | Tradeoff |
|---|---|---|
| Fastest notebook-style dashboards | Streamlit | Rerun model; less FastAPI-native routing/DI |
| Minimal HTML/HTMX apps with little framework | FastHTML | Fewer typed-component / CSRF / fragment contracts out of the box |
| Plotly-centric reactive apps | Dash | Callback graph; different security/HTML story |
| Model demos and ML UIs | Gradio | Different product shape; less CRUD/admin focus |
| Full control with templates | Jinja + HTMX by hand | **You** own CSRF, fragment allowlists, interaction headers, and contracts |
| Event-loop UI widgets in pure Python | NiceGUI | Different interaction model; less HTMX/fragment-first / FastAPI-native |
| Full-stack Python with a React compiler | Reflex | Generates a JS client stack; Hedron stays server-rendered HTML |
| Typed components + HTMX on FastAPI | **Hedron** | Learning the component + fragment contracts |

### What hand-rolled FastAPI+HTMX still means you maintain

Without Hedron you typically wire CSRF cookies/headers, HTMX target allowlists, fragment
vs page response modes, and secure HTML escaping yourself. Hedron ships those as
inspectable contracts — see [Plain FastAPI](plain-fastapi.md) when you already own the app.

Hedron is **not** an ORM, identity provider, client SPA framework, or whole-script
rerun engine. `Auto` and data extras cover common object display, not every Streamlit widget.

## When Hedron is a poor fit

- You need a pure client-rendered SPA with a separate JS build
- You require every Streamlit/Dash widget on day one (see [roadmap](roadmap.md))
- You cannot accept `0.x` Beta pinning and upgrade notes
- You only need notebook-style reruns and do not want FastAPI routing

## Next

[Evaluate Hedron](evaluate.md) · [What’s ready today](whats-ready.md) ·
[Streamlit migration](streamlit-migration.md) · [Quickstart](../getting-started/quickstart.md) ·
[Architecture](../ARCHITECTURE.md)
