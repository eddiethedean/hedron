---
description: Explain Hedron's FastAPI request model to teams familiar with Streamlit.
search:
  boost: 1.5
---

# How Hedron works

Hedron adds Python components and HTML responses to FastAPI. A registered route
handles each interaction. The route receives validated input, calls application
code, and returns a page, a replacement fragment, or an ordinary response.

The request path has three steps:

1. The browser requests a page, view, or action by URL.
2. FastAPI parses the input. The Hedron route calls the application's Python
   services and data sources.
3. The route returns a full HTML page, a fragment for a declared region, or an
   ordinary response. The browser displays the result.

FastAPI still provides dependency injection, middleware, JSON routes, and
OpenAPI. `hedron-core` renders the component tree and escapes HTML. Rendering a
component does not publish a route; `@app.page`, `@app.view`, and `@app.action`
register the HTTP boundaries.

## A page and an independently refreshed view

```python
from hedron import Hedron, Stack, Text

app = Hedron(title="Operations", security="standard")


@app.view("/status")
def status():
    return Text("All systems operational")


@app.page("/")
def home():
    return Stack(
        Text("Operations"),
        status(),
        status.refresh_button("Refresh status"),
    )
```

The first visit to `/` receives a full page. Selecting **Refresh status** sends
a request to `/status` and replaces that view's declared region. A write uses
an explicit action, normally a POST with authorization and CSRF protection;
the [minimal form guide](../../guides/minimal-form.md) shows that next step.

## The Streamlit comparison

- **Interaction:** A Streamlit widget change reruns the script by default.
  Hedron's browser requests one page, view, or action route.
- **Input:** Streamlit widget values participate in script execution.
  FastAPI parses validated query, form, or body input for a Hedron route.
- **Output:** Streamlit rebuilds the visible UI from script output. Hedron
  returns a full HTML page, a fragment, or a redirect.
- **Writes:** Both applications must decide data ownership and access. Hedron
  makes a write an explicit action route backed by application services.

Streamlit also has [forms](https://docs.streamlit.io/develop/concepts/architecture/forms)
that batch input and [fragments](https://docs.streamlit.io/develop/concepts/architecture/fragments)
that rerun part of an app. Hedron's distinction is the explicit HTTP request and
response contract. See Streamlit's [execution flow](https://docs.streamlit.io/develop/api-reference/execution-flow)
and Hedron's [migration guide](../../guides/streamlit-migration.md) for the
detailed comparison.

## Give each kind of state an owner

- **Shareable filters and navigation:** Path or query parameters.
- **One submitted operation:** Validated request input.
- **Small temporary workflow values:** Session state.
- **Durable records and permissions:** Database or application service.
- **Long-running work:** Job backend with a status route.

Keep existing Python queries, calculations, and models where they make sense.
Hedron's data, chart, and map packages can present results, while FastAPI can
serve JSON endpoints beside the HTML interface. Check the
[Streamlit component matrix](../../guides/streamlit-migration-matrix.md) for any
specialized widget before assuming a direct replacement.

Next: [Develop in Workbench and publish on Connect](workbench-connect.md).
