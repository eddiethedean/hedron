# What is Alpine?

**[Alpine.js](https://alpinejs.dev) adds small, reactive interactions directly to
server-rendered HTML.**

It is useful when a browser can handle an interaction without asking the server for new
data: opening a menu, switching tabs, filtering rows already on the page, or tracking a
temporary presentation preference. Hedron uses Alpine for this **browser-local** behavior
while keeping application truth, authorization, validation, and persistence on the server.

You do **not** need prior Alpine experience to use Hedron. You also do not need Node.js,
npm, a JavaScript bundle, or a separate frontend application.

## Start with local behavior

In ordinary Alpine HTML, a disclosure can look like this:

```html
<div x-data="{ open: false }">
  <button type="button" x-on:click="open = !open">Toggle details</button>
  <div x-show="open">All systems operational</div>
</div>
```

The three directives describe the behavior:

| Directive | Meaning |
|---|---|
| `x-data` | Defines local reactive state for this element and its descendants. |
| `x-on:click` | Runs a local expression when the button is clicked. |
| `x-show` | Shows or hides an element as the state changes. |

When someone clicks the button, Alpine changes `open` in the browser and updates the
existing HTML. There is no HTTP request, server route, response fragment, or page reload.

```text
User clicks Toggle details
  -> Alpine changes local state: open = true
  -> Alpine updates the existing disclosure
  -> the server is not contacted
```

The example above shows the upstream Alpine syntax so you can recognize it in rendered
HTML. Hedron application code normally uses built-in components or typed Python
declarations instead of writing raw `x-*` attributes.

## Alpine and HTMX solve different jobs

Alpine and HTMX both enhance server-rendered HTML, but they own different work:

| Need | Use | Why |
|---|---|---|
| Open a disclosure or switch tabs | Alpine | The result uses only disposable state already in the browser. |
| Filter 20 authorized rows already rendered | Alpine | No new server data is required. |
| Search a database | HTMX | The server owns the data and returns authoritative HTML. |
| Submit and validate a form | HTMX with a native form fallback | Mutation and validation belong on the server. |
| Open a dialog, then submit its form | Alpine + HTMX | Alpine owns dialog presentation; HTMX owns the one server request. |

A useful test is: **Could losing this browser state change the correct application
result?** If yes, it is not Alpine state. Put the value on the server, in the URL, or in a
native form as appropriate.

## How Hedron expresses it in Python

The common path is to use a built-in component that already declares its local behavior.
For example, `Tabs` uses Alpine to switch between content that the server has already
rendered:

```python
from hedron import Hedron, Stack, Tabs, Text

app = Hedron(
    title="Service status",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
)


@app.page("/")
def home():
    return Stack(
        Text("Service status"),
        Tabs(
            ("Overview", Text("All systems operational")),
            ("History", Text("No incidents in the last 24 hours")),
            active="Overview",
        ),
    )
```

The server renders both labelled panels as semantic HTML. Alpine owns only the active-tab
presentation in the browser. Switching tabs makes no request and creates no second copy of
server state.

Hedron collects the component's browser-feature requirements while rendering the page. It
then includes the pinned, same-origin Alpine CSP runtime and only the required plugins. A
page with no Alpine behavior emits no Alpine assets.

## Advanced: typed local behavior

Use `AlpineAttrs` when a distinct local behavior is not represented by a built-in
component. Hedron accepts typed state and expressions through the `alpine=` attribute and
rejects raw `x-*` attributes:

```python
from hedron import AlpineAttrs, AlpineExpression, Hedron, html

app = Hedron(
    title="Local details",
    security="standard",
    explorer="off",
    session_secret="replace-in-production",
)

open_state = AlpineExpression.name("open")
toggle_open = AlpineExpression.assign(
    "open",
    AlpineExpression.binary(
        "===",
        open_state,
        AlpineExpression.literal(False),
    ),
)
button_behavior = AlpineAttrs.on("click", toggle_open).merge(
    AlpineAttrs.bind("aria-expanded", open_state)
)


@app.page("/")
def home():
    return html.div(
        html.button(
            "Toggle details",
            type="button",
            aria={"controls": "service-details", "expanded": "false"},
            alpine=button_behavior,
        ),
        html.div(
            "All systems operational",
            id="service-details",
            alpine=AlpineAttrs.show(open_state),
        ),
        alpine=AlpineAttrs.data({"open": False}),
    )
```

This renders the same `x-data`, `x-on:click`, `x-bind:aria-expanded`, and `x-show`
concepts, but the values pass through Hedron's typed, CSP-safe validation. Initial state
must be JSON-compatible, directives use their normalized long-form names, and unsafe
expression globals and sinks fail closed.

!!! note "Fragments and browser feature plans"

    An ordinary page plan includes features found while rendering that page. If a later
    HTMX fragment can introduce a new Alpine feature that was not present initially,
    declare the page's reachable fragment closure in advance. A response cannot install a
    new runtime or plugin after the document has loaded.

## The ownership boundary

Alpine owns ephemeral component state and local presentation inside its root. It must not:

- call `fetch()`, `XMLHttpRequest`, or `htmx.ajax()` as another application request path;
- decide whether a user is authorized or whether server data is valid;
- store secrets, permissions, canonical records, payment state, or durable job results;
- rewrite HTMX methods, URLs, targets, swaps, or fallback policy at runtime;
- reconstruct an authoritative server response from JSON; or
- independently write a DOM property already owned by HTMX or a specialist Web Component.

Hedron's short rule is: **Alpine owns disposable local behavior; HTMX owns declared server
communication and HTML replacement; the server owns application truth.**

## What Alpine does—and does not do

Alpine provides reactive local state, event handling, bindings, and small DOM projections.
It is not:

- a server, Python package, database, or authorization boundary;
- a replacement for HTMX when an interaction needs server data;
- a second routing, validation, or persistence layer;
- a requirement for every page—native HTML remains the first choice where it is enough;
- the owner of specialist subsystems such as charts, maps, or data editors, which keep their
  bounded Web Component APIs.

Alpine state is replaceable. Ordinary HTMX replacement resets it unless a bounded
preservation contract says otherwise. Losing local state must never corrupt domain data or
change authorization.

## Common questions

### Is Alpine a Python dependency?

No. Alpine is a JavaScript library that runs in the browser. Hedron bundles Alpine's CSP
build **3.16.3** and serves it from same-origin `/hedron-static/` paths when the rendered
page requires it. Do not add a CDN script or npm package to a standard Hedron application.

### Does Alpine make a request when state changes?

No. A local Alpine interaction changes browser state and presentation only. If the intent
needs new data, mutation, or authoritative validation, use a declared HTMX/server
interaction instead.

### What happens when HTMX replaces an Alpine component?

Hedron's lifecycle coordinator cleans up the outgoing Alpine root, lets HTMX perform the
declared swap, and initializes the new root once. Local state resets by default, while the
server response remains authoritative.

### How do I debug local behavior?

Open the browser developer tools and inspect **Elements**. Find the nearest `x-data` root,
then check its `x-on:*`, `x-show`, `x-model`, or `x-bind:*` directives. A purely local
interaction should not create a request in **Network**.

## Continue learning

1. [What is HTMX?](what-is-htmx.md) — learn the request, target, fragment, and swap model.
2. [`Tabs`](../components/tabs.md) — use a built-in browser-local component.
3. [HTMX/Alpine boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md) — read the normative ownership, lifecycle, security, and failure contract.
4. [Interaction API](../api/INTERACTION.md) — declare local, request, and combined interactions.

If you have not scaffolded yet, start with [Build your first app](quickstart.md).
