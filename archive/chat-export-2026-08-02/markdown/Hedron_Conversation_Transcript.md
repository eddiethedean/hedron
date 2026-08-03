# Hedron conversation transcript

Complete transcript of the ChatGPT conversation "HTMX Component Composition," captured from the Hedron project on 2026-08-02.

---

## 1. You

I’m really excited to use htmx as a react replacement because my work environment does not have node.js. I miss the way you build components though.

## 2. ChatGPT

I actually think you're in a really interesting position. Given what you've told me about your work environment (Python/FastAPI, no Node.js, government environment), I think HTMX + Web Components is a stronger long-term architecture than trying to force React into that environment. The missing piece is exactly what you noticed: component composition.

React didn't become popular because of JSX. It became popular because components are a fantastic abstraction.

The good news is that HTMX doesn't prevent components. It just doesn't provide them.

For example, instead of React:

JavaScript
<Card title="Users">
    <Button>Save</Button>
</Card>

you can have server-side components.

Python
Run
# components/card.py

def Card(title: str, body: str):
    return f"""
    <div class="card">
        <h2>{title}</h2>
        <div>{body}</div>
    </div>
    """
Python
Run
page = Card(
    title="Users",
    body=Button("Save")
)

Now your FastAPI app is assembling HTML exactly like React assembles JSX.

Or, even better, use Jinja2 macros.

jinja
{% macro card(title) %}
<div class="card">
    <h2>{{ title }}</h2>

    {{ caller() }}

</div>
{% endmacro %}

Then

jinja
{% call card("Users") %}

{{ button("Save") }}

{% endcall %}

That's surprisingly close to React components.

Where I think there is a huge opportunity—and this gets me excited because it aligns with a lot of the libraries you've been building—is to create something that sits above HTMX.

Imagine this:

Python
Run
from hypercomponents import *

page = Page(

    Navbar(),

    Sidebar(),

    Main(

        Card(
            title="Users",

            Table(df),

            Button(
                "Refresh",
                hx_get="/users",
                hx_target="#table"
            )
        )
    )
)

No templating.

No JavaScript.

No Node.

Just Python objects that render to HTML.

Under the hood:

FastAPI

HTMX

Alpine.js (optional)

Web Components (optional)

Tailwind or PicoCSS

You could even make the API look suspiciously like React.

Python
Run
Button(
    "Delete",
    on_click=DeleteUser(id)
)

becomes

HTML
<button
    hx-delete="/users/5"
    hx-target="#table"
    hx-swap="outerHTML">

The developer never writes HTMX attributes manually.

I've actually been thinking about this in the context of your ecosystem. You already gravitate toward strongly typed, Python-first developer experiences:

Pydantic models instead of handwritten schemas.

SQLRules instead of raw SQL predicates.

RowGuard instead of manually validating query results.

LessonKit emphasizing declarative authoring.

A Python-first UI framework would fit that philosophy naturally.

Imagine a package like:

Python
Run
pip install hyperui

Then:

Python
Run
from hyperui import *

app = FastAPI()

@app.get("/")
def home():

    return Page(

        H1("Dashboard"),

        Grid(

            Card(
                title="Users",
                children=[
                    DataTable(users)
                ]
            ),

            Card(
                title="Jobs",
                children=[
                    JobList()
                ]
            )
        )
    )

No Node.js.

No npm.

No webpack.

No JSX.

No build step.

Just Python.

I think the final evolution would be to use Web Components for the truly interactive pieces. HTMX is excellent for server-driven updates, but components like data grids, charts, tree views, ontology editors, and code editors are naturally stateful. Wrapping those as Web Components lets HTMX orchestrate them while keeping the rest of the UI simple.

For something like OntoCode, I would probably build it this way:

FastAPI: routing and backend APIs.

HTMX: page navigation, dialogs, forms, CRUD operations, and server-rendered fragments.

Web Components: ontology graph, class tree, Monaco editor, property grid, drag-and-drop canvas, and other rich widgets.

Python component library: the layer developers actually write against.

That gives you React-style composition without requiring React or a Node.js toolchain.

I think there's room in the Python ecosystem for exactly this kind of framework. The current options each have tradeoffs:

Jinja2 is powerful but template-oriented rather than component-oriented.

NiceGUI is Pythonic but tightly coupled to its own runtime and Vue.

Reflex still depends on Node during development/builds.

HTMX intentionally avoids prescribing a component model.

A Python-native component library that generates semantic HTML and HTMX attributes could fill that gap very nicely, especially in enterprise and government environments where JavaScript tooling is restricted. Given your work constraints and the kinds of projects you build, it seems like a particularly good fit.

## 3. You

How do we integrate web components into this?

## 4. ChatGPT

The clean pattern is:

HTMX owns server-driven page updates. Web Components own rich client-side behavior inside those fragments.

That means you do not use Web Components to replace HTMX. You use them for the pieces that are awkward to express as plain HTML:

data grids

charts

tree views

autocomplete inputs

date pickers

modals

drag-and-drop

ontology graphs

code editors

1. Start with a normal custom element
HTML
<user-table
    data-url="/api/users"
    page-size="25">
</user-table>

Then define it in a regular JavaScript file:

JavaScript
class UserTable extends HTMLElement {
    connectedCallback() {
        this.render();
    }

    async render() {
        const url = this.getAttribute("data-url");
        const response = await fetch(url);
        const users = await response.json();

        this.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${user.name}</td>
                            <td>${user.email}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    }
}

customElements.define("user-table", UserTable);

Load it directly in the browser:

HTML
<script type="module" src="/static/components/user-table.js"></script>

No Node.js is required. The browser executes ES modules natively.

2. Let HTMX insert Web Components

Your FastAPI endpoint can return:

HTML
<section id="users-panel">
    <h2>Users</h2>

    <user-table
        data-url="/api/users"
        page-size="25">
    </user-table>
</section>

And HTMX can load it:

HTML
<button
    hx-get="/fragments/users"
    hx-target="#workspace"
    hx-swap="innerHTML">
    Open Users
</button>

<div id="workspace"></div>

When HTMX inserts <user-table>, the browser automatically recognizes the custom element and calls its connectedCallback().

You generally do not need a special HTMX initialization hook.

3. Prefer attributes for simple configuration

Your Python component layer could generate:

Python
Run
UserTable(
    data_url="/api/users",
    page_size=25,
    selectable=True,
)

Which renders:

HTML
<user-table
    data-url="/api/users"
    page-size="25"
    selectable>
</user-table>

Then JavaScript reads the attributes:

JavaScript
get pageSize() {
    return Number(this.getAttribute("page-size") ?? 25);
}

get selectable() {
    return this.hasAttribute("selectable");
}

Attributes work well for:

strings

numbers

booleans

URLs

element IDs

configuration names

Avoid placing large JSON objects directly into attributes.

4. Use properties for complex data

For more complex data, configure the element through a JavaScript property:

HTML
<ontology-tree id="ontology-tree"></ontology-tree>

<script type="module">
    const tree = document.querySelector("#ontology-tree");

    tree.nodes = [
        { id: "Animal", children: ["Mammal", "Bird"] },
        { id: "Mammal", children: ["Dog", "Cat"] }
    ];
</script>

A component can define a setter:

JavaScript
class OntologyTree extends HTMLElement {
    set nodes(value) {
        this._nodes = value;
        this.render();
    }

    get nodes() {
        return this._nodes ?? [];
    }
}

For HTMX applications, though, I would usually pass an API URL instead:

HTML
<ontology-tree
    data-url="/ontologies/123/tree">
</ontology-tree>

That keeps large payloads out of the HTML.

5. Let components emit browser events

Web Components should communicate outward through standard custom events:

JavaScript
this.dispatchEvent(new CustomEvent("user-selected", {
    bubbles: true,
    detail: {
        userId: user.id
    }
}));

The parent page can listen:

JavaScript
document.addEventListener("user-selected", event => {
    console.log(event.detail.userId);
});

More importantly, HTMX can respond to the event.

HTML
<div
    hx-get="/users/details"
    hx-trigger="user-selected from:body"
    hx-target="#user-details">
</div>

However, HTMX cannot automatically place event.detail.userId into the request without some assistance. A useful pattern is for the component to update a hidden input before emitting the event:

HTML
<input type="hidden" id="selected-user-id" name="user_id">

<div
    hx-get="/users/details"
    hx-trigger="user-selected from:body"
    hx-include="#selected-user-id"
    hx-target="#user-details">
</div>

Component:

JavaScript
selectUser(userId) {
    document.querySelector("#selected-user-id").value = userId;

    this.dispatchEvent(new CustomEvent("user-selected", {
        bubbles: true,
        detail: { userId }
    }));
}

Now the Web Component handles interaction, while HTMX performs the server request and DOM swap.

6. Web Components can contain HTMX markup

A custom element may render normal HTMX-enabled HTML:

JavaScript
this.innerHTML = `
    <button
        hx-delete="/users/${userId}"
        hx-target="#users-panel"
        hx-swap="outerHTML">
        Delete
    </button>
`;

Because that HTMX markup was added dynamically by JavaScript rather than inserted by HTMX, process it explicitly:

JavaScript
this.innerHTML = template;
htmx.process(this);

That is an important distinction:

HTML inserted by HTMX is automatically processed.

HTML inserted manually by a Web Component may need htmx.process(element).

A full example:

JavaScript
class UserActions extends HTMLElement {
    connectedCallback() {
        const userId = this.getAttribute("user-id");

        this.innerHTML = `
            <button
                hx-delete="/users/${userId}"
                hx-confirm="Delete this user?"
                hx-target="#users-panel"
                hx-swap="outerHTML">
                Delete
            </button>
        `;

        htmx.process(this);
    }
}

customElements.define("user-actions", UserActions);
7. Be careful with Shadow DOM

Web Components often use Shadow DOM:

JavaScript
this.attachShadow({ mode: "open" });

Shadow DOM provides excellent style and markup isolation, but it complicates HTMX integration because HTMX usually operates in the regular document tree.

For example:

JavaScript
this.shadowRoot.innerHTML = `
    <button hx-get="/something">Load</button>
`;

HTMX may not automatically discover or process that button in the same way it processes normal DOM content.

For an HTMX-first application, I would use this rule:

Use light DOM when:

HTMX needs to target elements inside the component

forms inside the component submit through HTMX

server fragments are swapped inside the component

global CSS should style the component

the component mostly enhances normal HTML

Use Shadow DOM when:

the component is a self-contained interactive widget

it manages its own state and requests

style isolation is important

HTMX only replaces the entire component from outside

For your environment, I would default to light DOM components unless you have a clear reason to use Shadow DOM.

8. Design components as progressive enhancements

A strong Web Component should enhance usable HTML rather than replace everything with JavaScript.

Instead of:

HTML
<user-list></user-list>

Consider:

HTML
<user-list>
    <ul>
        <li>Alice</li>
        <li>Bob</li>
    </ul>
</user-list>

Then the component adds filtering, selection, or keyboard navigation.

JavaScript
class UserList extends HTMLElement {
    connectedCallback() {
        this.addFiltering();
        this.addKeyboardNavigation();
    }
}

This gives you:

useful server-rendered HTML

better accessibility

graceful failure

simpler testing

less JavaScript

HTMX can replace the inner list while the custom element provides the enhanced behavior.

9. Handle HTMX swaps carefully

Suppose HTMX replaces the entire component:

HTML
<div
    hx-get="/fragments/tree"
    hx-target="#tree-region"
    hx-swap="innerHTML">
</div>

Every newly inserted custom element gets a fresh lifecycle:

JavaScript
connectedCallback()

When the old one is removed:

JavaScript
disconnectedCallback()

Use disconnectedCallback() to clean up:

JavaScript
class OntologyGraph extends HTMLElement {
    connectedCallback() {
        this.resizeObserver = new ResizeObserver(() => this.resize());
        this.resizeObserver.observe(this);
    }

    disconnectedCallback() {
        this.resizeObserver?.disconnect();
        this.abortController?.abort();
    }
}

Clean up:

event listeners

observers

timers

fetch requests

chart instances

editor instances

Otherwise repeated HTMX swaps can create memory leaks.

10. Let HTMX update content inside a component

A component can expose a target:

HTML
<notification-center>
    <button
        hx-get="/notifications"
        hx-target="#notification-list"
        hx-swap="innerHTML">
        Refresh
    </button>

    <div id="notification-list"></div>
</notification-center>

This works especially well with light DOM.

The custom element can add client behavior:

JavaScript
class NotificationCenter extends HTMLElement {
    connectedCallback() {
        this.addEventListener("click", this.handleClick);
    }

    disconnectedCallback() {
        this.removeEventListener("click", this.handleClick);
    }

    handleClick = event => {
        const notification = event.target.closest("[data-notification-id]");

        if (notification) {
            notification.classList.add("selected");
        }
    };
}

HTMX controls the server content. The Web Component controls local interaction.

11. Build a Python wrapper for each Web Component

Your Python component system can make Web Components feel like React components.

Python
Run
class OntologyTree(Component):
    tag = "ontology-tree"

    def __init__(
        self,
        ontology_id: str,
        selectable: bool = True,
        editable: bool = False,
    ):
        super().__init__(
            data_url=f"/api/ontologies/{ontology_id}/tree",
            selectable=selectable,
            editable=editable,
        )

Usage:

Python
Run
page = Page(
    Card(
        title="Ontology",
        children=[
            OntologyTree(
                ontology_id="animals",
                editable=True,
            )
        ],
    )
)

Rendered output:

HTML
<ontology-tree
    data-url="/api/ontologies/animals/tree"
    selectable
    editable>
</ontology-tree>

This is where you recover the React-like developer experience.

The Python layer provides:

composition

typed properties

defaults

validation

semantic component names

The Web Component provides:

browser lifecycle

client state

rich interaction

reusable behavior

HTMX provides:

server actions

fragment replacement

form submission

navigation

12. A good project structure
app/
├── main.py
├── routes/
│   ├── pages.py
│   ├── fragments.py
│   └── api.py
├── components/
│   ├── base.py
│   ├── layout.py
│   ├── forms.py
│   └── web_components.py
├── templates/
│   ├── base.html
│   └── fragments/
└── static/
    ├── components/
    │   ├── ontology-tree.js
    │   ├── data-grid.js
    │   ├── autocomplete-input.js
    │   └── code-editor.js
    ├── htmx.min.js
    └── app.css

Everything can be served by FastAPI:

Python
Run
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

Then:

HTML
<script src="/static/htmx.min.js"></script>
<script type="module" src="/static/components/ontology-tree.js"></script>
<script type="module" src="/static/components/data-grid.js"></script>

Still no package manager or build process.

The architecture I would recommend

Think of the boundaries like this:

Python components
    ↓ render
Semantic HTML + custom-element tags
    ↓
HTMX manages server interaction and fragment swaps
    ↓
Web Components enhance isolated interactive regions

A practical rule:

Use HTML first, HTMX when the server needs to react, and a Web Component when the browser needs persistent local behavior.

That gives you most of the composability people like about React without turning the entire application into a client-side JavaScript runtime.

## 5. You

Let’s consider making a rust core that we can use for all the popular back end languages (python, java, node)

## 6. ChatGPT

Yes—a Rust core with thin language-native adapters is probably the right architecture.

The important refinement is that the Rust core should not try to render an entire application. It should provide a language-neutral component model, HTML renderer, HTMX attribute system, validation, escaping, and serialization, while Python, Java, and Node provide idiomatic APIs.

Proposed architecture
                    ┌─────────────────────┐
                    │   Rust UI Core      │
                    │                     │
                    │ Component tree      │
                    │ HTML rendering      │
                    │ HTMX attributes     │
                    │ Escaping            │
                    │ Validation          │
                    │ Diffing/IDs         │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
     PyO3 adapter          JNI adapter         Node-API adapter
          │                    │                    │
       Python               Java/Kotlin          JS/TypeScript
          │                    │                    │
       FastAPI             Spring Boot          Express/Fastify

PyO3 is specifically designed to expose Rust as native Python modules. napi-rs targets compiled Node.js addons through Node-API, and Java can load the same kind of native Rust library through JNI.
Oracle Docs
+3
PyO3
+3
NAPI-RS
+3

What belongs in Rust

The Rust core should own behavior that must be identical across every language.

Rust
pub enum Node {
    Element(Element),
    Text(String),
    RawHtml(TrustedHtml),
    Fragment(Vec<Node>),
}

pub struct Element {
    pub tag: String,
    pub attributes: Vec<Attribute>,
    pub children: Vec<Node>,
}

pub struct Attribute {
    pub name: String,
    pub value: AttributeValue,
}

pub enum AttributeValue {
    String(String),
    Boolean(bool),
}

Then rendering is universal:

Rust
pub trait Render {
    fn render_into(&self, output: &mut String);
}

A Python, Java, or JavaScript component ultimately creates the same Rust tree:

Element(
    tag = "button",
    attributes = {
        "hx-post": "/users",
        "hx-target": "#users",
        "class": "primary"
    },
    children = [Text("Create user")]
)

The Rust renderer produces:

HTML
<button
    hx-post="/users"
    hx-target="#users"
    class="primary">
    Create user
</button>
Rust-core responsibilities

The core should include:

HTML escaping

attribute normalization

void-element handling

fragments and child flattening

deterministic component IDs

HTMX attribute validation

class and style merging

safe raw HTML wrappers

Web Component tag validation

rendering to strings and byte buffers

optional streaming rendering

optional component-tree serialization

These are all excellent Rust responsibilities because they are deterministic, performance-sensitive, and language-independent.

What should remain language-specific

Do not force Python, Java, and TypeScript developers to use the same awkward API.

Each adapter should feel native.

Python
Python
Run
from hyperui import Button, Card, Div

page = Card(
    title="Users",
    children=[
        Div(id="users"),
        Button(
            "Refresh",
            hx_get="/users",
            hx_target="#users",
        ),
    ],
)

Python should support:

keyword arguments

lists and generators as children

None omission

Pydantic integration

FastAPI responses

snake_case attribute conversion

context managers or decorators where useful

Java
Java
var page =
    Card.create("Users")
        .child(Div.create().id("users"))
        .child(
            Button.create("Refresh")
                .hxGet("/users")
                .hxTarget("#users")
        );

Java should support:

builders

overloads

immutable value objects

Spring ResponseEntity

Java records

Kotlin DSL extensions

TypeScript
TypeScript
const page = Card({
  title: "Users",
  children: [
    Div({ id: "users" }),
    Button({
      text: "Refresh",
      hxGet: "/users",
      hxTarget: "#users",
    }),
  ],
});

TypeScript should support:

typed object literals

arrays as children

JSX optionally

Express/Fastify response helpers

async iterables

generated .d.ts declarations

The rendered result can be identical even though the construction APIs differ.

Web Components fit naturally

A Web Component is just another element in the Rust tree.

Rust
Element::custom("ontology-tree")
    .attr("ontology-id", "animals")
    .bool_attr("editable", true)

Python:

Python
Run
OntologyTree(
    ontology_id="animals",
    editable=True,
)

Java:

Java
OntologyTree.create("animals")
    .editable(true);

TypeScript:

TypeScript
OntologyTree({
  ontologyId: "animals",
  editable: true,
});

All render:

HTML
<ontology-tree
    ontology-id="animals"
    editable>
</ontology-tree>

The browser-side JavaScript remains a standard ES module:

JavaScript
class OntologyTree extends HTMLElement {
    connectedCallback() {
        // Enhance the server-rendered element.
    }
}

customElements.define("ontology-tree", OntologyTree);

The Rust library does not need to execute JavaScript or understand the component's internal implementation. It only needs to render valid custom-element markup and configuration.

Two binding strategies

There are two viable approaches.

Approach A: native binding for each language
Rust core
├── PyO3
├── JNI
└── napi-rs

This provides the best developer experience and performance.

PyO3 exposes native Python extensions, napi-rs builds Node.js addons, and jni-rs provides Rust-side JNI support.
PyO3
+2
NAPI-RS
+2

Advantages:

native language objects

efficient calls

good error mapping

idiomatic APIs

no intermediary serialization

direct buffers where needed

Disadvantages:

three adapter implementations

more complex release pipelines

platform-specific binaries

Java JNI is significantly more cumbersome than Python or Node

every API change must be coordinated

This is still my recommended final architecture.

Approach B: stable C ABI underneath everything
Rust core
       ↓
Stable C ABI
       ↓
Python / Java / Node wrappers

Rust can export a narrow C-compatible API:

Rust
#[no_mangle]
pub extern "C" fn hui_render(
    input_ptr: *const u8,
    input_len: usize,
    output: *mut HuiBuffer,
) -> HuiStatus {
    // ...
}

A tool such as cbindgen can generate C/C++ headers for a Rust library exposing a public C API.
GitHub
+1

Advantages:

one stable low-level ABI

potentially supports Ruby, PHP, .NET, Go, and others later

bindings can share conformance fixtures

less coupling to any one Rust binding framework

Disadvantages:

manual memory ownership

weaker type mapping

more serialization

awkward callbacks

language wrappers still need substantial work

a public C ABI becomes a long-term compatibility commitment

I would not make the language-facing APIs call a large C API directly. Instead, use a very small internal ABI, if you use one at all.

Recommended hybrid

Use idiomatic direct bindings, but structure the repository so every adapter calls a stable internal Rust facade.

crates/
├── hyperui-core/
│   ├── nodes
│   ├── attributes
│   ├── escaping
│   └── rendering
│
├── hyperui-components/
│   ├── html
│   ├── htmx
│   └── web-components
│
├── hyperui-schema/
│   └── language-neutral component metadata
│
├── hyperui-python/
│   └── PyO3
│
├── hyperui-java/
│   └── JNI
│
├── hyperui-node/
│   └── napi-rs
│
└── hyperui-cli/
    └── code generation and validation

The adapter crates should be forbidden from implementing rendering rules. They only:

Accept language-native values.

Convert them into hyperui-core types.

Call the renderer.

Convert errors and results back into the host language.

That keeps behavior consistent.

Avoid excessive FFI calls

This is one of the most important performance decisions.

Do not cross the FFI boundary for every attribute and child:

Python
Run
button = rust.create_element("button")
rust.add_attribute(button, "hx-get", "/users")
rust.add_attribute(button, "hx-target", "#users")
rust.add_child(button, "Refresh")

That creates many small Python-to-Rust calls.

Instead, construct a language-side specification and send the whole subtree in one call:

Python
Run
Button(
    "Refresh",
    hx_get="/users",
    hx_target="#users",
).render()

Or batch an entire page:

Python
Run
render(page)

The adapter converts the complete tree and invokes Rust once.

A good rule is:

Cross the native boundary once per fragment, not once per node.

Component schema and code generation

Hand-maintaining hundreds of matching Python, Java, and TypeScript components would become painful. Define the component catalog once.

YAML
name: Button
tag: button

properties:
  variant:
    type: enum
    values:
      - primary
      - secondary
      - danger

  disabled:
    type: boolean

  hx_get:
    type: url
    html_name: hx-get

children:
  allowed: true

Then generate:

schema/button.yaml
    ├── Rust Button
    ├── Python Button
    ├── Java Button
    ├── Kotlin Button DSL
    ├── TypeScript Button
    └── documentation

This is where the project becomes much more than a Rust HTML string builder. It becomes a cross-language UI component specification.

Web Components could use the same schema:

YAML
name: OntologyTree
tag: ontology-tree
custom_element: true

properties:
  ontology_id:
    type: string
    html_name: ontology-id
    required: true

  editable:
    type: boolean

events:
  - ontology-selection-changed
  - ontology-node-expanded

The generator could produce:

Python wrappers

Java builders

TypeScript types

custom-element TypeScript declarations

event documentation

test fixtures

Data exchange

Keep the FFI type vocabulary intentionally small:

null
boolean
signed integer
unsigned integer
floating point
UTF-8 string
byte buffer
list
map
opaque handle

Do not expose Rust-specific types such as:

borrowed references

lifetimes

generic trait objects

PathBuf

Cow

arbitrary enums with payloads

deeply nested error types

Translate those at the adapter boundary.

For the initial version, you may not even need to expose node handles. The input can be a serialized or adapter-constructed Rust tree, and the output can simply be HTML.

Errors

Define one core error taxonomy:

Rust
pub enum HyperUiError {
    InvalidTag,
    InvalidAttribute,
    InvalidCustomElementName,
    UnsafeRawHtml,
    InvalidHtmxValue,
    InvalidChild,
    RenderFailure,
}

Map it naturally.

Python:

Python
Run
InvalidCustomElementNameError

Java:

Java
InvalidCustomElementNameException

Node:

TypeScript
throw new HyperUiError(
  "INVALID_CUSTOM_ELEMENT_NAME",
  message,
);

Every error should have a stable machine-readable code.

Packaging

This is the expensive operational part.

Python

Build wheels using PyO3 and maturin. PyO3 supports creating native Python extension modules.
PyO3
+1

Likely release artifacts:

manylinux x86_64
manylinux aarch64
macOS x86_64
macOS arm64
Windows x86_64
Node

Use napi-rs and publish precompiled platform packages. napi-rs is designed around precompiled Node.js addons and Node-API.
NAPI-RS
+1

Java

Publish:

hyperui-java.jar
hyperui-native-linux-x86_64.jar
hyperui-native-linux-aarch64.jar
hyperui-native-macos-aarch64.jar
hyperui-native-windows-x86_64.jar

The Java wrapper selects and extracts the appropriate native library at runtime.

JNI is standardized across JVM implementations on a given platform, but the native library itself still needs to be compiled for each target operating system and architecture.
Oracle Docs

Initial scope

I would resist building a full cross-language framework immediately.

Phase 1: Rust renderer

Create:

hyperui-core
hyperui-html
hyperui-htmx

Support:

HTML elements

attributes

text escaping

fragments

HTMX attributes

custom-element tags

deterministic rendering

snapshot tests

Phase 2: Python binding

Python is the immediate environment motivating the project.

Add:

hyperui-python
hyperui-fastapi

Prove:

ergonomic composition

FastAPI integration

HTMX fragments

Web Component wrappers

packaging without Node.js

acceptable debugging and tracebacks

Phase 3: schema/code generation

Once the Python API feels right, formalize it into the neutral schema.

Do not generate three poor APIs from an unproven abstraction.

Phase 4: Java adapter

Add Java builders and Spring integration.

This will test whether the core abstraction is genuinely language-neutral or accidentally Python-shaped.

Phase 5: Node adapter

Node is useful for adoption, even though users who already have Node can choose React or other frameworks. The differentiator there becomes:

shared server-rendered components

high-performance rendering

framework-neutral HTML

consistent component definitions across services

The product identity

This should not be marketed as merely:

Rust bindings for generating HTML.

The stronger idea is:

A cross-language, server-driven component system for HTML, HTMX, and Web Components.

Its central promise would be:

Define component behavior once.
Use it idiomatically from Python, Java, and TypeScript.
Render identical accessible HTML everywhere.

The architecture is viable. My strongest recommendation is to begin with Rust core + PyO3, keep the internal representation language-neutral, and delay Java and Node until the Python API has survived a real FastAPI application. That gives us a universal foundation without prematurely tripling the maintenance burden.

Sources

## 7. You

Create a detailed plan document and give me a download link

## 8. ChatGPT

I put together a structured architecture plan covering:

Vision and design goals

Overall Rust-core architecture

Component model

HTMX + Web Components integration strategy

Cross-language binding architecture (PyO3, JNI, napi-rs)

Schema-driven code generation

Repository layout

Development roadmap

Testing strategy

Future expansion ideas

You can download it here:

📄
HyperUI_Rust_Cross_Language_Architecture_Plan.docx

I also think this idea is substantial enough to grow into a full open-source framework. A next version of this document could be much more comprehensive (50–100 pages), similar to a Rust RFC or language design proposal, including:

Detailed API specification

Component lifecycle

Rendering algorithm

FFI architecture

Memory model

HTMX integration specification

Web Component lifecycle specification

Accessibility requirements

Plugin architecture

Performance benchmarks and goals

Code generation specification

Language binding guidelines

Governance and versioning strategy

Comparison with React, HTMX, LiveView, Phoenix, Blazor, Reflex, and NiceGUI

MVP and v1.0 implementation roadmap

That could become the foundation for the entire project before writing much code.

HyperUI_Rust_Cross_Language_Architecture_Plan.docx
Document

## 9. You

Let’s write     Comparison with React, HTMX, LiveView, Phoenix, Blazor, Reflex, and NiceGUI

## 10. ChatGPT

Worked for 2m 30s
HyperUI Framework Comparison

The completed document compares HyperUI with React, HTMX, Phoenix, Phoenix LiveView, Blazor, Reflex, and NiceGUI. It includes:

A high-level architecture matrix

Strengths and tradeoffs of each alternative

Direct implications for HyperUI’s design

A framework-selection guide

Strategic positioning and competitive differentiation

Requirements derived from the comparison

Explicit non-goals

A recommended product direction

Primary-source references

The comparison positions HyperUI as more structured than raw HTMX, less client-runtime-heavy than React, less platform-coupled than LiveView or Blazor, and less framework-prescriptive than Reflex or NiceGUI. This aligns with the documented architectures of the compared projects.
GitHub
+5
React
+5
htmx
+5

HyperUI_Framework_Comparison.docx

HyperUI_Framework_Comparison.docx
Document
Sources

## 11. You

Is this a good original idea?

## 12. ChatGPT

Yes. I think it's a good idea, but I would refine the vision slightly because the truly original part isn't "Rust renders HTML." There are already libraries that do that.

The originality comes from combining several ideas that haven't really been unified into a coherent ecosystem.

What's already been done

None of these ideas are new on their own:

React popularized component composition.

HTMX popularized server-driven UI.

Web Components standardized reusable browser components.

Rust has HTML builders such as Maud and Dioxus's SSR capabilities.

Phoenix LiveView showed that server-first UIs can feel modern.

NiceGUI and Reflex provide Python-first web frameworks.

So if the pitch is:

"A Rust HTML renderer."

that's not very differentiated.

What I think is novel

The interesting idea is:

A language-neutral component specification with a high-performance Rust core that exposes idiomatic APIs to multiple backend languages while targeting plain HTML, HTMX, and Web Components.

That's a much bigger idea.

Think of it as:

React's component model without React's runtime.

or

A portable server-component ecosystem.

I don't know of another project trying to solve exactly that problem across Python, Java, Node, and potentially Go or .NET.

The real innovation

I actually think the most valuable piece isn't the renderer.

It's the component specification.

Imagine this:

YAML
component: Button

properties:
  variant:
    enum:
      - primary
      - secondary

  disabled:
    type: bool

children: true

events:
  - click

From this one specification you generate:

Rust component

Python component

Java builder

TypeScript component

documentation

type definitions

tests

That's much more interesting than yet another rendering engine.

Why this matters

Suppose your company has:

Python FastAPI services

Java Spring applications

Node Express APIs

Today each team writes different UI helper libraries.

With HyperUI:

Python
↓

Button(...)

↓

Rust Core

↓

HTML
Java
↓

Button.builder()

↓

Rust Core

↓

HTML
Node
↓

<Button />

↓

Rust Core

↓

HTML

Every team produces identical HTML.

That's compelling for organizations with mixed-language backends.

I think there is an even bigger opportunity

While we've been discussing this, something clicked for me.

I don't think HyperUI should compete with React.

I think it should compete with design systems.

Imagine this:

HyperUI Material

HyperUI Bootstrap

HyperUI Government Design System

HyperUI USWDS

HyperUI Carbon

HyperUI Tailwind

All expose the same API:

Python
Run
Button(
    variant="primary"
)

The renderer chooses the CSS classes.

That starts looking like a cross-language design-system engine, which is a stronger long-term position than simply being another web framework.

The biggest technical risk

The challenge isn't Rust.

It's API design.

If you support:

Python

Java

Kotlin

Node

TypeScript

C#

Go

you'll constantly be asking:

"What is the canonical component API?"

React solved this by saying:

"Everything is JavaScript."

You don't have that luxury.

I think the answer is:

define behavior in the schema

let each language adapter feel completely native

never force Python to look like Java

never force Java to look like JavaScript

The schema should describe semantics, not syntax.

I would narrow the MVP

Instead of promising:

"React replacement."

I'd promise:

"The best way to build HTMX applications from Python."

That's a concrete audience with an immediate pain point—exactly the environment you've described, where Node.js isn't available.

Once the Python version succeeds, adding Java becomes much lower risk. If the abstractions hold up across those two very different languages, expanding to Node, Go, or .NET becomes a strategic decision rather than a leap of faith.

So my assessment is:

The individual technologies are not novel.

The combination is uncommon.

The strongest innovation is not the renderer but the language-neutral component model and schema-driven ecosystem.

The market fit is clearest for server-rendered applications that want modern component ergonomics without a JavaScript build tool.

That's a space where there is room for something genuinely differentiated, provided the project stays focused on its core value rather than trying to become "yet another frontend framework."

## 13. You

Is the component specification idea in the plan document you made?

## 14. ChatGPT

Not in the depth that I now think it deserves.

The document mentions a schema and code generation section, but after thinking through the architecture with you, I believe the Component Specification is actually the centerpiece of the entire project. It should move from being a supporting feature to being the foundation.

I would restructure the architecture document like this:

Vision

Core Principles

Component Specification (the heart of HyperUI)

Rust Rendering Engine

Language Bindings

HTMX Integration

Web Components

Design Systems

Developer Experience

Roadmap

The new "Component Specification" chapter would be substantial (20–30 pages by itself) and cover:

Goals

Language-neutral

Declarative

Strongly typed

Versioned

Extensible

Backwards compatible

Specification format

YAML/JSON/TOML

Schema validation

Versioning

Component model

Properties

Children

Slots

Events

Lifecycle hooks

Accessibility metadata

Type system

Primitive types

Enums

Unions

Collections

Defaults

Validation rules

Rendering semantics

HTML mapping

HTMX attribute mapping

Web Component mapping

Server Component mapping

Code generation

Rust

Python

Java

TypeScript

Documentation

Tests

Compatibility rules

Adding properties

Deprecating properties

Semantic versioning

Migration guidance

Extension model

Third-party component libraries

Design systems

Plugin architecture

Examples

Button

Card

DataGrid

OntologyTree

The more we've discussed it, the more convinced I am that the specification is the product.

The Rust renderer can be replaced.

The Python bindings can be rewritten.

The Java bindings can evolve.

But if there is a stable, well-designed component specification, everything else can be regenerated from it. That becomes the long-term asset of the project.

In fact, I would even consider renaming the core crate from something like hyperui-core to hyperui-spec, because every other crate would depend on that specification.

I think it's worth rewriting the architecture document around this idea. Rather than a 10-page overview, I'd aim for a proper engineering design document (roughly 75–100 pages) similar to an RFC or language specification, where the component specification is the central concept and the Rust implementation is presented as the first reference implementation rather than the defining feature.

## 15. You

Could we made pydantic models that convert to the spec?

## 16. ChatGPT

Yes—and that may be the best Python authoring experience for the specification.

The clean architecture would be:

Pydantic component models
        ↓
validated intermediate representation
        ↓
language-neutral HyperUI specification
        ↓
Rust renderer and code generators

Pydantic would be a Python authoring layer, not the canonical specification itself. That distinction matters because Java, Rust, and TypeScript implementations should not be forced to understand Pydantic-specific behavior.

Example

A developer could define a component using Pydantic:

Python
Run
from typing import Annotated, Literal
from pydantic import BaseModel, Field


class ButtonProps(BaseModel):
    variant: Literal["primary", "secondary", "danger"] = "primary"

    disabled: bool = False

    size: Literal["small", "medium", "large"] = "medium"

    label: Annotated[
        str,
        Field(
            min_length=1,
            description="Visible button label",
        ),
    ]

Then decorate or register it as a HyperUI component:

Python
Run
from hyperui.spec import component


@component(
    name="Button",
    tag="button",
    allows_children=False,
)
class ButtonProps(BaseModel):
    variant: Literal["primary", "secondary", "danger"] = "primary"
    disabled: bool = False
    size: Literal["small", "medium", "large"] = "medium"
    label: Annotated[str, Field(min_length=1)]

HyperUI could convert that into a canonical specification:

YAML
spec_version: "1.0"

component:
  name: Button
  tag: button

properties:
  label:
    type: string
    required: true
    validation:
      min_length: 1

  variant:
    type: enum
    values:
      - primary
      - secondary
      - danger
    default: primary

  disabled:
    type: boolean
    default: false

  size:
    type: enum
    values:
      - small
      - medium
      - large
    default: medium

children:
  allowed: false
Pydantic metadata can express rendering rules

Normal Pydantic fields describe data, but components also need HTML behavior. We could use Annotated metadata for that.

Python
Run
from typing import Annotated, Literal
from pydantic import BaseModel, Field

from hyperui.spec import (
    HtmlAttribute,
    BooleanAttribute,
    CssClassVariant,
)


class ButtonProps(BaseModel):
    disabled: Annotated[
        bool,
        BooleanAttribute("disabled"),
    ] = False

    title: Annotated[
        str | None,
        HtmlAttribute("title"),
    ] = None

    variant: Annotated[
        Literal["primary", "secondary", "danger"],
        CssClassVariant(
            prefix="btn-",
            mappings={
                "primary": "btn-primary",
                "secondary": "btn-secondary",
                "danger": "btn-danger",
            },
        ),
    ] = "primary"

That could compile into:

YAML
properties:
  disabled:
    type: boolean
    default: false
    rendering:
      target: attribute
      html_name: disabled
      boolean_attribute: true

  title:
    type: string
    nullable: true
    rendering:
      target: attribute
      html_name: title

  variant:
    type: enum
    values:
      - primary
      - secondary
      - danger
    default: primary
    rendering:
      target: css_class
      mappings:
        primary: btn-primary
        secondary: btn-secondary
        danger: btn-danger
HTMX metadata

This could be especially powerful for HTMX.

Python
Run
from hyperui.spec import HtmxAttribute


class RefreshButtonProps(BaseModel):
    endpoint: Annotated[
        str,
        HtmxAttribute("hx-get"),
    ]

    target: Annotated[
        str,
        HtmxAttribute("hx-target"),
    ]

    swap: Annotated[
        Literal[
            "innerHTML",
            "outerHTML",
            "beforebegin",
            "afterbegin",
            "beforeend",
            "afterend",
            "delete",
            "none",
        ],
        HtmxAttribute("hx-swap"),
    ] = "innerHTML"

Usage:

Python
Run
button = RefreshButtonProps(
    endpoint="/users",
    target="#users",
)

Rendered output:

HTML
<button
    hx-get="/users"
    hx-target="#users"
    hx-swap="innerHTML">
</button>
Web Component models

Pydantic would also work nicely for typed Web Component wrappers.

Python
Run
from typing import Annotated
from pydantic import BaseModel

from hyperui.spec import (
    HtmlAttribute,
    BooleanAttribute,
    custom_element,
)


@custom_element(
    name="OntologyTree",
    tag="ontology-tree",
)
class OntologyTreeProps(BaseModel):
    ontology_id: Annotated[
        str,
        HtmlAttribute("ontology-id"),
    ]

    editable: Annotated[
        bool,
        BooleanAttribute("editable"),
    ] = False

    selectable: Annotated[
        bool,
        BooleanAttribute("selectable"),
    ] = True

This generates:

YAML
component:
  name: OntologyTree
  tag: ontology-tree
  kind: custom_element

properties:
  ontology_id:
    type: string
    required: true
    rendering:
      target: attribute
      html_name: ontology-id

  editable:
    type: boolean
    default: false
    rendering:
      target: boolean_attribute
      html_name: editable

  selectable:
    type: boolean
    default: true
    rendering:
      target: boolean_attribute
      html_name: selectable

And the HTML:

HTML
<ontology-tree
    ontology-id="animals"
    selectable>
</ontology-tree>
Children and slots

Pydantic can represent children too, although they should probably be modeled separately from ordinary HTML attributes.

Python
Run
from typing import Annotated
from pydantic import BaseModel

from hyperui.spec import Children, Slot


class CardProps(BaseModel):
    title: str

    header: Annotated[
        "ComponentNode | None",
        Slot("header"),
    ] = None

    children: Annotated[
        list["ComponentNode"],
        Children(),
    ] = []

Canonical specification:

YAML
slots:
  header:
    required: false
    cardinality: one

children:
  allowed: true
  cardinality: many

Usage:

Python
Run
Card(
    title="Users",
    header=Badge(text="Admin"),
    children=[
        UserTable(),
        RefreshButton(),
    ],
)
Events

Web Component events can also be declared through model metadata.

Python
Run
from hyperui.spec import ComponentEvent, custom_element


@custom_element(
    name="OntologyTree",
    tag="ontology-tree",
    events=[
        ComponentEvent(
            name="node-selected",
            payload_model="OntologyNodeSelected",
            bubbles=True,
            composed=True,
        ),
    ],
)
class OntologyTreeProps(BaseModel):
    ontology_id: str

Payload model:

Python
Run
class OntologyNodeSelected(BaseModel):
    node_id: str
    node_type: str

That could generate:

Python event payload types

Rust structs

Java records

TypeScript event types

Web Component declaration files

documentation

For TypeScript:

TypeScript
interface OntologyNodeSelected {
  nodeId: string;
  nodeType: string;
}

interface OntologyTreeEventMap {
  "node-selected": CustomEvent<OntologyNodeSelected>;
}
Use Pydantic’s JSON Schema—but do not expose it directly

Pydantic can already generate JSON Schema:

Python
Run
schema = ButtonProps.model_json_schema()

That is useful for extracting:

property names

required fields

string constraints

numeric constraints

enums

unions

arrays

nested models

descriptions

defaults

However, raw JSON Schema is not enough to describe UI semantics such as:

HTML tag mapping

CSS class mapping

HTMX attributes

slots

event behavior

child rules

accessibility requirements

Web Component registration

design-system tokens

So the converter should combine:

Pydantic JSON Schema
+
HyperUI Annotated metadata
+
component decorator metadata
=
HyperUI Component Specification
Proposed converter API
Python
Run
from hyperui.spec import compile_component


spec = compile_component(ButtonProps)

Or:

Python
Run
spec = ButtonProps.__hyperui_spec__()

Export formats:

Python
Run
spec.to_dict()
spec.to_json()
spec.to_yaml()
spec.to_toml()

Example:

Python
Run
spec.to_yaml("components/button.hyperui.yaml")
Compilation pipeline

Internally:

1. Inspect decorated Pydantic model
2. Generate Pydantic JSON Schema
3. Read FieldInfo and Annotated metadata
4. Resolve nested models and references
5. Normalize types into HyperUI's type system
6. Validate rendering semantics
7. Produce canonical intermediate representation
8. Serialize YAML/JSON
9. Generate language bindings

The intermediate representation might look like:

Python
Run
class ComponentSpec(BaseModel):
    spec_version: str
    name: str
    tag: str
    kind: str
    properties: list["PropertySpec"]
    children: "ChildrenSpec"
    slots: list["SlotSpec"]
    events: list["EventSpec"]
    accessibility: "AccessibilitySpec | None"

Interestingly, the specification model itself could also be written in Pydantic.

Python
Run
class PropertySpec(BaseModel):
    name: str
    type: "TypeSpec"
    required: bool
    default: object | None = None
    rendering: "RenderingSpec | None" = None

Then the Python compiler produces an instance of ComponentSpec, which serializes to the canonical format.

Design-system example

This gets especially compelling with design systems.

Python
Run
from typing import Annotated, Literal
from pydantic import BaseModel

from hyperui.spec import CssClassVariant, component


@component(name="Button", tag="button")
class UswdsButtonProps(BaseModel):
    variant: Annotated[
        Literal[
            "default",
            "secondary",
            "accent-cool",
            "accent-warm",
            "base",
            "outline",
            "unstyled",
        ],
        CssClassVariant(
            mappings={
                "default": "usa-button",
                "secondary": "usa-button usa-button--secondary",
                "accent-cool": "usa-button usa-button--accent-cool",
                "accent-warm": "usa-button usa-button--accent-warm",
                "base": "usa-button usa-button--base",
                "outline": "usa-button usa-button--outline",
                "unstyled": "usa-button usa-button--unstyled",
            }
        ),
    ] = "default"

The same semantic component could have alternate render profiles:

Button specification
├── USWDS rendering profile
├── Bootstrap rendering profile
├── Tailwind rendering profile
└── Carbon rendering profile

The user-facing Python model stays stable while the active renderer determines the markup and classes.

Important architectural rule

The direction of dependency should be:

Pydantic model
    ↓ compiles to
HyperUI specification

Not:

HyperUI specification
    ↓ depends permanently on
Pydantic implementation details

The canonical spec should remain representable as plain YAML or JSON. That allows:

Rust-native authoring later

Java annotation processors

Kotlin DSLs

TypeScript decorators or schemas

external design-system tools

IDE integrations

non-Python users

Recommended project packages
hyperui-spec
    Canonical specification models and validation

hyperui-pydantic
    Pydantic-to-spec compiler

hyperui-codegen
    Rust, Python, Java and TypeScript generation

hyperui-render
    Rust rendering engine

hyperui-python
    Runtime Python component API

A Python developer could install:

Bash
pip install hyperui-pydantic

And write:

Python
Run
from hyperui_pydantic import component, HtmlAttribute

The resulting .hyperui.yaml files become portable assets consumed by every language.

Best role for Pydantic

Pydantic would give HyperUI:

excellent Python ergonomics

strong validation

type introspection

JSON Schema generation

nested model support

discriminated unions

custom validators

clear error messages

familiar use of Annotated and Field

So yes: Pydantic models converting into the language-neutral component specification should probably be one of HyperUI’s flagship features.

It gives Python users a concise authoring model while preserving the larger goal of a portable, cross-language component ecosystem.

## 17. You

I think we are missing a key concept from react components: the ability to directly write html ourselves. I’d like an jsx like interface

## 18. ChatGPT

Yes—that is the missing piece.

Pydantic models are excellent for declaring component contracts, but they are not a pleasant way to author the component’s markup. HyperUI needs two complementary concepts:

Component specification — props, events, slots, validation, accessibility, and cross-language metadata.

Component template — JSX-like markup describing what the component renders.

The ideal experience would look something like this:

HTML
<Component name="UserCard" props={UserCardProps}>
    <article class="user-card">
        <header>
            <Avatar src={props.avatar_url} alt={props.name} />
            <h2>{props.name}</h2>
        </header>

        <p>{props.email}</p>

        <Button
            variant="primary"
            hx-get={"/users/" + props.user_id}
            hx-target="#user-details"
        >
            View user
        </Button>
    </article>
</Component>

That is much closer to what makes React components enjoyable: you can directly write HTML while freely composing higher-level components.

The proposed model
Pydantic props model
        +
JSX-like HyperUI template
        ↓
HyperUI compiler
        ↓
canonical component specification
        +
Rust render instructions
        ↓
Python / Java / Node runtime
        ↓
HTML + HTMX + Web Components

For example:

Python
Run
from pydantic import BaseModel, HttpUrl


class UserCardProps(BaseModel):
    user_id: str
    name: str
    email: str
    avatar_url: HttpUrl | None = None

Then a sibling template:

HTML
<!-- user_card.hui -->

<article class="user-card">
    <header>
        <Avatar
            src={props.avatar_url}
            alt={props.name}
        />

        <h2>{props.name}</h2>
    </header>

    <p>{props.email}</p>

    <Button
        hx-get={"/users/" + props.user_id}
        hx-target="#user-details"
    >
        View user
    </Button>
</article>

Registration:

Python
Run
from hyperui import component

UserCard = component(
    name="UserCard",
    props=UserCardProps,
    template="user_card.hui",
)

Usage:

HTML
<UserCard
    user-id="123"
    name="Ada Lovelace"
    email="ada@example.com"
/>

Or from Python:

Python
Run
page = UserCard(
    user_id="123",
    name="Ada Lovelace",
    email="ada@example.com",
)
It should support native HTML directly

The template language should treat lowercase tags as HTML:

HTML
<section>
    <h1>{props.title}</h1>
    <p>{props.description}</p>
</section>

Uppercase tags represent HyperUI components:

HTML
<Card>
    <Button>Save</Button>
</Card>

Hyphenated tags represent Web Components:

HTML
<ontology-tree
    ontology-id={props.ontology_id}
    editable={props.editable}
/>

This gives us a clean interpretation rule:

<div>             → native HTML
<Button>          → HyperUI component
<ontology-tree>   → Web Component
JSX-like expressions

A first version should intentionally support a limited expression language.

Property access
HTML
<h2>{props.user.name}</h2>
Conditional rendering
HTML
{#if props.is_admin}
    <Badge variant="danger">Administrator</Badge>
{/if}
Iteration
HTML
<ul>
    {#for user in props.users}
        <li>
            <UserCard user={user} />
        </li>
    {/for}
</ul>
Optional values
HTML
{#if props.description}
    <p>{props.description}</p>
{/if}
Attribute expressions
HTML
<button
    disabled={props.disabled}
    class={classes("button", props.variant)}
>
    {props.label}
</button>
Slots
HTML
<Card>
    <slot name="header">
        <h2>{props.title}</h2>
    </slot>

    <slot />

    <slot name="footer" />
</Card>

This should not embed unrestricted Python, JavaScript, or Java code. Templates must remain portable across backend languages.

Why we should not use actual JavaScript JSX

Real JSX is fundamentally JavaScript syntax transformed into JavaScript function calls:

JavaScript
<Button variant="primary">Save</Button>

becomes something conceptually similar to:

JavaScript
jsx(Button, {
    variant: "primary",
    children: "Save",
});

Using standard JSX would make JavaScript the canonical implementation language and usually introduce a JavaScript compilation toolchain—the exact dependency we are trying to avoid.

Instead, HyperUI should have a JSX-inspired language implemented by the Rust compiler.

Potential extensions:

.hui
.hxui
.hyper

I like .hui because it is concise and framework-specific:

user_card.py
user_card.hui

The compiler itself could be distributed as a native executable:

Bash
hyperui compile components/

No Node.js or npm would be involved.

Compile-time versus runtime parsing

We could support both.

Development mode

Parse templates dynamically:

Python
Run
app = HyperUI(
    templates="components/",
    reload=True,
)

When user_card.hui changes, the development server recompiles it automatically.

Production mode

Compile templates ahead of time:

Bash
hyperui build

Output:

.hyperui/
├── component-registry.bin
├── render-programs.bin
└── manifest.json

The Rust runtime loads precompiled render instructions. Production requests never parse templates.

This preserves a comfortable editing experience while delivering fast rendering.

The template compiler

The Rust compiler would parse:

HTML
<Button
    variant={props.variant}
    disabled={props.disabled}
>
    {props.label}
</Button>

Into an intermediate representation:

Rust
ComponentNode {
    component: "Button",
    properties: [
        BoundProperty {
            name: "variant",
            expression: PropertyPath(["props", "variant"]),
        },
        BoundProperty {
            name: "disabled",
            expression: PropertyPath(["props", "disabled"]),
        },
    ],
    children: [
        ExpressionNode(
            PropertyPath(["props", "label"])
        ),
    ],
}

The compiler can then validate the template against the Pydantic-derived specification:

Does Button exist?

Is variant a valid property?

Does the value have the correct type?

Is disabled Boolean?

Does the component permit children?

Are required properties supplied?

Is the HTML tag valid?

Is the custom-element name valid?

That is stronger than ordinary JSX because the compiler has a language-neutral component registry.

Inline templates should also be possible

For small Python components:

Python
Run
from hyperui import component, hui
from pydantic import BaseModel


class AlertProps(BaseModel):
    message: str
    severity: str = "info"


@component
class Alert:
    Props = AlertProps

    template = hui("""
        <aside class={"alert alert-" + props.severity}>
            <strong>{props.message}</strong>
        </aside>
    """)

However, external .hui templates should be preferred for larger components because they provide:

syntax highlighting

formatting

language-server support

cleaner Python files

reusable compiler tooling

easier cross-language portability

Java could use the same template
Java
@HyperComponent(
    name = "UserCard",
    template = "user_card.hui"
)
public record UserCardProps(
    String userId,
    String name,
    String email
) {}

Node could use it too:

TypeScript
export const UserCard = defineComponent<UserCardProps>({
  name: "UserCard",
  template: "./user_card.hui",
});

All three runtimes consume the same template and produce the same HTML.

That is a substantial advantage over exposing only language-specific builders.

Direct HTML escape hatch

There should also be a deliberate way to write raw HTML fragments where necessary:

HTML
{@html props.trusted_html}

But the type should require an explicitly trusted value:

Python
Run
from hyperui import TrustedHtml

class ArticleProps(BaseModel):
    body: TrustedHtml

Ordinary expressions remain escaped:

HTML
<div>{props.user_input}</div>

This protects against accidentally turning normal strings into unescaped HTML.

Python-only JSX is another option—but not the foundation

We could eventually provide Python syntax such as:

Python
Run
def UserCard(props: UserCardProps):
    return html(
        <article class="user-card">
            <h2>{props.name}</h2>
            <Button>View user</Button>
        </article>
    )

But Python cannot parse JSX syntax natively. Supporting this would require:

a source preprocessor,

a custom import hook,

an editor plugin,

or Python grammar extensions.

That could be an optional convenience feature, but it is too fragile to become the canonical authoring format.

A .hui template language gives us JSX ergonomics without fighting each host language's parser.

The resulting component architecture

Each component would consist of up to three pieces:

UserCard
├── contract
│   └── UserCardProps model
├── view
│   └── user_card.hui
└── optional browser behavior
    └── user-card.js Web Component

The responsibilities are clean:

Pydantic model: accepted data and validation

.hui template: HTML structure and component composition

Web Component: persistent browser-side interaction

HTMX: server requests and fragment updates

Rust core: compilation, validation, and rendering

Recommendation

The JSX-like template language should become a first-class pillar of HyperUI rather than a minor convenience feature:

Pydantic defines what a component accepts. HyperUI Markup defines what it renders. Web Components define how rich browser interactions behave.

That gives us the central ergonomics people love about React while retaining plain HTML, server rendering, HTMX, language portability, and a Node-free toolchain.

## 19. You

Rewrite the plan document with this

## 20. ChatGPT

Worked for 3m 5s

I rewrote the architecture plan around the new core model:

Pydantic contracts define component inputs.

JSX-like .hui templates define rendered markup.

Rust compiles, validates, and renders the templates.

HTMX handles server interaction and fragment updates.

Web Components provide persistent browser-side behavior.

Python, Java, and Node consume the same component specification and templates.

The revised document is 18 pages and includes syntax proposals, compiler architecture, expression rules, slots, control flow, escaping, bindings, repository layout, MVP scope, roadmap, risks, and prototype acceptance criteria.

HyperUI_Rewritten_Architecture_Plan.docx

HyperUI_Rewritten_Architecture_Plan.docx
Document

## 21. You

Hyperui is already taken on pypi

## 22. ChatGPT

That's actually useful to know this early. If you're serious about building this, I'd avoid starting with a name that's already occupied.

I also think we've uncovered something more important: the project has evolved beyond "UI."

What you're really building is:

a component specification

a compiler

a cross-language runtime

a rendering engine

a code generator

The UI is almost an implementation detail.

I would look for a name that reflects that

Instead of:

HyperUI

FastUI

BetterUI

I'd lean toward names that evoke:

composition

templates

rendering

markup

components

specifications

Component/specification inspired

These are my favorites.

Compono

Latin for "put together, compose."

Python
Run
from compono import Button

Compositor

Python
Run
from compositor import Card

Very descriptive.

Rendera

Short and memorable.

Python
Run
from rendera import html

RenderKit

Suggests a toolkit rather than a framework.

MarkupKit

Emphasizes the template language.

ComposeKit

Especially appropriate since composition is the central idea.

Rust-inspired

FerrumUI

Ferrum = Latin for iron.

ForgeUI

You seem to gravitate toward "Forge" (OntoForge, etc.).

Anvil

Components are forged.

Python
Run
from anvil import Button

There are existing products with that name, though, so availability would need to be checked.

Template-language inspired

If the .hui language becomes central:

Glyph

Because you're writing markup.

Stencil

A stencil generates HTML.

There are existing projects using this name, so availability would need to be checked.

Weave

You're weaving components together.

Loom

Templates are woven.

My favorite direction

The more I think about it, the more I think the framework shouldn't be named after "UI" at all.

The specification deserves its own identity.

Something like:

Compose Specification

↓

Rust Compiler

↓

Language Bindings

↓

HTML

For example:

Loom
├── loom-spec
├── loom-compiler
├── loom-python
├── loom-java
├── loom-node
├── loom-htmx
└── loom-webcomponents

That feels like a language ecosystem rather than just another Python package.

One thing I'd change from the current plan

I'd also rename the template extension.

I don't love:

.hui

because it's tightly coupled to the framework name.

Instead I'd choose something framework-independent like:

.comp

or

.component

or

.view

or

.render

Then if you ever rename the framework, the template language doesn't become awkward.

I also think it's worth taking a step back and treating this like you did with OntoCode: pick the name before you write much code. A cross-language component system has the potential to become an ecosystem, so the project name, the specification name, and the template language name should all fit together from the start.

## 23. You

What are some obscure words that sound like react or angular?

## 24. ChatGPT

I like this direction. Framework names tend to be:

Short (2–3 syllables)

Easy to pronounce

Slightly technical

Not obviously descriptive

Memorable enough to become a verb ("we use React", "we use Angular")

Here are some categories.

Latin-inspired

These have meanings related to building or composing.

Name	Meaning
Compago	Framework, structure
Nexus	Connection, binding
Contexta	Woven together
Structor	Builder
Textura	Weaving, structure
Origo	Origin
Forma	Form, shape
Contex	To weave together
Necto	To bind together
Ligare	To connect

I especially like Compago.

Greek-inspired
Name	Meaning
Synthex	From synthesis
Morphos	Shape/form
Kosmos	Ordered arrangement
Stoicheia	Elements
Syntaxa	Inspired by syntax
Metron	Measure
Logion	Logic/speech

Synthex feels framework-like.

Geometry-inspired

React and Angular both have geometric names.

Vertex

Facet

Prism

Vector

Axis

Arcus

Chord

Radius

Tangent

Polygon

Apex

Lattice

Vertexa

Tessella

Tessera

I really like Lattice because components connect together.

Compiler-inspired

Since you're really building a compiler.

Parsec

Lexer

Token

ASTra

Arbor

Arboris

Syntax

Arbora

Codex

Compilex

Lexor

Weaving/Fabric

This fits component composition well.

Loom

Weave

Warp

Weft

Spindle

Shuttle

Filament

Mesh

Fabric

Interlace

Invented names

These are my favorite because they don't carry baggage.

Reactra

Compora

Rendera

Nexora

Virex

Vireon

Templex

Compyx

Rendrix

Composa

Structra

Templarix

Markora

Syntra

Flexor

Nexis

Compyx

Arcora

Vectra

Lumora

My favorites

If I wanted something that sounds like React, Angular, Vue, Svelte, Solid, Astro, etc., I'd shortlist:

Synthex ⭐⭐⭐⭐⭐

Compago ⭐⭐⭐⭐⭐

Rendera ⭐⭐⭐⭐☆

Nexora ⭐⭐⭐⭐☆

Lattice ⭐⭐⭐⭐☆

Arcora ⭐⭐⭐⭐☆

Vectra ⭐⭐⭐⭐☆

Composa ⭐⭐⭐⭐☆

Templex ⭐⭐⭐⭐☆

Morphos ⭐⭐⭐⭐☆

One naming idea I really like

Because your project is centered on a component specification, you could use a name that's a little abstract, similar to "React" (which isn't directly descriptive of a UI library).

For example:

Nexora

Synthex

Arcora

Compago

Then your ecosystem naturally becomes:

Nexora
├── nexora-spec
├── nexora-compiler
├── nexora-python
├── nexora-java
├── nexora-node
├── nexora-htmx
└── nexora-webcomponents

That feels like a cohesive language ecosystem rather than just a Python package.

One thing I'd recommend before getting attached to a name is checking:

PyPI package availability

crates.io availability

npm availability

GitHub organization/repository availability

A reasonably available .dev or .org domain

Finding a name that's available across all of those is often harder than coming up with the name itself.

## 25. You

I actually own the python package hedron that nobody uses that we could just use because I really like the name. The only awkward part is some 3 year old rust crate is called hedron that I don’t own.

## 26. ChatGPT

I actually think Hedron is significantly better than HyperUI.

It's short, memorable, easy to pronounce, and doesn't lock you into "UI." It also has a subtle connection to geometry and composition, which fits a component system surprisingly well.

Think about the branding:

Hedron

No explanation needed. Similar vibe to:

React

Angular

Vue

Solid

Astro

Svelte

They're all essentially invented or repurposed words.

It also scales well
hedron-spec
hedron-compiler
hedron-python
hedron-java
hedron-node
hedron-rust
hedron-htmx
hedron-webcomponents
hedron-cli

or as Rust crates:

hedron-core
hedron-render
hedron-template
hedron-spec
hedron-codegen

That sounds like a real ecosystem.

The Rust crate issue

I don't think the existence of a small, inactive crate named hedron is necessarily a dealbreaker, but it does affect your options.

You have a few approaches:

Option 1 (my favorite)

Use Hedron as the project name.

Use:

hedron-core
hedron-render
hedron-spec

instead of trying to publish a crate literally named hedron.

This is extremely common.

Examples:

Tokio → tokio-util, tokio-stream

Bevy → bevy_ecs, bevy_render

Axum → axum-core

Serde → serde_json

Many ecosystems don't actually depend on a crate that matches the project name exactly.

Option 2

Reach out to the owner.

A three-year-old crate with little activity may have an owner who is happy to transfer it if it's effectively abandoned. There's no guarantee, but it's worth asking politely if the project becomes serious.

Option 3

Use a different root crate.

hedron-core

becomes the primary crate.

People write:

Rust
use hedron_core::html;

Not as elegant as use hedron::..., but perfectly acceptable.

I actually like the meaning

A hedron is simply a geometric solid with flat faces.

That has some surprisingly nice metaphors:

Components are building blocks.

Components connect at faces.

Complex applications are assemblies of simple solids.

Composition becomes literal geometry.

The logo possibilities are excellent:

Cube

Octahedron

Icosahedron

Low-poly aesthetic

Isometric graphics

It's distinctive without being gimmicky.

One thing I'd lean into

Rather than hiding the geometric connection, I'd make it part of the identity.

For example:

Hedron is built from components. Components compose into applications the way faces compose a polyhedron.

Even if users never think about the etymology again, it's a memorable origin story.

One suggestion

I'd stop calling the templates ".hui" now.

Instead:

.component

or

.hedron

or

.hdn

For example:

UserCard.hdn
Button.hdn
Dashboard.hdn

I actually like .hdn—it's short, recognizable, and tied to the project name without being verbose.

My only hesitation

The one thing I'd investigate before committing is trademark risk, not just package names.

"Hedron" appears in various company and product names across different industries. That doesn't automatically prevent you from using it for an open-source framework, but if you're envisioning this becoming a major ecosystem or commercial venture, it's worth doing a trademark search in software classes before investing heavily in branding.

From a purely technical and branding perspective, though, I think Hedron is a stronger, more timeless name than HyperUI. It leaves room for the project to grow beyond a UI library into the component specification, compiler, and cross-language ecosystem we've been discussing.

## 27. You

Let’s go all in with Hedron. Rewrite our plan document

## 28. ChatGPT

I like this direction. I think Hedron is a much stronger identity than HyperUI because it doesn't pigeonhole the project as "just a UI framework." It leaves room for the specification, compiler, language bindings, and ecosystem to evolve together.

I've rewritten the architecture plan around the Hedron vision:

Hedron as the project identity

Pydantic contracts as the Python authoring model

.hdn JSX-like templates as the primary component authoring experience

Canonical Hedron Component Specification as the central abstraction

Rust compiler/runtime as the reference implementation

HTMX + Web Components as first-class runtime concepts

Cross-language bindings for Python, Java, and Node

Updated repository layout and roadmap

You can download it here:

📄
Hedron_Architecture_Plan_v2.docx

I also think we're at the point where this deserves to become a proper design specification rather than a project plan. I'd propose writing a Hedron RFC-0001 (75–100 pages) modeled after a language specification. It would define:

The Hedron philosophy

The Component Specification

The .hdn language grammar

The compiler architecture

The AST

The rendering model

The runtime model

HTMX integration

Web Component integration

Language binding requirements

Code generation

Plugin system

Versioning and compatibility guarantees

That document would become the project's "constitution" and make future implementation decisions much easier. I think it's the right next step before writing significant code.

Hedron_Architecture_Plan_v2.docx
Document

## 29. You

I want hdn to feel extremely familiar to react developers

## 30. ChatGPT

Then .hdn should intentionally feel like JSX with fewer surprises, not like a new template language wearing JSX syntax.

The goal should be:

A React developer should understand 80–90% of an .hdn file immediately.

Recommended direction

Use JSX conventions almost exactly:

JavaScript
<UserCard user={props.user}>
  <Avatar src={props.user.avatarUrl} />
  <h2>{props.user.name}</h2>

  {props.user.isAdmin && (
    <Badge variant="danger">Admin</Badge>
  )}

  <Button
    hx-get={`/users/${props.user.id}`}
    hx-target="#details"
  >
    View profile
  </Button>
</UserCard>

That means Hedron should support familiar React patterns:

{expression}

ternaries

&& conditional rendering

.map(...)

fragments

component props

spread props

className

style={{ ... }}

event-like attributes

component composition

children

named slots through props

self-closing tags

Keep actual JSX syntax

I would not use custom constructs like:

HTML
{#if condition}
{/if}

or:

HTML
{#for item in items}
{/for}

Those feel like Jinja, Svelte, or Handlebars—not React.

Prefer:

JavaScript
{props.showDetails && <Details />}
JavaScript
{props.users.map(user => (
  <UserCard key={user.id} user={user} />
))}
JavaScript
{props.loading ? <Spinner /> : <UserList users={props.users} />}

That familiarity is worth the compiler complexity.

Fragments

Support React-style fragments:

JavaScript
<>
  <Header />
  <Main />
  <Footer />
</>

And possibly explicit fragments:

JavaScript
<Fragment>
  <Header />
  <Main />
</Fragment>
Children

Make children behave exactly as React developers expect:

JavaScript
<Card>
  <h2>Users</h2>
  <UserList users={props.users} />
</Card>

Inside Card.hdn:

JavaScript
<section className="card">
  {props.children}
</section>

Or expose children directly:

JavaScript
<section className="card">
  {children}
</section>

I prefer children as a top-level template binding because it feels more React-like.

Props

Use camelCase in .hdn:

JavaScript
<Button
  isDisabled={props.isDisabled}
  userId={props.userId}
/>

The compiler can map them to Python snake_case, Java bean-style names, or HTML kebab-case.

For example:

HDN:       userId
Python:    user_id
Java:      userId
HTML:      user-id

This keeps the template language independent from backend naming conventions.

HTML attributes

To maximize familiarity, accept React-style names:

JavaScript
<div
  className="panel"
  htmlFor="email"
  tabIndex={0}
/>

The compiler emits:

HTML
<div class="panel" tabindex="0"></div>
<label for="email"></label>

I would also allow native HTML forms:

JavaScript
<div class="panel">

But choose one canonical style for formatting and documentation. React developers will expect className, though plain class may be more honest for a server-rendered system.

My recommendation:

accept both class and className

format to className in .hdn

compile both to class

Expressions

The expression language should look JavaScript-like but remain constrained and portable.

Support:

JavaScript
{props.name}
{props.count + 1}
{props.enabled && <Panel />}
{props.mode === "compact" ? <Compact /> : <Full />}
{props.items.map(item => <Item item={item} />)}
{formatDate(props.createdAt)}

Avoid unrestricted JavaScript.

Do not support:

JavaScript
{window.location}
{fetch(...)}
{new Date()}
{eval(...)}
{someGlobalVariable}

The compiler should allow a portable expression subset:

literals

property access

arithmetic

comparisons

Boolean operators

ternaries

arrays and objects

safe function calls

map, filter, and perhaps join

template strings

Template strings

React developers will expect:

JavaScript
<a href={`/users/${props.userId}`}>
  View user
</a>

This should be supported.

Spread props

Support:

JavaScript
<Button {...props.buttonProps}>
  Save
</Button>

And HTML spreads:

JavaScript
<input {...props.inputAttributes} />

But validate them strongly.

The compiler should know:

which fields are legal

which values are safe

whether spreads may override explicit props

how duplicate attributes are resolved

Use React's rule: later props win.

JavaScript
<Button
  {...props.defaults}
  variant="danger"
/>

Here variant="danger" wins.

key

Support key for familiarity:

JavaScript
{props.users.map(user => (
  <UserCard key={user.id} user={user} />
))}

Even if Hedron does not initially perform client-side reconciliation, key can still provide:

stable generated IDs

deterministic rendering

future incremental rendering support

better diagnostics

list identity

That makes key semantically useful rather than decorative compatibility syntax.

Styling

Support React-like style objects:

JavaScript
<div
  style={{
    display: "grid",
    gap: "1rem",
    gridTemplateColumns: "1fr 1fr"
  }}
/>

Compile to:

HTML
<div style="display:grid;gap:1rem;grid-template-columns:1fr 1fr"></div>

Also support class composition:

JavaScript
<div
  className={cx(
    "card",
    props.selected && "card--selected",
    props.compact ? "card--compact" : null
  )}
/>

Hedron should provide a small set of built-in portable helpers:

cx()
clsx()
style()
url()
json()
Events need a deliberate distinction

This is where Hedron cannot simply imitate React, because React event handlers are browser-side JavaScript functions:

JavaScript
<button onClick={() => setCount(count + 1)}>

That does not fit a server-first, language-neutral system.

I would still use familiar event-like syntax, but make the semantics explicit.

HTMX server actions
JavaScript
<Button
  onClick={server.action("deleteUser", { userId: props.userId })}
>
  Delete
</Button>

Compiler output:

HTML
<button
  hx-delete="/users/123"
  hx-target="#users"
  hx-swap="outerHTML">
  Delete
</button>

Or more directly:

JavaScript
<Button
  hx-delete={`/users/${props.userId}`}
  hx-target="#users"
/>
Web Component events
JavaScript
<ontology-tree
  onNodeSelected={events.forward("ontologyNodeSelected")}
/>

The compiler can wire this to a declarative event bridge.

Avoid pretending arbitrary backend functions can be passed into the browser like React callbacks.

Components should look like React components

External template:

JavaScript
export component UserCard(props: UserCardProps) {
  return (
    <article className="user-card">
      <h2>{props.user.name}</h2>
      <p>{props.user.email}</p>
    </article>
  );
}

This is maximally familiar—but it also starts looking like actual JavaScript and creates parsing ambiguity.

A cleaner .hdn format would be:

JavaScript
<article className="user-card">
  <h2>{props.user.name}</h2>
  <p>{props.user.email}</p>
</article>

With the component identity and prop type supplied separately:

Python
Run
@component(template="UserCard.hdn")
class UserCardProps(BaseModel):
    user: User

This preserves JSX familiarity without pretending .hdn is JavaScript.

Recommended .hdn syntax contract

A React developer should be able to write:

JavaScript
<>
  <PageHeader title={props.title} />

  <main className="dashboard">
    {props.isLoading ? (
      <Spinner />
    ) : (
      props.cards.map(card => (
        <Card key={card.id} card={card} />
      ))
    )}
  </main>
</>

And understand it immediately.

The Hedron-specific concepts should be minimal:

JavaScript
<ServerAction
  method="delete"
  endpoint={`/users/${props.userId}`}
  target="#users"
>
  <Button variant="danger">Delete</Button>
</ServerAction>

or declarative primitives like:

JavaScript
<Button
  action={server.delete(`/users/${props.userId}`)}
  target="#users"
>
  Delete
</Button>
What not to copy from React

Hedron should copy JSX ergonomics, not React's runtime model.

Do not copy:

hooks

useEffect

client-side state as the default

virtual DOM

hydration requirements

JavaScript closures as props

framework-owned synthetic events

browser-only component execution

Hedron's equivalent mental model should be:

React:
props + state -> JSX -> virtual DOM

Hedron:
typed props + server data -> HDN -> HTML

For rich client state:

Web Component owns browser behavior
HTMX owns server interaction
Hedron owns structure and rendering
Best design principle

I would put this into the plan as a formal rule:

Hedron should maximize syntactic familiarity with JSX while minimizing semantic dependence on React.

That gives React developers a comfortable entry point without misleading them about how the framework actually operates.

The ideal reaction from a React developer should be:

“This looks like JSX, but it renders on the server and I don't need Node.”

## 31. You

Our react familiarity should not feel forced, only adopt react features that naturally fit into our framework

## 32. ChatGPT

Exactly. Hedron should not be “React syntax pasted onto a server framework.” It should feel familiar because the underlying ideas genuinely overlap.

The better principle is:

Adopt React conventions only where they express Hedron’s own model cleanly.

That means keeping the parts that naturally fit:

Component composition

Nested markup

Props

Children

Fragments

Self-closing components

Expression interpolation

Conditional rendering

List rendering

Stable keys where identity matters

Familiar component naming conventions

And avoiding features that would create false expectations:

Hooks

Client-side state as the default

Effect lifecycles

Function callbacks passed to the browser

Synthetic events

Virtual DOM semantics

Hydration assumptions

Arbitrary JavaScript execution

React-specific attribute quirks unless they serve a real purpose

A more natural .hdn design

This feels familiar without pretending to be JSX:

JavaScript
<Card title={props.title}>
  <p>{props.description}</p>

  {props.showActions && (
    <div class="actions">
      <Button href={props.editUrl}>Edit</Button>
    </div>
  )}
</Card>

The familiarity comes from:

tags

props

children

braces

composition

But the semantics remain Hedron-native.

For example, I would prefer standard HTML:

JavaScript
<label for="email" class="field-label">

over React-specific syntax:

JavaScript
<label htmlFor="email" className="field-label">

React uses className and htmlFor because JSX maps to JavaScript DOM properties. Hedron compiles directly to HTML, so standard HTML names are more natural.

Keep expressions familiar but constrained

This is probably appropriate:

JavaScript
{props.user.name}
{props.enabled && <Panel />}
{props.loading ? <Spinner /> : <Content />}

This may also be natural:

JavaScript
{props.users.map(user => (
  <UserCard key={user.id} user={user} />
))}

But only if the Hedron expression language truly supports first-class mapping cleanly.

A more portable Hedron-native alternative could be:

JavaScript
{for user in props.users}
  <UserCard key={user.id} user={user} />
{/for}

The decision should be based on compiler clarity and cross-language portability, not on which syntax looks most like React.

Children should stay

Children are not really a React-specific idea. They are a natural consequence of component composition.

JavaScript
<Card>
  <h2>Users</h2>
  <UserList users={props.users} />
</Card>

Inside the card:

JavaScript
<section class="card">
  {children}
</section>

That belongs in Hedron.

Fragments should stay

Fragments also solve a real structural problem:

JavaScript
<>
  <Header />
  <Main />
  <Footer />
</>

They avoid unnecessary wrapper elements. That is useful regardless of React.

key should exist only if Hedron uses it

Hedron should support key only when it has actual semantics, such as:

deterministic identity

incremental rendering

stable generated IDs

keyed fragment replacement

improved diagnostics

It should not exist merely because React developers expect it.

Events should look like Hedron

This would be misleading:

JavaScript
<Button onClick={() => deleteUser(props.userId)}>

It implies that a JavaScript closure will execute in the browser.

Prefer semantics that clearly express what Hedron does:

JavaScript
<Button
  hx-delete={`/users/${props.userId}`}
  hx-target="#users"
>
  Delete
</Button>

Or a typed server-action abstraction:

JavaScript
<Button
  action={server.deleteUser(userId=props.userId)}
  target="#users"
>
  Delete
</Button>

The second option can still feel component-oriented without pretending to be React.

The right design test

For every React-inspired feature, ask three questions:

Does this solve a real Hedron problem?

Can its semantics remain consistent across Python, Java, and Node?

Would a developer correctly predict what it does without knowing React internals?

If the answer is no, leave it out.

Revised positioning

Hedron should not promise:

JSX without React.

It should promise:

A server-native component language that feels familiar to developers who already know HTML and component-based frameworks.

React developers will feel at home, but HTML, Razor, Vue, Svelte, and template-engine developers should also find it intuitive.

The plan should state this explicitly:

Hedron values semantic clarity over superficial React compatibility. Familiar syntax is adopted where it naturally supports server-rendered component composition; React-specific runtime concepts are not reproduced.

## 33. You

Write an hdn design doc

## 34. ChatGPT

I wrote the first draft of the HDN design document as an RFC-style proposal.

It covers:

The philosophy of .hdn

Design goals

Core principles

Component model

Tag semantics (HTML vs Hedron components vs Web Components)

Expression philosophy

Children/composition

What HDN intentionally does not copy from React

HTMX integration

Web Component integration

Compilation pipeline

A guiding design rule

Future work

You can download it here:

📄
Hedron_HDN_Design_Document.docx

I also think we should treat HDN as a language rather than just a template format. I'd like the next iteration to be much more formal—closer to a language specification than framework documentation—with chapters such as:

Lexical grammar

Parsing rules

AST definition

Expression language

Type system

Component resolution

Rendering semantics

Whitespace rules

Escaping rules

Compiler passes

Error diagnostics

Formatting specification (like rustfmt or gofmt)

Language Server Protocol (LSP) support

Tree-sitter grammar

Editor integrations

Versioning and backwards compatibility

That would turn HDN into a well-defined language with a stable specification, making it much easier to build high-quality tooling and maintain compatibility over time.

Hedron_HDN_Design_Document.docx
Document

## 35. You

What if we added a future feature that can convert a react component and its sub components into hdx?

## 36. ChatGPT

That could be a very strong future feature.

Assuming you mean converting React components into HDN, I would frame it as a migration compiler, not a perfect universal transpiler.

The useful version

A command like:

Bash
hedron migrate-react src/components/UserCard.tsx

could:

Parse the selected React component.

Follow its local component imports.

Build a dependency graph.

Convert supported JSX into .hdn.

Extract props into Hedron contracts.

Flag React-specific behavior that needs manual redesign.

Emit a migration report.

Example input:

TypeScript
type UserCardProps = {
  name: string;
  email: string;
  isAdmin?: boolean;
};

export function UserCard({
  name,
  email,
  isAdmin = false,
}: UserCardProps) {
  return (
    <Card>
      <h2>{name}</h2>
      <p>{email}</p>

      {isAdmin && <Badge>Admin</Badge>}
    </Card>
  );
}

Possible output:

JavaScript
<Card>
  <h2>{props.name}</h2>
  <p>{props.email}</p>

  {props.isAdmin && <Badge>Admin</Badge>}
</Card>

And a generated Python contract:

Python
Run
class UserCardProps(BaseModel):
    name: str
    email: str
    is_admin: bool = False
Where conversion would work well

The converter could reliably handle:

JSX markup

props

destructured props

conditional rendering

ternaries

fragments

.map() list rendering

imported child components

static classes and styles

TypeScript prop interfaces

default prop values

basic helper functions

pure presentational components

That would cover a large number of design-system and dashboard components.

Where it becomes difficult

React components often mix markup with client runtime behavior:

TypeScript
const [open, setOpen] = useState(false);

useEffect(() => {
  fetchData();
}, []);

Those cannot simply become server-rendered HDN.

The converter would need to classify behavior.

Server action
TypeScript
onClick={() => deleteUser(id)}

Could become:

JavaScript
<Button
  hx-delete={`/users/${props.id}`}
  hx-target="#users"
>
  Delete
</Button>
Local browser state
TypeScript
const [open, setOpen] = useState(false);

Might become a Web Component:

JavaScript
<disclosure-panel open={props.open}>
  ...
</disclosure-panel>
Side effects
TypeScript
useEffect(...)

Would usually require manual review because it may belong in:

the backend route

HTMX lifecycle handling

a Web Component

application startup logic

Migration categories

Every converted component should receive a status:

AUTO_CONVERTED
CONVERTED_WITH_WARNINGS
WEB_COMPONENT_REQUIRED
SERVER_ACTION_REQUIRED
MANUAL_REWRITE_REQUIRED
UNSUPPORTED

That makes the tool trustworthy.

A report could look like:

UserCard.tsx
  ✓ JSX converted
  ✓ props converted
  ✓ child components converted

UserList.tsx
  ✓ map expression converted
  ⚠ key retained for stable identity

UserDialog.tsx
  ⚠ useState detected
  → generated Web Component migration stub

UserSearch.tsx
  ⚠ useEffect and fetch detected
  → manual server/HTMX redesign required
Component graph conversion

The subcomponent feature is especially valuable.

Given:

UserPage
├── UserHeader
├── UserCard
│   ├── Avatar
│   └── Badge
└── UserActions

The tool could migrate the whole graph:

Bash
hedron migrate-react UserPage.tsx --recursive

Output:

components/
├── UserPage.hdn
├── UserHeader.hdn
├── UserCard.hdn
├── Avatar.hdn
├── Badge.hdn
├── UserActions.hdn
└── contracts/
    ├── user_page.py
    ├── user_card.py
    └── user_actions.py

It should avoid converting third-party packages automatically. Instead:

<Card> from ./Card.tsx
    → convert

<Button> from @company/design-system
    → map using migration registry

<DatePicker> from external package
    → preserve as Web Component candidate or flag
Migration mappings

Hedron should support a configurable mapping file:

YAML
components:
  "@mui/material/Button":
    hedron_component: "Button"

  "@mui/material/Card":
    hedron_component: "Card"

  "@company/ui/DataGrid":
    web_component: "company-data-grid"

This would make design-system migrations much more practical.

Compiler architecture

The tool would likely need:

React/TypeScript parser
        ↓
React component graph
        ↓
React semantic IR
        ↓
Migration analysis
        ↓
Hedron component IR
        ↓
HDN + contracts + migration report

The important part is the React semantic intermediate representation. The converter should not perform simple text replacement.

It needs to understand:

imports

JSX elements

prop types

hooks

closures

event handlers

state

effects

context

child components

browser APIs

React concepts and likely Hedron targets
React concept	Hedron target
JSX markup	HDN
Props interface	Component contract
Children	Children
Fragment	Fragment
Conditional JSX	HDN condition
.map()	HDN list rendering
useState	Web Component or server state
useEffect	Backend or Web Component
Event callback	HTMX action or Web Component event
Context	Request/render context
CSS modules	Preserved or remapped styles
Client fetch	Backend route or HTMX request
React portal	Hedron layout/overlay component
Ref	Web Component concern
What not to promise

Do not promise:

Convert any React application automatically.

That would be unrealistic.

Promise:

Convert presentational React component trees automatically and produce guided migrations for stateful components.

That is achievable and still extremely useful.

Strong product positioning

This could become one of Hedron's biggest adoption features:

Bring your existing React component library. Hedron converts the server-compatible parts and tells you exactly what must move to HTMX or Web Components.

It also reinforces Hedron's design philosophy. Hedron is not trying to emulate React's runtime. It is helping teams preserve the valuable part—component structure and markup—while moving to a server-native architecture.

I would add this to the roadmap as:

React-to-Hedron Migration Toolkit

TSX/JSX parser

Recursive component graph analysis

TypeScript props-to-contract generation

JSX-to-HDN conversion

React hook classification

HTMX migration suggestions

Web Component stub generation

Design-system mapping registry

Structured migration report

IDE migration preview

That is ambitious, but technically coherent and potentially very compelling.

## 37. You

I don’t want to overwhelm new users with too much to learn up front. I’d like an easy mode that doesn’t require hdn to be written directly but if they want to have fine tune control they can be eased into wetting hdn and any other complicated code needed.

## 38. ChatGPT

That is the right product direction.

Hedron should have a progressive disclosure model:

Start with Python objects and sensible defaults. Introduce HDN only when the user needs deeper control.

Three authoring levels
1. Easy mode

The user writes only backend-language code.

Python
Run
from hedron import Page, Card, Text, Button

page = Page(
    title="Users",
    children=[
        Card(
            title="Team",
            children=[
                Text("Manage your users"),
                Button(
                    "Refresh",
                    hx_get="/users",
                    hx_target="#users",
                ),
            ],
        ),
    ],
)

No HDN. No schema files. No compiler concepts.

Hedron renders the standard component templates internally.

This should be enough for:

CRUD applications

dashboards

forms

admin tools

internal applications

ordinary HTMX workflows

2. Customization mode

Users override specific parts without owning the whole template.

Python
Run
Card(
    title="Team",
    variant="outlined",
    header=Badge("Admin"),
    footer=Button("Refresh"),
)

Or use styling and slot APIs:

Python
Run
Card(
    class_="team-card",
    slots={
        "header": TeamHeader(),
        "footer": TeamActions(),
    },
)

They still do not need to write HDN.

This level introduces:

props

children

slots

variants

design tokens

HTMX behavior

Web Component wrappers

3. HDN mode

When the standard component is no longer sufficient, users can eject or extend it.

Bash
hedron eject Card

Output:

components/
├── Card.hdn
└── card.py

Then they can edit:

JavaScript
<section class="card">
  {props.title && (
    <header class="card-header">
      <h2>{props.title}</h2>
    </header>
  )}

  <div class="card-body">
    {children}
  </div>

  {props.footer && (
    <footer class="card-footer">
      {props.footer}
    </footer>
  )}
</section>

The key is that users encounter HDN only when they have already learned why they need it.

The ideal learning path
Use components
    ↓
Configure components
    ↓
Compose components
    ↓
Use slots
    ↓
Override templates
    ↓
Write custom HDN components
    ↓
Add Web Components or compiler extensions

Each stage should be optional.

A user should be able to build a useful application without ever reaching the bottom.

Convention over configuration

Easy mode should rely heavily on conventions.

Python
Run
class UserForm(Form):
    model = User
    submit_to = "/users"

Hedron could infer:

fields

labels

validation messages

input types

submit behavior

HTMX endpoint

default layout

The user can gradually override:

Python
Run
class UserForm(Form):
    model = User
    submit_to = "/users"

    fields = {
        "email": EmailField(help_text="Work email only"),
        "role": SelectField(options=["admin", "user"]),
    }

Only advanced users need a custom template.

Pydantic should power easy mode

This is where Pydantic becomes especially valuable.

Python
Run
class User(BaseModel):
    name: str
    email: EmailStr
    active: bool = True

Then:

Python
Run
AutoForm(User)
AutoTable(User, rows=users)
AutoDetail(User, value=user)

Hedron can generate default components from the contract.

That gives new users an immediate payoff:

Python
Run
return Page(
    AutoTable(User, rows=users)
)
Built-in component templates

The standard component library should ship with internal HDN templates:

hedron-components/
├── Button.hdn
├── Card.hdn
├── Form.hdn
├── Table.hdn
├── Modal.hdn
└── Navbar.hdn

Easy-mode users consume those templates indirectly.

Advanced users can:

extend them

override them

eject them

replace them

author new ones

This keeps one rendering system underneath both beginner and advanced modes.

Avoid two separate frameworks

Easy mode must not become a separate implementation.

Bad architecture:

Python builder renderer
HDN renderer

That would create inconsistent behavior.

Better architecture:

Python easy-mode API
        ↓
Hedron component specification
        ↓
built-in HDN templates
        ↓
Rust renderer

Easy mode is simply a higher-level authoring surface over the same core.

Escape hatches

Users should be able to drop down one level at a time.

Insert native HTML
Python
Run
Html(
    "section",
    Html("h2", "Users"),
    Html("p", "Manage your users"),
)
Add raw attributes
Python
Run
Button(
    "Save",
    attrs={
        "data-controller": "save-button",
        "aria-describedby": "save-help",
    },
)
Use an inline fragment
Python
Run
HdnFragment("""
  <aside class="notice">
    {props.message}
  </aside>
""", props={"message": message})
Use a custom component
Python
Run
UserCard(user=user)
Eject the built-in template
Bash
hedron eject UserCard

Each escape hatch should be explicit and discoverable.

Documentation should follow the same progression

The first tutorial should not mention:

ASTs

compiler passes

canonical specifications

JNI

Web Component lifecycle

template grammar

It should look like:

Python
Run
from hedron import FastAPIApp, Page, Card, Button

app = FastAPIApp()

@app.page("/")
def home():
    return Page(
        Card(
            title="Hello",
            children=[
                Button("Load users", hx_get="/users"),
            ],
        )
    )

Then later guides introduce:

Component composition

Forms and Pydantic

HTMX

Slots and variants

Custom components

HDN

Web Components

Compiler and cross-language features

Recommended terminology

Avoid calling it “easy mode” in the public API because that can sound limited or amateur-oriented.

Use names like:

Declarative API

Component API

Standard authoring

Template authoring

Advanced authoring

For example:

Hedron Component API
Hedron HDN Templates
Hedron Browser Components
Product rule

The design document should include this principle:

Hedron must provide immediate value before requiring users to learn HDN. Every advanced capability should be reachable through a gradual, reversible transition from the standard component API.

That gives beginners a simple Python-first framework while preserving the depth and control needed for serious applications.

## 39. You

The pydantic models they write should not be made directly with pydantic. I’d like a basemodel subclass that they import from hedron that is limited to just what hedron supports

## 40. ChatGPT

Yes. Hedron should expose its own ComponentModel or Model base class and treat Pydantic as an implementation detail.

That gives us a controlled contract language:

Python
Run
from hedron import ComponentModel, Field


class UserCardProps(ComponentModel):
    name: str
    email: str
    is_admin: bool = False

Users get familiar Pydantic-style ergonomics, but Hedron controls what is legal.

Why this is better

Directly accepting arbitrary pydantic.BaseModel would make the component specification inherit all of Pydantic’s complexity:

custom validators

computed fields

serializers

arbitrary types

recursive models

discriminated unions

implementation-specific metadata

behavior that may not map cleanly to Java, TypeScript, or Rust

That would undermine the language-neutral specification.

Instead:

Hedron ComponentModel
        ↓
restricted Pydantic implementation
        ↓
canonical Hedron specification
Proposed API
Python
Run
from hedron import ComponentModel, Field
from typing import Literal


class ButtonProps(ComponentModel):
    label: str

    variant: Literal[
        "primary",
        "secondary",
        "danger",
    ] = "primary"

    disabled: bool = False

    title: str | None = None

Users should not need to import anything from Pydantic.

Python
Run
from hedron import ComponentModel, Field

Internally:

Python
Run
from pydantic import BaseModel as PydanticBaseModel


class ComponentModel(PydanticBaseModel):
    ...

But that inheritance should not become part of the public promise.

Supported type system

The first version should deliberately support a narrow portable subset:

str
bool
int
float
None
Literal
Enum
list[T]
dict[str, T]
T | None
nested ComponentModel
ComponentNode
list[ComponentNode]
TrustedHtml
URL-like Hedron types

Possibly later:

datetime
date
decimal
tagged unions
generic component data

Unsupported types should fail during model definition or compilation, not much later during rendering.

Python
Run
class BadProps(ComponentModel):
    callback: Callable[[], None]

Error:

HEDRON1007: unsupported component property type `Callable[[], None]`

Component properties must be representable in the Hedron specification.
Use a server action, event declaration, or browser component instead.
Hedron-owned Field

Hedron should wrap or replace Pydantic's Field:

Python
Run
from hedron import ComponentModel, Field


class SearchProps(ComponentModel):
    query: str = Field(
        default="",
        min_length=0,
        max_length=200,
        description="Current search query",
    )

Only supported options should be exposed.

For example:

Python
Run
Field(
    default=...,
    description=...,
    alias=...,
    min_length=...,
    max_length=...,
    minimum=...,
    maximum=...,
    pattern=...,
    deprecated=...,
)

Avoid exposing every Pydantic Field option unless Hedron can represent it portably.

Hedron-specific metadata

The same field API can carry rendering semantics:

Python
Run
class ButtonProps(ComponentModel):
    disabled: bool = Field(
        default=False,
        attribute="disabled",
        boolean_attribute=True,
    )

    variant: Literal["primary", "danger"] = Field(
        default="primary",
        class_map={
            "primary": "button button--primary",
            "danger": "button button--danger",
        },
    )

Or keep contract and rendering metadata more explicitly separated:

Python
Run
from hedron import ComponentModel, prop


class ButtonProps(ComponentModel):
    disabled: bool = prop.boolean_attribute("disabled", default=False)

    variant: Literal["primary", "danger"] = prop.class_variant(
        default="primary",
        mapping={
            "primary": "button--primary",
            "danger": "button--danger",
        },
    )

I prefer a small set of semantic helpers over an enormous generic Field signature.

Suggested public model classes

Avoid calling everything BaseModel, because users may confuse it with Pydantic.

A clear public hierarchy could be:

Python
Run
from hedron import Model, Props, EventPayload
Python
Run
class User(Model):
    id: str
    name: str


class UserCardProps(Props):
    user: User


class UserSelected(EventPayload):
    user_id: str

Underneath:

HedronModel
├── Model
├── Props
├── EventPayload
├── ActionInput
└── ActionResult

They can share the same restricted type compiler while expressing intent.

My preferred names are:

Python
Run
HedronModel
ComponentProps
EventPayload

Example:

Python
Run
from hedron import HedronModel, ComponentProps


class User(HedronModel):
    id: str
    name: str


class UserCardProps(ComponentProps):
    user: User
    compact: bool = False
Enforce restrictions at class creation

Do not wait until someone runs the CLI.

Python
Run
class ReportProps(ComponentProps):
    data: pandas.DataFrame

This should fail immediately when Python creates the class:

TypeError: ReportProps.data uses unsupported Hedron type `pandas.DataFrame`.

Convert the value to a supported Hedron model or collection before passing it as a component property.

That can be implemented with __pydantic_init_subclass__ or a metaclass-level validation pass.

Conceptually:

Python
Run
class HedronModel(PydanticBaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        validate_hedron_fields(cls)
Restrict configuration

Users should not be able to alter serialization semantics unpredictably.

Hedron should own the configuration:

Python
Run
class HedronModel(PydanticBaseModel):
    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=False,
        validate_assignment=True,
        frozen=False,
        populate_by_name=True,
    )

Potentially prohibit overriding important options:

Python
Run
class BadProps(ComponentProps):
    model_config = ConfigDict(arbitrary_types_allowed=True)

Error:

Hedron model configuration cannot enable `arbitrary_types_allowed`.
Validators

This needs a deliberate policy.

Basic validators are useful:

Python
Run
class Percentage(ComponentProps):
    value: int

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: int) -> int:
        if not 0 <= value <= 100:
            raise ValueError("must be between 0 and 100")
        return value

But arbitrary Python validators cannot be represented in the cross-language specification.

I would support two categories.

Portable constraints

These compile into the Hedron specification:

Python
Run
value: int = Field(minimum=0, maximum=100)
Runtime-only validators

These work in Python but produce a portability warning:

Python
Run
@python_validator("value")
def validate_value(...):
    ...

Or disallow them in portable components entirely.

A clean mode system might be:

Python
Run
class LocalSearchProps(ComponentProps, portability="python"):
    ...

versus:

Python
Run
class SharedButtonProps(ComponentProps, portability="portable"):
    ...

For the MVP, I would simply disallow custom validators on component contracts. Add them later only when the portability behavior is well defined.

Conversion API

Every Hedron model should compile directly:

Python
Run
spec = UserCardProps.hedron_spec()
Python
Run
UserCardProps.export_spec("UserCard.props.json")

Potential methods:

Python
Run
UserCardProps.hedron_schema()
UserCardProps.hedron_spec()
UserCardProps.validate_portability()

But new users should rarely need to call these. The component decorator and build process handle it automatically:

Python
Run
from hedron import component


@component(template="UserCard.hdn")
class UserCardProps(ComponentProps):
    user: User
Standard authoring experience

Easy mode:

Python
Run
from hedron import ComponentProps, component


@component
class Alert(ComponentProps):
    message: str
    kind: Literal["info", "warning", "error"] = "info"

If no .hdn template is supplied, Hedron can use:

a built-in renderer

a registered component implementation

an inferred standard component

or a Python component body

Advanced mode:

Python
Run
@component(template="Alert.hdn")
class AlertProps(ComponentProps):
    message: str
    kind: Literal["info", "warning", "error"] = "info"

Both compile through the same specification.

Important naming distinction

I would separate domain data models from component property contracts:

Python
Run
from hedron import Model, Props


class User(Model):
    id: str
    name: str


class UserCardProps(Props):
    user: User
    compact: bool = False

That is concise and approachable.

Python
Run
from hedron import Model, Props, Field

No Pydantic import appears in user documentation.

Recommended rule for the design document

Hedron exposes a constrained model system inspired by Pydantic. The public API supports only types, constraints, and behaviors that Hedron can validate and represent consistently. Pydantic is the initial Python implementation mechanism, not part of the portable Hedron specification.

That gives us the ergonomics of Pydantic without allowing Pydantic to define the boundaries of the framework.

## 41. You

Rewrite the hedron plan with this pydantic idea and the starter new person concepts too
2/2

## 42. ChatGPT

I rewrote the plan to reflect the direction we've converged on.

The biggest changes are:

Progressive disclosure is now a core design principle. New users start with a simple Python API and only learn HDN when they actually need it.

Hedron owns the model layer. Users no longer import pydantic.BaseModel; instead they import Props, Model, and Field from Hedron. Pydantic becomes an internal implementation detail.

The beginner experience is treated as a first-class feature rather than an afterthought.

The learning path is explicitly defined from beginner to advanced.

HDN is positioned as an advanced authoring tool, not a requirement.

The React philosophy is clarified: adopt only those concepts that naturally fit Hedron rather than chasing compatibility.

You can download it here:

📄
Hedron_Architecture_Plan_v3.docx

I think we've also uncovered something that should become one of Hedron's guiding principles:

Every feature in Hedron should have a "beginner path" and an "expert path."

For example:

Beginner	Expert
Props	Generated Hedron Component Specification
Built-in components	Custom .hdn templates
Auto-generated layouts	Hand-authored HDN
Standard component library	Custom component libraries
HTMX attributes	Custom Web Components
Automatic rendering	Compiler plugins
Python API	Cross-language code generation

The important part is that both paths use the same architecture. A beginner isn't using a "toy mode"—they're simply using higher-level abstractions over the exact same compiler and runtime. I think that philosophy will make Hedron much more approachable while still giving experienced developers room to grow.

Hedron_Architecture_Plan_v3.docx
Document

## 43. You

As a brand new framework, competition will be fierce and adoption will be our biggest hurdle

## 44. ChatGPT

I think that's exactly the right concern to optimize for now—not technical elegance, but time-to-first-success.

Most frameworks don't fail because they're technically inferior. They fail because a developer doesn't get to the point where they experience the advantages.

I think Hedron needs a "30-second rule"

A brand new user should be able to install it and build something useful in under 30 seconds.

Python
Run
from hedron import App, Page, Card, Button

app = App()

@app.page("/")
def home():
    return Page(
        Card(
            title="Hello, Hedron!",
            children=[
                Button("Click me")
            ]
        )
    )

If they can see that in a browser immediately, they're hooked.

Notice what they didn't have to learn:

HDN

Rust

HTMX

Web Components

Component specifications

ASTs

Rendering engines

Those become "nice, now let me show you something even cooler."

I think we should completely rethink the documentation

Instead of organizing by technology:

Models
Templates
Compiler
HTMX
Web Components

Organize by developer maturity.

Day 1

Install Hedron

First page

Buttons

Forms

Tables

Never mention HDN.

Day 2

Components

Props

Layout

Themes

Still no HDN.

Week 1

Eventually the developer asks:

"Can I customize this Card?"

Now documentation says:

Absolutely.

Here's how to override the template.

That's when HDN appears.

Month 1

The user thinks:

I wish this component had client-side drag-and-drop.

Now they discover Web Components.

Month 6

Now they care about:

compiler plugins

language bindings

generated specifications

That's expert territory.

HDN should feel like an optimization

Not a requirement.

This reminds me of Rust.

You don't start by learning:

procedural macros

unsafe

pinning

allocators

You write:

Rust
println!("Hello");

Only later do you discover the advanced features.

Hedron should follow the same philosophy.

I actually think we should hide Pydantic too

Even though Hedron uses it internally.

Users write:

Python
Run
from hedron import Props

class UserProps(Props):
    ...

Not

Python
Run
from pydantic import BaseModel

Because psychologically they're learning Hedron, not Pydantic.

Later they might discover:

Oh... this is powered by Pydantic.

Exactly like FastAPI users eventually realize:

Oh... that's Starlette underneath.

Every feature should answer one question

Instead of:

Here's HDN.

Documentation should say:

Are the built-in components not flexible enough?

If "yes":

Here's HDN.

Likewise:

Do you need browser-side state?

If "yes":

Here's Web Components.

Everything should be pull-based rather than push-based.

This gives Hedron a huge marketing advantage

Imagine the homepage.

Current frameworks:

Learn JSX.

Learn hooks.

Learn effects.

Learn hydration.

Learn routing.

Learn build tooling.

Hedron:

Install.

Return components from your FastAPI route.

That's it.

Everything else can wait.

I think we should adopt one design philosophy

I would actually put this at the very top of the architecture document.

The Principle of Progressive Disclosure

Hedron is designed so developers can remain productive without learning its advanced features. Every capability should be introduced only when the developer has encountered the problem it solves.

I think that becomes one of Hedron's defining characteristics.

One more thought

I also think the CLI should become a teacher.

Instead of making users read docs, it should suggest the next step.

Example:

Bash
$ hedron new dashboard

Later:

Bash
$ hedron inspect Card

Output:

Card is currently using the built-in template.

Need more control?

Run:

    hedron eject Card

to create a local Card.hdn template.

Or:

This page contains a large interactive table.

You may benefit from converting it into a Web Component.

Learn more:

    hedron learn web-components

That turns the framework into a mentor rather than expecting developers to absorb the whole architecture up front.

I think this may actually become Hedron's strongest differentiator. Not the Rust compiler, not HDN, and not the component specification—but the fact that you can be productive on day one while still having a path to expert-level control without switching frameworks.

## 45. You

Hedron seems like it would benefit from being tightly connected to FastApi

## 46. ChatGPT

Yes—Python adoption probably depends on Hedron feeling like a natural extension of FastAPI, not a separate framework layered awkwardly beside it.

FastAPI already gives Hedron the exact foundation it needs:

routing

dependency injection

request validation

forms

response types

middleware

lifespan management

OpenAPI

Starlette’s ASGI foundation

FastAPI also supports returning custom Response objects and declaring custom response classes, so Hedron can integrate cleanly without modifying FastAPI itself.
FastAPI
+1

Recommended product structure

I would separate the universal project from the flagship Python integration:

Hedron
├── hedron-spec
├── hedron-compiler
├── hedron-render
├── hedron-python
└── hedron-fastapi

But the normal Python install should be:

Bash
pip install hedron

That package should install or expose the FastAPI integration by default.

The user experience should not begin with:

Python
Run
from fastapi import FastAPI
from hedron_fastapi import HedronRenderer
from hedron.responses import HedronResponse

It should begin with:

Python
Run
from hedron import Hedron

app = Hedron()

Internally, Hedron can subclass or configure FastAPI.

Option A: Hedron subclasses FastAPI
Python
Run
from hedron import Hedron, Page, Card, Button

app = Hedron()


@app.page("/")
def home():
    return Page(
        Card(
            title="Hello",
            children=[
                Button("Load users", hx_get="/users"),
            ],
        )
    )

Conceptually:

Python
Run
from fastapi import FastAPI


class Hedron(FastAPI):
    ...

This gives the simplest beginner experience.

Users still retain FastAPI:

Python
Run
@app.get("/api/users")
def users() -> list[User]:
    return load_users()

And Hedron pages:

Python
Run
@app.page("/users")
def users_page():
    return UserPage(users=load_users())

The distinction is intuitive:

@app.get()   → ordinary FastAPI endpoint
@app.page()  → Hedron HTML page
Option B: regular FastAPI plus a Hedron router

Advanced users may already have an application:

Python
Run
from fastapi import FastAPI
from hedron.fastapi import HedronRouter

app = FastAPI()
pages = HedronRouter()


@pages.page("/")
def home():
    return Page(...)


app.include_router(pages)

FastAPI preserves router and route behavior when routers are included, and it supports custom APIRoute classes, which gives Hedron a legitimate extension point for specialized route behavior.
FastAPI
+2
FastAPI
+2

We should support both:

New project:
    Hedron()

Existing FastAPI project:
    HedronRouter()
Hedron component responses

A route should be able to return a component directly:

Python
Run
@app.page("/users")
def users_page():
    return UserList(users=get_users())

Hedron converts it into:

Python
Run
HedronResponse(
    content=renderer.render(component),
    media_type="text/html",
)

For streamed pages:

Python
Run
HedronStreamingResponse(component)

FastAPI supports both custom HTML responses and streaming response classes, so these can remain standard ASGI responses rather than proprietary runtime objects.
FastAPI
+1

Full pages versus HTMX fragments

The integration should automatically recognize HTMX requests.

Python
Run
@app.page("/users")
def users_page(request: Request):
    return UserPage(users=get_users())

For an ordinary browser request:

HTML
<!doctype html>
<html>
    ...
    <body>
        <main>...</main>
    </body>
</html>

For an HTMX request:

HTML
<section id="users">...</section>

A possible API:

Python
Run
@app.page(
    "/users",
    layout=AppLayout,
)
def users_page():
    return UserList(users=get_users())

Hedron handles:

full document rendering for normal navigation

fragment rendering for HX-Request

layout omission for fragments

appropriate Vary headers

HTMX redirect and refresh headers

title and history updates

The user should not have to write duplicate routes.

Dependency injection should remain native FastAPI

This is critical. Hedron must not invent its own service container.

Python
Run
from fastapi import Depends
from hedron import Page


@app.page("/users/{user_id}")
def user_page(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_user),
):
    return UserDetail(
        user=service.get(user_id),
        viewer=current_user,
    )

That preserves one of FastAPI’s strongest features rather than wrapping or obscuring it.

Hedron models and FastAPI request models

Hedron’s restricted model types should integrate with FastAPI without becoming interchangeable with every API model.

Python
Run
from hedron import Model, Props, FormModel

Possible distinctions:

Python
Run
class User(Model):
    id: int
    name: str


class UserCardProps(Props):
    user: User


class CreateUser(FormModel):
    name: str
    email: Email

Then:

Python
Run
@app.action("/users")
def create_user(data: CreateUser):
    ...

FastAPI already supports validated models for request bodies and form models. Hedron can use compatible internals while exposing its restricted portable API.
FastAPI
+1

However, we should not force all FastAPI API models to inherit from Hedron.

A normal API should still work:

Python
Run
from pydantic import BaseModel


class ExternalApiPayload(BaseModel):
    ...

The boundary should be:

Hedron models for Hedron components, forms, actions, and portable contracts

ordinary Pydantic models for unrestricted FastAPI APIs

Typed actions

FastAPI integration gives Hedron an opportunity to improve on raw HTMX attributes.

Beginner mode:

Python
Run
@app.action("/users/{user_id}/delete")
def delete_user(user_id: int):
    remove_user(user_id)
    return UserList(users=get_users())

Component:

Python
Run
Button(
    "Delete",
    action=delete_user.bind(user_id=user.id),
    target="#users",
)

Hedron could compile this into the correct:

HTML
<button
    hx-delete="/users/42/delete"
    hx-target="#users"
>
    Delete
</button>

This would provide:

route-aware URL generation

typed parameters

method validation

automatic CSRF support

fewer handwritten endpoint strings

refactoring safety

Advanced users can still write raw HTMX:

Python
Run
Button(
    "Delete",
    hx_delete=f"/users/{user.id}/delete",
    hx_target="#users",
)
FastAPI form integration

A major adoption feature could be:

Python
Run
class CreateUser(FormModel):
    name: str
    email: Email
    role: Literal["admin", "member"] = "member"

Then:

Python
Run
@app.page("/users/new")
def new_user():
    return AutoForm(
        CreateUser,
        submit=create_user,
    )

Hedron can infer:

labels

input controls

required fields

select options

server validation

inline errors

HTMX submission

focus behavior after errors

accessible descriptions

That creates a compelling reason for FastAPI developers to try Hedron.

Validation-error rendering

FastAPI normally expresses request validation errors as JSON. Hedron should translate form-action validation failures into rendered component errors when the request originated from a Hedron form.

For example:

HTML
<label for="email">Email</label>
<input
    id="email"
    name="email"
    aria-invalid="true"
    aria-describedby="email-error"
>
<p id="email-error">Enter a valid email address.</p>

The same validation rules power:

API errors

form errors

generated docs

Hedron specification constraints

Lifespan integration

Hedron’s compiler registry and built-in templates should initialize through FastAPI’s lifespan mechanism, which is the currently recommended FastAPI approach for startup and shutdown behavior.
FastAPI

Conceptually:

Python
Run
app = Hedron(
    components="components/",
    development=True,
)

During lifespan startup:

load built-in component specifications

compile .hdn files

build the component registry

initialize file watching in development

load design-system configuration

During shutdown:

stop watchers

release native renderer resources

flush diagnostics or caches

Suggested Python API
Simplest application
Python
Run
from hedron import Hedron, Page, Card, Text

app = Hedron()


@app.page("/")
def home():
    return Page(
        Card(
            title="Welcome",
            children=[
                Text("Built with Hedron and FastAPI.")
            ],
        )
    )
Existing FastAPI application
Python
Run
from fastapi import FastAPI
from hedron.fastapi import HedronRouter

app = FastAPI()
ui = HedronRouter()


@ui.page("/")
def home():
    return HomePage()


app.include_router(ui)
API and UI together
Python
Run
@app.get("/api/users", response_model=list[UserResponse])
def users_api():
    return get_users()


@app.page("/users")
def users_page():
    return UserTable(rows=get_users())

This co-location is a major selling point.

The strategic positioning

I would describe the relationship as:

Hedron is to FastAPI UI development what FastAPI is to Python API development: typed, declarative, approachable, and progressively extensible.

But Hedron should remain architecturally capable of supporting other backends.

The layers should be:

Hedron specification and compiler
            ↓
language runtime
            ↓
framework integration

Python:
    Hedron → FastAPI

Java:
    Hedron → Spring Boot

Node:
    Hedron → Fastify / Express

FastAPI should be the flagship integration, not a dependency baked into the universal specification.

Recommended priority

For adoption, I would narrow the initial public identity to:

Hedron: component-based HTML and HTMX applications for FastAPI.

Do not lead with:

cross-language component specifications

JNI

Node bindings

compiler architecture

universal design systems

Those are important long-term architecture, but they do not give a new Python user an immediate reason to install the package.

The first launch should win one specific audience:

FastAPI developers who need modern server-rendered interfaces without Node.js.

If Hedron becomes excellent at that, the Rust core and neutral specification give it room to expand later. Starting with a broad “all backend languages” message would make the project seem ambitious but less immediately relevant.

Sources

## 47. You

Now that we’ve dug in more into pydantic and fastapi as first class integrations. I think writing our core logic in rust would over complicate things to start. Future rust offloading should be a future idea.

## 48. ChatGPT

I agree. Rust-first is now the wrong MVP architecture.

The Rust core made sense when Hedron was primarily envisioned as a cross-language renderer. But the product has become much more clearly:

A typed, component-based HTML and HTMX framework designed first for FastAPI developers.

That changes the priorities.

Why Python-first is better

A Rust core would immediately introduce:

PyO3 and native-extension complexity

platform-specific wheels

cross-compilation and release automation

harder debugging and tracebacks

FFI conversion costs

duplicated Python/Rust type representations

slower experimentation with component semantics

extra friction for contributors

None of that helps validate the most important questions:

Is the component API enjoyable?

Does the restricted Props model feel natural?

Does FastAPI integration feel seamless?

Are built-in components sufficient for beginners?

Is HDN worth learning when users need more control?

Does the HTMX abstraction remove meaningful boilerplate?

Those should be answered in Python first.

Revised architecture
Hedron Python
├── FastAPI integration
├── Hedron model system
├── Component API
├── HTML renderer
├── HTMX integration
├── HDN parser/compiler
├── Built-in components
└── Web Component integration

Everything begins as normal Python.

Python
Run
from hedron import Hedron, Page, Card, Button

app = Hedron()

@app.page("/")
def home():
    return Page(
        Card(
            title="Welcome",
            children=[
                Button("Load users", hx_get="/users")
            ],
        )
    )

Internally:

Python component objects
        ↓
Python component tree
        ↓
Python renderer
        ↓
HTML response

That is enough for an MVP.

The specification should remain—but internal

We should not abandon the canonical component representation. We should just avoid overformalizing it too early.

A Python-first representation could use Hedron's restricted model system:

Python
Run
class ComponentSpec(HedronInternalModel):
    name: str
    tag: str | None
    props: dict[str, PropSpec]
    children: ChildrenSpec
    slots: dict[str, SlotSpec]
    template: TemplateSpec

This provides a clean internal boundary without forcing us to publish a language-neutral standard in version 0.1.

Later, once the Python API has stabilized:

Python internal component representation
        ↓ stabilized through real usage
Portable Hedron Specification
        ↓
Java / Node / Rust implementations

The specification should emerge from a successful framework, not dictate an untested one.

Python renderer design

The first renderer can be straightforward and optimized later.

Python
Run
class Node:
    def render(self, context: RenderContext) -> str:
        raise NotImplementedError
Python
Run
class Element(Node):
    def __init__(
        self,
        tag: str,
        *,
        attrs: dict[str, object] | None = None,
        children: list[Node | str] | None = None,
    ):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = children or []

Rendering can initially use efficient list accumulation:

Python
Run
def render_element(element: Element) -> str:
    output: list[str] = []
    render_into(element, output)
    return "".join(output)

This will likely be fast enough for normal FastAPI applications. Rendering HTML strings is rarely the dominant bottleneck compared with database queries and network calls.

HDN should also begin in Python

The HDN parser does not initially need to be a sophisticated native compiler.

Version one could use:

a Python tokenizer

a recursive-descent parser

Python dataclass AST nodes

compile-time validation

cached template programs

HDN source
    ↓
Python parser
    ↓
HDN AST
    ↓
validated render plan
    ↓
Python renderer

For production:

Python
Run
@lru_cache
def compile_template(path: Path) -> CompiledTemplate:
    ...

Templates are parsed once and reused.

We could use a parsing library initially, but a small custom parser may eventually be preferable because HDN's syntax should remain deliberately constrained.

Hedron models become easier

Because Hedron is Python-first, the restricted Pydantic-backed API can be implemented directly:

Python
Run
from hedron import Props, Field

class UserCardProps(Props):
    name: str
    email: str
    compact: bool = False

Internally:

Python
Run
class Props(PydanticBaseModel):
    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=False,
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        validate_hedron_model(cls)

There is no FFI boundary or Rust type translation to complicate this.

FastAPI should become the center

The initial package architecture should probably be:

hedron/
├── app.py
├── routing.py
├── responses.py
├── models/
│   ├── base.py
│   ├── props.py
│   ├── forms.py
│   └── fields.py
├── components/
│   ├── base.py
│   ├── html.py
│   ├── forms.py
│   ├── layout.py
│   └── data.py
├── rendering/
│   ├── renderer.py
│   ├── attributes.py
│   ├── escaping.py
│   └── context.py
├── hdn/
│   ├── lexer.py
│   ├── parser.py
│   ├── ast.py
│   ├── compiler.py
│   └── diagnostics.py
├── htmx/
│   ├── requests.py
│   ├── responses.py
│   ├── actions.py
│   └── headers.py
└── webcomponents/
    ├── component.py
    └── events.py
A better roadmap
Phase 1: prove the beginner experience

Build only:

Hedron() FastAPI subclass

HedronRouter

@app.page

direct component responses

basic HTML components

layouts

HTMX attributes

HTML escaping

static asset serving

development reload

No HDN compiler is required to prove this phase.

Phase 2: typed forms and models

Add:

Model

Props

FormModel

Hedron Field

supported-type validation

AutoForm

inline validation errors

typed actions

This is likely Hedron's strongest FastAPI-specific differentiator.

Phase 3: composition and customization

Add:

slots

variants

themes

design tokens

component inheritance or wrapping

native HTML escape hatches

built-in component inspection

Phase 4: HDN

Only after the Python component model is stable:

.hdn parser

expressions

children

conditionals

iteration

template overrides

hedron eject

syntax highlighting

At this point, HDN will be designed around real limitations users encountered instead of imagined ones.

Phase 5: browser components

Add:

Web Component helpers

event bridging

lifecycle integration

packaged browser component library

client-state guidance

Phase 6: performance profiling

Measure real applications:

page render time

allocation count

template compilation time

large-table rendering

concurrency

memory usage

Only then decide whether Rust is justified.

Where Rust may eventually help

Rust should be treated as an optimization backend, not the architecture.

Potential candidates:

HTML escaping

large component-tree rendering

HDN parsing

template compilation

static analysis

source-map generation

formatter

language server

incremental compilation

A future package might look like:

hedron
└── pure Python implementation

hedron-native
└── optional Rust accelerator

Installation:

Bash
pip install hedron

Optional acceleration:

Bash
pip install "hedron[native]"

Runtime detection:

Python
Run
try:
    from hedron_native import render as native_render
except ImportError:
    native_render = python_render

The output and semantics must remain identical.

Preserve a clean optimization boundary

Even in Python, structure the implementation so selected parts can later move to Rust.

Python
Run
class RendererProtocol(Protocol):
    def render(self, node: Node, context: RenderContext) -> str:
        ...

Implementations:

Python
Run
class PythonRenderer:
    ...

class NativeRenderer:
    ...

Likewise:

Python
Run
class TemplateCompilerProtocol(Protocol):
    def compile(self, source: str) -> CompiledTemplate:
        ...

That keeps future Rust acceleration possible without making it today's burden.

Cross-language support should become aspirational

I would remove Java and Node bindings from the near-term roadmap.

They can remain part of the long-term vision, but Hedron should earn the right to become cross-language by first becoming excellent for Python.

The public positioning should now be:

Hedron is a typed, component-based framework for building FastAPI interfaces with HTML, HTMX, and progressive enhancement.

Not:

A universal cross-language rendering engine.

The latter may eventually emerge, but the former is concrete, understandable, and immediately useful.

Updated guiding principle

Hedron begins as a pure-Python FastAPI framework. Native acceleration and cross-language implementations are introduced only after profiling and real-world usage demonstrate a clear need.

That is a much lower-risk plan. It improves contributor accessibility, accelerates iteration, simplifies packaging, and aligns the implementation with Hedron's actual first audience.

## 49. You

While fastapi will be our core app dependency. I  still want developers to be able to use hedron with flask and jango

## 50. ChatGPT

Yes—FastAPI should be Hedron’s flagship integration, not its architectural prison.

The clean approach is to split Hedron into a framework-neutral core plus thin adapters:

hedron
├── components
├── rendering
├── models
├── hdn
├── htmx
└── responses

hedron-fastapi
hedron-flask
hedron-django

For Python packaging, these could still ship together initially:

Bash
pip install hedron

with optional extras:

Bash
pip install "hedron[fastapi]"
pip install "hedron[flask]"
pip install "hedron[django]"

I’m assuming “jango” means Django. Django is the established Python web framework; “Jango” appears to refer mainly to unrelated products.
Wikipedia
+1

Framework-neutral core

The core should know nothing about:

FastAPI decorators

Flask application contexts

Django views

ASGI versus WSGI

framework-specific request objects

It should accept component trees and return a neutral rendered result:

Python
Run
from hedron import Page, Card, Button, render

component = Page(
    Card(
        title="Users",
        children=[
            Button("Refresh", hx_get="/users")
        ],
    )
)

html = render(component)

A richer result type could carry headers and metadata:

Python
Run
result = render(component)

result.html
result.status_code
result.headers
result.title

Each adapter converts that into its framework’s response type.

FastAPI integration

FastAPI remains the best beginner experience:

Python
Run
from hedron.fastapi import Hedron
from hedron import Page, Card

app = Hedron()

@app.page("/")
def home():
    return Page(
        Card(title="Hello from FastAPI")
    )

FastAPI-specific features can include:

@app.page

typed actions

dependency injection

automatic form validation

async rendering

request models

OpenAPI-aware action generation

ASGI streaming

This should be the integration shown on the homepage and in the primary tutorial.

Flask integration

Flask users should be able to add Hedron without changing how their application is structured:

Python
Run
from flask import Flask
from hedron.flask import Hedron
from hedron import Page, Card

app = Flask(__name__)
ui = Hedron(app)

@app.get("/")
def home():
    return ui.render(
        Page(
            Card(title="Hello from Flask")
        )
    )

Or with a decorator:

Python
Run
@app.get("/")
@ui.page
def home():
    return Page(
        Card(title="Hello from Flask")
    )

Flask support should integrate with:

Flask request context

blueprints

sessions

url_for

flash messages

synchronous views

Flask-WTF optionally, without requiring it

Hedron should not try to replace Flask’s application model.

Django integration

Django needs a more idiomatic adapter because its conventions differ more significantly:

Python
Run
from hedron.django import page
from hedron import Page, Card

@page
def home(request):
    return Page(
        Card(title="Hello from Django")
    )

URL configuration remains ordinary Django:

Python
Run
from django.urls import path
from .views import home

urlpatterns = [
    path("", home, name="home"),
]

Class-based views should also work:

Python
Run
from hedron.django import HedronView

class UserPage(HedronView):
    component = UserList

    def get_props(self, request):
        return {
            "users": User.objects.all(),
        }

Django-specific features could eventually include:

URL reversing

middleware compatibility

Django forms and model forms

CSRF integration

authentication context

messages framework

Django ORM querysets

template context processors

async views where supported

Django already has its own forms and template ecosystem, so Hedron should complement it rather than pretend those features do not exist.

Shared component code

The most important promise is that the same component should work across all three:

Python
Run
from hedron import Props, component

class UserCardProps(Props):
    name: str
    email: str

@component
def UserCard(props: UserCardProps):
    return Card(
        title=props.name,
        children=[
            Text(props.email)
        ],
    )

Then:

Python
Run
# FastAPI
@app.page("/user")
def user_page():
    return UserCard(name="Ada", email="ada@example.com")
Python
Run
# Flask
@app.get("/user")
@ui.page
def user_page():
    return UserCard(name="Ada", email="ada@example.com")
Python
Run
# Django
@page
def user_page(request):
    return UserCard(name="Ada", email="ada@example.com")

The framework adapter should affect routing and responses—not component semantics.

Request abstraction

Some custom components will need request information. Hedron should provide a small portable request context rather than exposing a FastAPI Request everywhere:

Python
Run
from hedron import current_request

request = current_request()

request.method
request.path
request.query
request.headers
request.is_htmx
request.user

Adapters populate this from:

Starlette/FastAPI request

Flask request proxy

Django HttpRequest

Framework-native request access should still be available when necessary:

Python
Run
request.native

But portable Hedron components should avoid depending on it.

Actions need an adapter interface

Typed actions should be framework-neutral at the component level:

Python
Run
Button(
    "Delete",
    action=DeleteUser(user_id=user.id),
    target="#users",
)

Each adapter resolves the action into its routing system:

FastAPI → route name and dependency injection
Flask   → endpoint and url_for
Django  → named URL and reverse()

That suggests an internal protocol:

Python
Run
class FrameworkAdapter(Protocol):
    def make_response(self, rendered: RenderedPage): ...
    def get_request_context(self) -> RequestContext: ...
    def reverse_url(self, action: ActionBinding) -> str: ...
    def validate_form(self, model_type, request): ...
Core dependency question

There is one important wording distinction.

If FastAPI is a required dependency of the base hedron package, Flask and Django users will be forced to install FastAPI and Starlette even when they never use them. That weakens the framework-neutral story.

I would instead make:

Pydantic a core implementation dependency.

FastAPI the default integration and recommended extra.

hedron-fastapi the flagship adapter.

Flask and Django optional integrations.

The default onboarding command could still be:

Bash
pip install "hedron[fastapi]"

or a convenience metapackage:

Bash
pip install hedron-fastapi

The branding remains FastAPI-first without coupling every user to FastAPI.

Recommended positioning

Publicly:

Hedron is a component framework for Python web applications, with first-class FastAPI integration and support for Flask and Django.

In the main tutorial:

Build a FastAPI interface in five minutes.

In secondary guides:

Add Hedron to an existing Flask application.

Use Hedron components in Django views.

Share a Hedron design system across multiple Python frameworks.

That gives Hedron a clear beachhead without excluding a large part of the Python web ecosystem.

Sources

## 51. You

Let’s maybe have flask and Django users have to install a separate package like hedron-flask that doesn’t install fastapi

## 52. ChatGPT

Yes. That is the cleaner packaging model.

Recommended package structure
hedron-core
hedron-fastapi
hedron-flask
hedron-django

Public installs:

Bash
pip install hedron-fastapi
pip install hedron-flask
pip install hedron-django

Each adapter depends on hedron-core, but only installs its own web framework.

hedron-fastapi
├── hedron-core
├── fastapi
└── starlette

hedron-flask
├── hedron-core
└── flask

hedron-django
├── hedron-core
└── django

That avoids making Flask and Django users install FastAPI unnecessarily.

PyPI naming

Because you already own hedron on PyPI, I would use it as the lightweight core package:

hedron          → framework-neutral component system
hedron-fastapi  → flagship FastAPI integration
hedron-flask    → Flask integration
hedron-django   → Django integration

Then Python users write shared component code with:

Python
Run
from hedron import Card, Button, Props

Framework setup comes from the adapter:

Python
Run
from hedron.fastapi import Hedron

The distribution can be named hedron-fastapi while its import namespace remains under hedron.fastapi.

That gives users one coherent namespace rather than this:

Python
Run
from hedron_fastapi import Hedron
Namespace layout
hedron/
├── components/
├── models/
├── rendering/
├── hdn/
├── htmx/
├── context/
└── protocols/

The adapter distributions contribute:

hedron/fastapi/
hedron/flask/
hedron/django/

From the user’s perspective:

Python
Run
from hedron import Page, Card, Button
from hedron.fastapi import Hedron

or:

Python
Run
from hedron import Page, Card, Button
from hedron.flask import HedronFlask

or:

Python
Run
from hedron import Page, Card, Button
from hedron.django import page
FastAPI example
Bash
pip install hedron-fastapi
Python
Run
from hedron import Button, Card, Page
from hedron.fastapi import Hedron

app = Hedron()


@app.page("/")
def home():
    return Page(
        Card(
            title="Welcome",
            children=[
                Button("Load users", hx_get="/users"),
            ],
        )
    )
Flask example
Bash
pip install hedron-flask
Python
Run
from flask import Flask
from hedron import Card, Page
from hedron.flask import HedronFlask

app = Flask(__name__)
ui = HedronFlask(app)


@app.get("/")
@ui.page
def home():
    return Page(
        Card(title="Welcome")
    )
Django example
Bash
pip install hedron-django
Python
Run
from hedron import Card, Page
from hedron.django import page


@page
def home(request):
    return Page(
        Card(title="Welcome")
    )
Internal adapter contract

All adapters should implement the same internal protocol:

Python
Run
class FrameworkAdapter(Protocol):
    def make_response(self, result: RenderResult): ...

    def request_context(self) -> RequestContext: ...

    def reverse_url(
        self,
        route_name: str,
        **params: object,
    ) -> str: ...

    def is_htmx_request(self) -> bool: ...

    def parse_form(self, model_type: type[FormModel]): ...

This keeps the renderer and component system independent from any framework.

Development repository

I would keep everything in one monorepo initially:

hedron/
├── packages/
│   ├── hedron/
│   ├── hedron-fastapi/
│   ├── hedron-flask/
│   └── hedron-django/
├── examples/
│   ├── fastapi/
│   ├── flask/
│   └── django/
└── tests/
    └── adapter-conformance/

A monorepo gives you:

synchronized releases

shared tests

easier refactoring

one documentation site

one issue tracker

consistent adapter behavior

You can still publish four separate distributions from it.

Release strategy

Initially, keep versions synchronized:

hedron 0.1.0
hedron-fastapi 0.1.0
hedron-flask 0.1.0
hedron-django 0.1.0

The adapters can require compatible core versions:

TOML
dependencies = [
    "hedron>=0.1,<0.2",
    "flask>=3.0",
]

Once the project matures, adapters can release independently if necessary.

Product positioning

I would lead with:

Hedron is a component framework for Python web applications. FastAPI is the flagship integration, with dedicated Flask and Django adapters.

The primary documentation and homepage should still feature FastAPI, because Hedron needs a clear initial audience. Flask and Django support should look intentional and first-class, but not dilute the initial message.

This packaging structure gives you both: a focused FastAPI story and a genuinely framework-neutral core.

## 53. You

Let’s make hedron install fastapi and hedron-core be the package hedron-flask and hedron-django install.

## 54. ChatGPT

Yes. That packaging model is cleaner for adoption because the obvious package name gives users the flagship experience.

Recommended package layout
hedron
hedron-core
hedron-flask
hedron-django

Dependencies:

hedron
├── hedron-core
├── fastapi
└── starlette

hedron-flask
├── hedron-core
└── flask

hedron-django
├── hedron-core
└── django

This gives you:

Bash
pip install hedron

for the primary FastAPI experience, while Flask and Django users install:

Bash
pip install hedron-flask
pip install hedron-django

without pulling in FastAPI.

Import design

The shared API should still come from hedron where possible:

Python
Run
from hedron import Page, Card, Button, Props

For Flask and Django, the adapter packages can provide their own top-level namespaces:

Python
Run
from hedron_flask import HedronFlask
from hedron_django import page

However, there is an important packaging limitation: hedron-flask cannot safely install modules into the hedron namespace unless you deliberately use namespace-package techniques. I would avoid that complexity initially.

So the public imports could be:

FastAPI
Python
Run
from hedron import Hedron, Page, Card
Flask
Python
Run
from hedron_core import Page, Card
from hedron_flask import HedronFlask
Django
Python
Run
from hedron_core import Page, Card
from hedron_django import page

That works technically, but it weakens the brand because Flask and Django users must import hedron_core.

Better import model

Use hedron-core as the distribution name, but have it install the Python package named hedron_core only internally, while each adapter re-exports the public component API.

For Flask:

Python
Run
from hedron_flask import HedronFlask, Page, Card, Button, Props

For Django:

Python
Run
from hedron_django import page, Page, Card, Button, Props

For FastAPI:

Python
Run
from hedron import Hedron, Page, Card, Button, Props

Each adapter re-exports the same shared classes from hedron-core.

Internally:

Python
Run
# hedron_flask/__init__.py
from hedron_core import Button, Card, Page, Props
from .app import HedronFlask

This keeps each onboarding path coherent.

Package responsibilities
hedron-core

Framework-neutral implementation:

hedron_core/
├── components/
├── models/
├── rendering/
├── hdn/
├── htmx/
├── actions/
├── context/
└── protocols/

It should not depend on FastAPI, Flask, or Django.

hedron

Flagship FastAPI package:

hedron/
├── app.py
├── routing.py
├── responses.py
├── forms.py
├── dependencies.py
└── static.py

It depends on hedron-core and re-exports the core API.

hedron-flask
hedron_flask/
├── extension.py
├── routing.py
├── responses.py
├── forms.py
└── context.py
hedron-django
hedron_django/
├── decorators.py
├── views.py
├── responses.py
├── forms.py
└── middleware.py
User experience
FastAPI
Bash
pip install hedron
Python
Run
from hedron import Hedron, Page, Card

app = Hedron()

@app.page("/")
def home():
    return Page(
        Card(title="Hello")
    )
Flask
Bash
pip install hedron-flask
Python
Run
from flask import Flask
from hedron_flask import HedronFlask, Page, Card

app = Flask(__name__)
hedron = HedronFlask(app)

@app.get("/")
@hedron.page
def home():
    return Page(
        Card(title="Hello")
    )
Django
Bash
pip install hedron-django
Python
Run
from hedron_django import page, Page, Card

@page
def home(request):
    return Page(
        Card(title="Hello")
    )
Monorepo structure
hedron/
├── packages/
│   ├── hedron-core/
│   ├── hedron/
│   ├── hedron-flask/
│   └── hedron-django/
├── examples/
│   ├── fastapi/
│   ├── flask/
│   └── django/
└── tests/
    └── adapter-conformance/
Versioning

Keep all four packages synchronized initially:

hedron-core 0.1.0
hedron 0.1.0
hedron-flask 0.1.0
hedron-django 0.1.0

Dependencies should be pinned to the same minor series:

TOML
dependencies = [
    "hedron-core>=0.1,<0.2",
    "fastapi>=0.116",
]

The exact FastAPI minimum should be selected when implementation begins rather than guessed now.

Recommendation

This is the strongest packaging strategy:

hedron is the batteries-included FastAPI framework. hedron-core is the framework-neutral engine. hedron-flask and hedron-django are complete alternative distributions built on the same core.

The only thing I would avoid is making Flask and Django users import directly from hedron_core. Re-export the shared component API from each adapter package so every audience gets a clean, single-package experience.

## 55. You

Rewrite the hedron plan with these ideas

## 56. ChatGPT

Worked for 1m 26s

The rewritten plan now reflects the full current direction:

Python-first implementation, with Rust deferred until profiling proves a need

hedron as the batteries-included FastAPI distribution

hedron-core as the framework-neutral engine

Separate hedron-flask and hedron-django packages that do not install FastAPI

Hedron-owned Model, Props, FormModel, and Field APIs backed internally by Pydantic

Beginner-first component authoring with progressive disclosure

HDN as an advanced customization path rather than an onboarding requirement

Shared framework-adapter protocols and conformance testing

HTMX and Web Component responsibilities

Adoption strategy, package layout, implementation phases, non-goals, and early success criteria

Optional future native acceleration through a separate hedron-native path

Hedron_Architecture_and_Adoption_Plan_v4.docx

Hedron_Architecture_and_Adoption_Plan_v4.docx
Document

## 57. You

Making our components into fastapi endpoints makes me excited for how this makes them feel even more like react components and how we can organize them and point to a folder of components and have it treat them as endpoints

## 58. ChatGPT

I think you may have stumbled onto something that's actually more interesting than the original idea.

Instead of thinking of Hedron as "a component library," think of it as a component application server.

React has this mental model:

Component
    ↓
Rendered by React
    ↓
HTML

Hedron could become:

Component
    ↓
FastAPI endpoint
    ↓
HTML or HTMX fragment

That's a very natural mapping.

Imagine this

Project structure:

app/
├── pages/
│   ├── home.py
│   └── users.py
│
├── components/
│   ├── UserCard.py
│   ├── UserTable.py
│   ├── Dashboard.py
│   └── Navbar.py

Startup:

Python
Run
app = Hedron(
    components="app/components",
)

Hedron automatically discovers:

UserCard
UserTable
Dashboard
Navbar

Each becomes part of the component registry.

Components become addressable

Every component could have an optional endpoint.

Python
Run
class UserCard(Props):
    user_id: int

Automatically:

/_hedron/components/UserCard

POST:

JSON
{
  "user_id": 42
}

Returns:

HTML
<article class="user-card">
...
</article>

That opens up a lot of possibilities.

HTMX becomes almost automatic

Instead of:

Python
Run
Button(
    hx_get="/users/card?id=42",
)

you write:

Python
Run
Button(
    component=UserCard(user_id=42),
)

Hedron knows:

component name

props

route

Generates:

HTML
<button
    hx-get="/_hedron/components/UserCard?user_id=42"
    hx-target="#..."
>

The developer never writes the URL.

Components become reusable services

Now imagine:

Python
Run
UserTable(users=users)

or

Python
Run
component.render()

or

Python
Run
component.url()

Every component knows how to:

render inline

expose itself as an endpoint

refresh itself

generate its own HTMX URL

That's a really elegant abstraction.

Component organization becomes familiar

React developers already think in folders:

components/

Hedron could do the same.

components/
├── users/
│   ├── Card.py
│   ├── Table.py
│   └── Detail.py
│
├── layout/
│   ├── Sidebar.py
│   └── Navbar.py

Automatic routing:

/_hedron/users/card
/_hedron/users/table
/_hedron/users/detail

No manual registration.

This also solves live updates

Suppose:

Python
Run
UserTable(
    users=users,
)

The refresh button doesn't need a URL.

It already knows.

Python
Run
RefreshButton(
    target=UserTable
)

Compiler:

HTML
<button
    hx-get="/_hedron/users/table"

The component owns its own refresh endpoint.

Components become deployable units

You could eventually imagine packages like:

hedron-auth
hedron-admin
hedron-crud
hedron-blog

Each ships:

components/

Hedron discovers them automatically.

Very React-like.

Component-local assets

This also gives a nice organization story.

UserCard/
    component.py
    template.hdn
    styles.css
    browser.js

Very similar to React.

But server-first.

One thing I'd change

I would avoid making every component an endpoint automatically.

Some components are just presentation.

Python
Run
Avatar
Icon
Badge

They don't need routes.

Instead:

Python
Run
@component
class UserCard(...):
    ...

Only becomes an endpoint when you opt in.

Maybe:

Python
Run
@page_component
class UserTable(...):
    ...

or

Python
Run
class UserTable(Component):
    endpoint = True

Or simply:

Python
Run
@component(endpoint=True)

Then Hedron generates:

/_hedron/components/UserTable

Presentation components stay lightweight.

I think the biggest insight

The thing that excites me most isn't actually the endpoint.

It's this:

A Hedron component is both a Python object and an addressable resource.

React components are just functions.

Hedron components could be:

Python objects

renderable

refreshable

addressable

discoverable

typed

composable

That's a richer model.

One architectural suggestion

I'd introduce a distinction between two kinds of components:

Renderable Component

Can be embedded inside other components.

Purely compositional.

Addressable Component

Everything above.

Plus it owns a route.

Can render independently.

Can be targeted by HTMX.

Can refresh itself.

Can be lazy-loaded.

Can be linked to directly.

That keeps the simple components simple while giving larger UI sections powerful capabilities. It also aligns well with the way people naturally break applications into reusable widgets and page regions.

## 59. You

This works perfectly with how htmx works

## 60. ChatGPT

I think this is where Hedron starts to become its own thing instead of "FastAPI + components."

You're right: HTMX's unit of composition is the endpoint. React's unit of composition is the component.

Hedron can unify those.

React
Component
      ↓
JSX
      ↓
Virtual DOM

HTMX
Endpoint
      ↓
HTML Fragment

Hedron
Component
      ↓
Endpoint
      ↓
HTML Fragment

That feels remarkably natural.

The endpoint disappears

Today in HTMX you write:

HTML
<button
    hx-get="/users/table"
    hx-target="#table">

The URL is an implementation detail.

In Hedron, the component is the abstraction.

Python
Run
Button(
    "Refresh",
    target=UserTable()
)

The compiler determines:

UserTable
↓
endpoint
↓
URL
↓
HTMX attribute

The developer never types the endpoint.

Components become self-refreshing

Imagine:

Python
Run
UserTable(
    users=users
)

Inside the component:

Python
Run
RefreshButton()

Hedron already knows the component's endpoint.

It could simply mean:

Refresh me.

No URL.

No endpoint lookup.

No string interpolation.

Nested components become beautiful
Python
Run
Dashboard(
    children=[
        UserTable(),
        Statistics(),
        RecentOrders(),
    ]
)

Each component could independently expose:

/_hedron/dashboard/user-table
/_hedron/dashboard/statistics
/_hedron/dashboard/recent-orders

Now HTMX naturally updates each independently.

Lazy loading becomes almost free

React:

JavaScript
<Suspense>
    <UserTable />
</Suspense>

Hedron:

Python
Run
UserTable(
    lazy=True
)

Compiler:

HTML
<div
    hx-get="/_hedron/components/UserTable"
    hx-trigger="load">
</div>

That feels incredibly elegant.

Polling

Today:

HTML
<div
    hx-get="/metrics"
    hx-trigger="every 5s">

Hedron:

Python
Run
Metrics(
    poll="5s"
)

Compiler:

component endpoint
+
poll interval
=
correct HTMX
Infinite scrolling
Python
Run
UserTable(
    infinite_scroll=True
)

Compiler:

hx-trigger="revealed"

Again...

No endpoint.

Just:

Load more of this component.

Component state becomes endpoint state

This is interesting.

Python
Run
UserTable(
    page=2,
    search="John"
)

Those props become query parameters.

/_hedron/components/UserTable

?page=2
&search=John

Exactly how HTMX wants to work.

Components become bookmarkable

Every addressable component has a URL.

Dashboard
    ↓

Statistics
    ↓

endpoint

That means components can be:

linked

refreshed

embedded

cached

tested

All independently.

This also solves testing

Instead of Selenium:

Render Dashboard

Find UserTable

Hope it works

You can simply test:

GET /_hedron/components/UserTable

Assert HTML.

That's fantastic.

Discovery

Imagine:

hedron routes

Output:

Dashboard
    /

UserTable
    /_hedron/components/UserTable

Statistics
    /_hedron/components/Statistics

Navbar
    (internal)

Instant introspection.

Component registry

Now the registry becomes incredibly useful.

Component Registry

UserTable
    endpoint ✓

Statistics
    endpoint ✓

Button
    endpoint ✗

Avatar
    endpoint ✗

HTMX integration almost writes itself.

I think this is the killer feature

I actually think we've found Hedron's elevator pitch.

Not:

React for Python.

Not:

HTMX framework.

But:

Hedron turns components into first-class HTTP resources.

That sentence is unique.

React components aren't HTTP resources.

HTMX endpoints aren't reusable components.

Hedron bridges those two ideas.

One suggestion

I wouldn't expose raw endpoints publicly by default.

Instead I'd think of them as component resources.

For example:

Component
    ↓
Resource
    ↓
Endpoint

The endpoint is just one transport.

Later...

The exact same resource could be rendered:

inside FastAPI

inside Flask

inside Django

during static site generation

by a CLI renderer

in unit tests

So I think the architecture should revolve around:

Every addressable Hedron component is a resource that can be rendered through multiple transports. HTTP is simply the first transport.

I think that's an even stronger long-term abstraction because it leaves room for future capabilities without tying the component model exclusively to web requests.

## 61. You

Rewrite our hedron plan document with these ideas in mind

## 62. ChatGPT

I rewrote the plan around what I think is Hedron's clearest identity so far.

The biggest changes are:

FastAPI-first rather than merely FastAPI-compatible.

hedron, hedron-core, hedron-flask, and hedron-django package strategy.

Hedron-owned model system (Props, Model, FormModel, Field) with Pydantic hidden behind the public API.

Progressive disclosure as a core product philosophy.

Addressable Components as the major architectural innovation:

Components become HTTP resources.

HTMX URLs are generated automatically.

Components can refresh, lazy-load, poll, and be tested independently.

Separation between Renderable Components and Addressable Components.

Rust moved to the long-term roadmap as an optimization rather than the foundation.

You can download it here:

📄
Hedron_Architecture_Plan_v5.docx

I also think we've reached a point where Hedron has a genuinely distinct architectural idea:

React made components the unit of composition. HTMX made endpoints the unit of interaction. Hedron makes components the unit of interaction by turning addressable components into HTTP resources.

That's a much stronger story than "React for Python" or "another HTMX framework." It's an idea that can shape everything else in the framework—from the API to the CLI to testing, documentation, and even future tooling.

Hedron_Architecture_Plan_v5.docx
Document

## 63. You

I also love the idea of endpoint functions returning hedron components and also type annotated with the hedron component and the underlying code converting it to an html string in the same way fastapi endpoints convert pydantic models to json

## 64. ChatGPT

That should be a first-class Hedron feature, not just a convenience.

The mental model is excellent:

Python
Run
@app.get("/users/{user_id}")
def user_card(user_id: int) -> UserCard:
    user = load_user(user_id)
    return UserCard(user=user)

FastAPI sees the return annotation, Hedron sees that UserCard is a component type, and the integration converts the returned component into an HTML response automatically.

Conceptually:

Pydantic return model
    ↓
FastAPI serialization
    ↓
JSON response

Hedron return component
    ↓
Hedron rendering
    ↓
HTML response
The ideal API
Python
Run
from hedron import Hedron, Card, Props

app = Hedron()


class UserCardProps(Props):
    name: str
    email: str


class UserCard(Card):
    props = UserCardProps


@app.get("/users/{user_id}")
def user_card(user_id: int) -> UserCard:
    user = get_user(user_id)

    return UserCard(
        name=user.name,
        email=user.email,
    )

The developer should not need:

Python
Run
return HTMLResponse(render(component))

or:

Python
Run
return HedronResponse(component)

The type annotation and returned object should be enough.

This fits FastAPI naturally

FastAPI already inspects:

parameter annotations

request models

dependency annotations

response models

return values

Hedron can extend the response path so that when the returned value is a Hedron component, it becomes:

Python
Run
HTMLResponse(
    content=hedron.render(component),
    media_type="text/html",
)

That preserves the FastAPI experience instead of introducing a parallel routing model.

Two supported styles

Hedron should support both ordinary FastAPI decorators and the more explicit page decorator.

Normal FastAPI endpoint
Python
Run
@app.get("/users/{user_id}")
def user_card(user_id: int) -> UserCard:
    return UserCard(user=get_user(user_id))

Hedron infers HTML rendering from the return type or value.

Hedron page endpoint
Python
Run
@app.page("/users/{user_id}")
def user_page(user_id: int) -> UserPage:
    return UserPage(user=get_user(user_id))

@app.page can add page-specific behavior:

layout wrapping

document metadata

full-page versus HTMX fragment handling

navigation headers

default text/html

component route registration

The regular @app.get path remains useful for fragments and incremental adoption.

Return annotation semantics

The return type should communicate the endpoint contract.

Python
Run
def users() -> UserTable:
    ...

means:

endpoint returns HTML

rendered root component is UserTable

OpenAPI should not claim JSON

Hedron can validate the returned component type

tooling can discover which component owns the endpoint

A mismatch should produce a clear error:

Python
Run
def users() -> UserTable:
    return UserCard(...)

Possible diagnostic:

HEDRON2104: endpoint declared return type UserTable
but returned UserCard.

Return a UserTable, change the annotation, or annotate with Component.
Base return types

Users should be able to choose how specific they want to be.

Python
Run
def endpoint() -> UserCard:
    ...

Strict component type.

Python
Run
def endpoint() -> Component:
    ...

Any Hedron component.

Python
Run
def endpoint() -> Component | Response:
    ...

Component or explicit framework response.

Python
Run
def endpoint() -> UserCard | RedirectResponse:
    ...

Useful for authentication and redirects.

Hedron should preserve explicit response objects unchanged.

Async endpoints

This should work identically:

Python
Run
@app.get("/users/{user_id}")
async def user_card(user_id: int) -> UserCard:
    user = await user_service.get(user_id)
    return UserCard(user=user)

Rendering can remain synchronous initially unless HDN rendering later supports async values or streams.

Automatic fragment behavior

This gets especially elegant with HTMX.

Python
Run
@app.get("/users")
def users() -> UserTable:
    return UserTable(rows=get_users())

A normal request could render the component as returned.

An HTMX request also gets the same fragment directly.

For page components:

Python
Run
@app.page("/dashboard")
def dashboard() -> Dashboard:
    return Dashboard(...)

Hedron can return:

a full document for a normal browser request

only the component fragment for HX-Request: true

The endpoint still returns the same Dashboard object.

Response metadata

Components may need to influence the HTTP response without becoming response objects.

For example:

Python
Run
return UserTable(
    rows=users,
).with_response(
    status_code=200,
    headers={"HX-Trigger": "usersLoaded"},
)

Or a dedicated wrapper:

Python
Run
return ComponentResponse(
    UserTable(rows=users),
    headers={"HX-Trigger": "usersLoaded"},
)

I would keep plain component returns as the default and use ComponentResponse only for advanced response control.

OpenAPI integration

This is important.

FastAPI should not document Hedron endpoints as JSON responses. Hedron should generate:

Content-Type: text/html

and ideally include useful component metadata through an OpenAPI extension:

JSON
{
  "x-hedron-component": "UserCard",
  "x-hedron-addressable": true
}

That could power:

generated docs

component explorer

route inspection

IDE tooling

testing utilities

The visible API docs could say:

GET /users/{user_id}
Returns: UserCard
Media type: text/html
Component props as endpoint input

The symmetry gets even better if Hedron can also derive endpoint parameters from component props.

Python
Run
class UserCardProps(Props):
    user_id: int
    compact: bool = False


@app.component("/users/card")
def user_card(props: UserCardProps) -> UserCard:
    user = get_user(props.user_id)
    return UserCard(
        user=user,
        compact=props.compact,
    )

For a GET request:

/users/card?user_id=42&compact=true

FastAPI validates the input, and Hedron renders the output.

However, for beginner ergonomics, ordinary function parameters are probably clearer:

Python
Run
def user_card(
    user_id: int,
    compact: bool = False,
) -> UserCard:
    ...

The props-model form should be available when useful, not mandatory.

Automatic response conversion

The integration path should conceptually behave like:

Python
Run
async def serialize_endpoint_result(
    value: object,
    return_annotation: object,
    request: Request,
) -> Response:
    if isinstance(value, Response):
        return value

    if isinstance(value, Component):
        return render_component_response(
            value,
            request=request,
            expected_type=return_annotation,
        )

    return fastapi_default_serialization(value)

Hedron must not interfere with ordinary JSON endpoints:

Python
Run
@app.get("/api/users")
def users_api() -> list[UserResponse]:
    return get_users()

That should remain normal FastAPI behavior.

Components as endpoint contracts

This creates a deeper idea:

A Hedron component type is both a rendering type and an HTTP response contract.

For example:

Python
Run
@app.get("/users/{id}")
def user_card(id: int) -> UserCard:
    ...

describes:

route inputs

output component

output media type

render behavior

HTMX fragment identity

testing target

component ownership

That is more expressive than returning a generic HTMLResponse.

Testing becomes clean
Python
Run
def test_user_card(client):
    response = client.get("/users/42")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert 'class="user-card"' in response.text

Hedron could also expose component-aware assertions:

Python
Run
response = client.get_component("/users/42")

response.assert_component(UserCard)
response.assert_prop("name", "Ada")

That might rely on development-only metadata or rendered markers.

Recommended design rule

The plan should include:

Hedron components may be returned directly from FastAPI endpoints. Hedron detects component return values and component return annotations, validates the endpoint contract, renders the component, and returns an HTML response through FastAPI’s normal response pipeline.

This may be one of the strongest pieces of the framework because it makes Hedron feel like a genuine extension of FastAPI:

Python
Run
JSON endpoint:
def endpoint() -> UserModel

HTML endpoint:
def endpoint() -> UserCard

Same framework, same dependency injection, same annotations, different representation.

## 65. You

Add this to our plan document

## 66. ChatGPT

I updated the architecture plan to incorporate what I think is one of Hedron's defining ideas:

FastAPI endpoints can return Hedron components directly.

Return type annotations define the HTML contract, analogous to how Pydantic models define JSON contracts in FastAPI.

Hedron automatically:

Detects returned components

Renders them to HTML

Produces the correct HTML response

Validates the returned component against the annotated type

Leaves normal JSON endpoints untouched

The plan also keeps the ideas we've developed around:

Python-first architecture

FastAPI-first distribution

hedron-core with separate Flask and Django adapters

Hedron-owned model system

Progressive disclosure

HDN as an advanced feature

Addressable Components as HTTP resources

Future Rust acceleration only after profiling

You can download it here:

📄
Hedron_Architecture_Plan_v6.docx

I also think we've identified what should probably become Hedron's primary tagline:

"JSON endpoints return models. HTML endpoints return components."

It's immediately understandable to every FastAPI developer, maps directly onto how they already think about request/response models, and communicates Hedron's core value in a single sentence.

Hedron_Architecture_Plan_v6.docx
Document

## 67. You

But of course, if the user prefers to use fastapi directly with hedron, they would need to wrap the component return with html response

## 68. ChatGPT

Exactly. We should distinguish between two integration levels:

Using Hedron()

Python
Run
from hedron import Hedron

app = Hedron()

@app.get("/users/{user_id}")
def user_card(user_id: int) -> UserCard:
    return UserCard(user=get_user(user_id))

Here Hedron extends FastAPI’s response handling, so direct component returns work automatically.

Using plain FastAPI()

Python
Run
from fastapi import FastAPI
from hedron import HTML, UserCard

app = FastAPI()

@app.get("/users/{user_id}", response_class=HTML)
def user_card(user_id: int) -> HTML:
    return HTML(
        UserCard(user=get_user(user_id))
    )

Or more explicitly:

Python
Run
from fastapi.responses import HTMLResponse
from hedron import render

@app.get("/users/{user_id}", response_class=HTMLResponse)
def user_card(user_id: int) -> HTMLResponse:
    component = UserCard(user=get_user(user_id))
    return HTMLResponse(render(component))

I would make the Hedron wrapper concise:

Python
Run
return HTML(UserCard(...))

rather than requiring users to call the renderer and construct HTMLResponse manually.

Recommended contract

The plan should state:

Direct component returns are a feature of the Hedron FastAPI subclass and Hedron-aware routers. When using an unmodified FastAPI application, developers explicitly wrap components in Hedron’s HTML response type.

That preserves FastAPI’s normal behavior and avoids surprising global monkey-patching.

A clean API might be:

Python
Run
from hedron import ComponentResponse
Python
Run
@app.get("/users/{user_id}")
def user_card(user_id: int) -> ComponentResponse:
    return ComponentResponse(
        UserCard(user=get_user(user_id))
    )

My preference is ComponentResponse for the formal type and a shorter alias for convenience:

Python
Run
from hedron import HTML

return HTML(UserCard(...))

So the two paths are clear:

Hedron() + component return
    → automatic conversion

FastAPI() + HTML(component)
    → explicit conversion

That is a good boundary: seamless when users choose Hedron’s application integration, explicit when they choose to stay entirely within native FastAPI.

## 69. You

Update the plan document with this idea

## 70. ChatGPT

I updated the architecture plan to include the dual integration strategy, which I think is the cleanest design.

The new plan now explicitly distinguishes between:

1. Hedron Application (recommended)
Python
Run
app = Hedron()

@app.get("/users/{id}")
def user(id: int) -> UserCard:
    return UserCard(user=get_user(id))

Components are returned directly.

Hedron automatically renders them to HTML.

Component return annotations become HTML contracts, analogous to FastAPI's JSON response models.

2. Existing FastAPI Application
Python
Run
app = FastAPI()

@app.get("/users/{id}")
def user(id: int):
    return HTML(
        UserCard(user=get_user(id))
    )

No monkey-patching or hidden behavior.

Existing FastAPI applications can adopt Hedron incrementally.

Developers explicitly opt into HTML rendering with Hedron's response wrapper.

I also updated the guiding principle to reflect this:

JSON endpoints return models. HTML endpoints return components. When using Hedron(), component rendering is automatic. When using plain FastAPI(), rendering is explicit through Hedron's HTML response wrapper.

You can download the updated document here:

📄
Hedron_Architecture_Plan_v7.docx

I think this is a much stronger architectural boundary than trying to transparently modify every FastAPI application. It gives new projects a very ergonomic experience while making Hedron easy to adopt incrementally in existing FastAPI codebases.

Hedron_Architecture_Plan_v7.docx
Document

## 71. You

How can we add more automatic intuitive behavior to the hedron first app development experience?

## 72. ChatGPT

The Hedron-first experience should feel like FastAPI with UI awareness, not a separate framework users must constantly configure.

The best automatic behavior is behavior Hedron can infer reliably from types, component structure, HTTP semantics, and HTMX conventions.

1. Automatically distinguish pages from fragments
Python
Run
app = Hedron()

@app.page("/users")
def users() -> UsersPage:
    return UsersPage(users=get_users())

For a normal browser request, Hedron renders:

HTML
<!doctype html>
<html>
  ...
  <body>
    <main>...</main>
  </body>
</html>

For an HTMX request, it returns only the component fragment.

The endpoint author should not need:

Python
Run
if request.headers.get("HX-Request"):
    ...

The same returned component should work for both.

2. Infer the response type from the return annotation
Python
Run
@app.get("/users")
def users() -> UserTable:
    return UserTable(rows=get_users())

Hedron should infer:

text/html

expected root component

component-aware OpenAPI metadata

rendering pipeline

development-time return-type validation

Meanwhile, ordinary FastAPI behavior remains unchanged:

Python
Run
@app.get("/api/users")
def users_api() -> list[User]:
    return get_users()

No decorator distinction should be required for basic fragment endpoints.

3. Automatically register addressable components

Users could point Hedron at component modules:

Python
Run
app = Hedron(
    components="app.components",
)

Or multiple locations:

Python
Run
app = Hedron(
    component_packages=[
        "app.components",
        "shared_ui.components",
    ],
)

Hedron discovers only explicitly exported or decorated addressable components:

Python
Run
from hedron import addressable


@addressable
class UserTable(Component):
    ...

Then it registers a stable internal route without making every tiny component an endpoint.

4. Component references instead of URL strings

This should be one of the strongest automatic behaviors.

Instead of:

Python
Run
Button(
    "Refresh",
    hx_get="/_hedron/components/user-table?page=1",
    hx_target="#users",
)

Users write:

Python
Run
Button(
    "Refresh",
    refresh=UserTable(page=1),
    target="#users",
)

Or:

Python
Run
UserTable(
    rows=users,
    refreshable=True,
)

Hedron knows:

the component route

the HTTP method

how to serialize props

the default target

the appropriate swap mode

This removes fragile URL strings from the UI layer.

5. Self-refreshing components

Addressable components should be able to refer to themselves.

Python
Run
class UserTable(AddressableComponent):
    def render(self) -> Component:
        return Section(
            RefreshButton(),
            Table(...),
        )

Inside an addressable component:

Python
Run
RefreshButton()

could automatically mean:

HTML
<button
  hx-get="this component's URL"
  hx-target="closest [data-hedron-component]"
  hx-swap="outerHTML">

No endpoint or target required.

6. Automatic stable component identity

Hedron should generate consistent attributes:

HTML
<section
  id="hedron-user-table-a84f"
  data-hedron-component="UserTable"
  data-hedron-key="team-users">

Users may provide a key:

Python
Run
UserTable(
    key="team-users",
    rows=users,
)

This enables automatic:

refresh targeting

loading indicators

out-of-band swaps

debugging

component-aware testing

future incremental updates

The IDs should be deterministic within a render, but users should not normally need to see them.

7. Sensible HTMX defaults

HTMX is simple, but repeated attribute decisions still create friction. Hedron should provide semantic behavior.

Python
Run
Button(
    "Delete",
    action=delete_user.bind(user_id=user.id),
)

Hedron should infer:

method: DELETE

confirmation when configured by the action

target: nearest owning addressable component

swap: outerHTML

disabled/loading behavior while submitting

CSRF handling

error target

Users can override any inferred value.

Python
Run
Button(
    "Delete",
    action=delete_user.bind(user_id=user.id),
    target="#user-list",
    swap="innerHTML",
)
8. Typed actions instead of endpoint strings
Python
Run
@app.action(
    "/users/{user_id}",
    method="delete",
)
def delete_user(user_id: int) -> UserTable:
    remove_user(user_id)
    return UserTable(rows=get_users())

Then:

Python
Run
Button(
    "Delete",
    action=delete_user(user_id=user.id),
)

The action binding should be declarative—not execute the function immediately.

It provides:

route-safe URL generation

validated route parameters

known HTTP method

known return component

automatic HTMX wiring

better refactoring support

9. Automatic form generation from Hedron models
Python
Run
from hedron import FormModel, Field


class CreateUser(FormModel):
    name: str
    email: str
    role: Literal["admin", "member"] = "member"
    active: bool = True

Then:

Python
Run
Form(
    CreateUser,
    submit=create_user,
)

Hedron should infer:

text inputs

email inputs

select controls

checkboxes

labels

required state

help text

server validation

field errors

accessible IDs

HTMX submission

This could be Hedron’s biggest adoption feature for FastAPI users.

10. Automatic validation-error fragments

When a typed action fails validation, Hedron should not return FastAPI’s normal JSON error response to a Hedron form.

It should rerender the form with:

entered values preserved

invalid fields marked

accessible error messages

first invalid field focused

an error summary when appropriate

The developer should not write manual error plumbing for standard forms.

11. Automatic loading and failure states

For a lazy component:

Python
Run
UserStats(
    lazy=True,
)

Hedron could render:

HTML
<section
  hx-get="..."
  hx-trigger="load"
  hx-swap="outerHTML">
  <default skeleton>
</section>

Customization remains easy:

Python
Run
UserStats(
    lazy=True,
    fallback=StatsSkeleton(),
)

For actions, Hedron can automatically apply:

disabled buttons

aria-busy

loading text or spinner

centralized error fragments

12. Layout inference
Python
Run
@app.page("/dashboard")
def dashboard() -> Dashboard:
    return Dashboard(...)

Hedron should use the configured default layout:

Python
Run
app = Hedron(
    layout=ApplicationLayout,
)

Per-page overrides:

Python
Run
@app.page("/login", layout=PublicLayout)
def login() -> LoginPage:
    ...

And explicit opt-out:

Python
Run
@app.page("/embed", layout=None)

Normal requests get the layout. HTMX fragment requests do not.

13. Automatic page metadata

Page components could declare:

Python
Run
class UserPage(Page):
    title = "Users"
    description = "Manage organization users"

Or dynamically:

Python
Run
return UserPage(
    title=f"{user.name} – Profile",
    user=user,
)

Hedron automatically populates:

<title>

description metadata

document language

canonical navigation metadata where configured

HTMX title updates

14. Static assets without manual setup

A new application should not require mounting static directories manually.

Python
Run
app = Hedron()

Should automatically serve:

HTMX

Hedron’s small runtime bridge

built-in styles

development assets

Production users can choose:

Python
Run
app = Hedron(
    assets="external",
)

or provide CDN/self-hosted settings.

15. Development component explorer

In development mode:

Python
Run
app = Hedron(dev=True)

Hedron could expose:

/_hedron
/_hedron/components
/_hedron/routes

The component explorer shows:

registered components

props

endpoint URLs

rendered previews

generated HTML

HTMX behavior

accessibility warnings

incoming request parameters

This would significantly improve discoverability.

16. Excellent error pages

Hedron should translate low-level failures into component-specific diagnostics.

Instead of:

KeyError: title

Show:

HEDRON2012: Missing required prop `title`

Component: UserCard
Endpoint: GET /users/{user_id}
Template: components/UserCard.hdn:4

Expected:
    title: str

Received props:
    user
    compact

In development, render this as a useful HTML error page. In production, use a safe generic failure component.

17. Convention-based project discovery

A beginner project could use:

app/
├── main.py
├── pages/
├── components/
├── models/
└── static/

Then:

Python
Run
app = Hedron.discover("app")

Hedron discovers:

pages

addressable components

HDN templates

assets

model-linked forms

This should be optional. Explicit configuration remains available.

18. Dependency injection into components

FastAPI dependencies should work in addressable component factories.

Python
Run
@addressable
def UserTable(
    team_id: int,
    service: UserService = Depends(get_user_service),
) -> Component:
    return Table(rows=service.for_team(team_id))

That makes addressable components feel like genuine FastAPI endpoints while preserving component composition.

Pure renderable components should remain ordinary objects without dependency injection.

19. Component-local organization

Support both simple files and component folders.

Simple:

components/
└── UserCard.py

Advanced:

components/
└── UserCard/
    ├── component.py
    ├── template.hdn
    ├── styles.css
    ├── browser.js
    └── tests.py

Hedron should discover either structure automatically.

20. Automatic test helpers
Python
Run
response = client.get("/users/42")

response.assert_component(UserCard)
response.assert_text("Ada")
response.assert_htmx_target("#users")

And direct component testing:

Python
Run
html = render(UserCard(user=user))

assert_component(html, UserCard)

Addressable components should also get generated test URLs or fixtures.

What Hedron should not infer

Automatic behavior becomes dangerous when it is ambiguous. Hedron should not guess:

database queries

authorization policy

whether a mutation requires confirmation

whether browser state belongs on the server

arbitrary component endpoint exposure

destructive HTTP methods from button labels

how custom JavaScript should behave

A useful rule is:

Hedron may infer mechanics from declared intent, but it should never infer business intent.

The strongest beginner API

A polished Hedron-first application could eventually look like:

Python
Run
from hedron import Hedron, Page, Card, AutoTable, Button
from app.models import User

app = Hedron(
    components="app.components",
    layout="app.components.AppLayout",
)


@app.page("/users")
def users() -> Page:
    return Page(
        title="Users",
        children=[
            Card(
                title="Team",
                children=[
                    AutoTable(
                        User,
                        rows=get_users(),
                        refreshable=True,
                    ),
                ],
            ),
        ],
    )

The developer gets:

FastAPI routing

HTML responses

full page rendering

HTMX fragment rendering

component identity

refresh endpoints

accessible markup

loading behavior

validation

OpenAPI/component metadata

without learning HDN or writing HTMX URLs.

The product principle I would add to the plan is:

Hedron should infer framework mechanics aggressively where intent is explicit, while keeping business behavior explicit and all inferred behavior inspectable and overridable.

## 73. You

Add all of these to the plan document

## 74. ChatGPT

I've consolidated everything we've discussed into a new version of the plan.

New additions in v8

FastAPI-first architecture with hedron as the flagship distribution

hedron-core, hedron-flask, and hedron-django packaging strategy

Hedron-owned Props, Model, FormModel, and Field API (Pydantic hidden internally)

Progressive disclosure learning model

HDN positioned as an advanced customization layer

Addressable Components as first-class HTTP resources

Dual FastAPI integration:

Hedron() → automatic component rendering

FastAPI() → explicit HTML(...) wrapper

Automatic behaviors section including:

Full page vs HTMX fragment detection

HTML contracts from return annotations

Automatic component endpoint registration

Component references instead of HTMX URLs

Self-refreshing components

Stable component identities

Sensible HTMX defaults

Typed actions

Automatic forms

Automatic validation rendering

Skeleton/loading states

Layout inference

Automatic page metadata

Static asset serving

Development component explorer

Component-aware error pages

Convention-based discovery

FastAPI dependency injection

Component folder conventions

Component-aware testing helpers

Updated roadmap with:

React migration toolkit

Optional Rust acceleration later

Cross-language support after Python matures

Visual component studio

You can download it here:

📄
Hedron_Architecture_Plan_v8.docx

One suggestion for the next step: I think we've reached the point where the architecture document should split into multiple RFCs rather than continue growing as one file. I'd organize it like this:

RFC-0001 — Hedron Vision & Philosophy

RFC-0002 — Component Model

RFC-0003 — FastAPI Integration

RFC-0004 — HDN Language Specification

RFC-0005 — Addressable Components

RFC-0006 — Automatic Behaviors & Conventions

RFC-0007 — Adapter Architecture (Flask/Django)

RFC-0008 — CLI & Developer Experience

RFC-0009 — Component Discovery & Routing

RFC-0010 — Testing & Tooling

That structure will make the project much easier to evolve as Hedron grows.

Hedron_Architecture_Plan_v8.docx
Open file

## 75. You

Let’s consider how hedron will handle fastapi’s OpenApi auto docs

## 76. ChatGPT

Hedron should preserve FastAPI’s OpenAPI documentation rather than replace it, while adding component-aware metadata on top.

The central challenge is that OpenAPI understands HTTP inputs, status codes, media types, and JSON Schema—but it does not natively understand “this HTML response is a UserCard component.” Hedron therefore needs two complementary documentation layers:

Standard OpenAPI documentation for HTTP behavior.

Hedron extensions and a component explorer for component semantics.

Desired result

Given:

Python
Run
@app.get("/users/{user_id}")
def user_card(user_id: int) -> UserCard:
    return UserCard(user=get_user(user_id))

FastAPI’s docs should show:

GET /users/{user_id}

Path parameters
  user_id: integer

Responses
  200
  Content-Type: text/html
  Component: UserCard

  404
  Content-Type: application/json

FastAPI uses the declared response class to determine and document the response media type. Returning a Response object directly bypasses automatic response documentation unless the route also declares the response class or explicit OpenAPI response information.
FastAPI
+1

Hedron-aware route registration

When Hedron() encounters a component return annotation, it should internally transform the route configuration.

User code:

Python
Run
@app.get("/users/{user_id}")
def user_card(user_id: int) -> UserCard:
    return UserCard(user=get_user(user_id))

Internal equivalent:

Python
Run
@app.get(
    "/users/{user_id}",
    response_class=HedronHTMLResponse,
    response_model=None,
    responses={
        200: {
            "description": "Rendered UserCard component",
            "content": {
                "text/html": {
                    "schema": {
                        "type": "string",
                    }
                }
            },
        }
    },
)
def user_card(user_id: int):
    ...

The important details are:

response_class=HedronHTMLResponse

response_model=None

text/html as the documented media type

a string schema representing the rendered HTML

component-specific OpenAPI extensions

FastAPI supports combining route response information, status codes, media types, and explicit responses metadata in the generated OpenAPI document.
FastAPI
+1

Add Hedron OpenAPI extensions

OpenAPI permits vendor extensions beginning with x-. Hedron should add metadata such as:

JSON
{
  "responses": {
    "200": {
      "description": "Rendered UserCard component",
      "content": {
        "text/html": {
          "schema": {
            "type": "string"
          }
        }
      },
      "x-hedron-component": {
        "name": "UserCard",
        "kind": "addressable",
        "fragment": true
      }
    }
  }
}

A richer operation could include:

JSON
{
  "x-hedron": {
    "component": "UserCard",
    "componentId": "app.components.users.UserCard",
    "addressable": true,
    "renderMode": "fragment",
    "propsSchema": "#/components/schemas/UserCardProps",
    "template": "UserCard.hdn",
    "htmx": {
      "target": "self",
      "swap": "outerHTML"
    }
  }
}

FastAPI supports extending individual operations with openapi_extra, and its generated OpenAPI schema can also be customized globally and cached.
FastAPI
+1

Component return annotations must not become JSON models

FastAPI normally uses annotated return models to generate JSON Schema, validate the response, filter fields, and serialize the result as JSON.
FastAPI

Hedron needs to intercept component annotations before FastAPI treats them as ordinary response models.

Conceptually:

Python
Run
def register_route(endpoint, **route_options):
    return_type = get_return_type(endpoint)

    if is_hedron_component_type(return_type):
        route_options.setdefault(
            "response_class",
            HedronHTMLResponse,
        )
        route_options.setdefault(
            "response_model",
            None,
        )
        route_options["responses"] = merge_component_docs(
            route_options.get("responses"),
            return_type,
        )

    return fastapi_register_route(
        endpoint,
        **route_options,
    )

This can live in:

a Hedron-aware APIRoute

a custom APIRouter

the Hedron application subclass

Hedron’s route decorators

FastAPI supports custom APIRoute and APIRouter behavior, including preserving custom route classes when routers are included in applications.
FastAPI
+1

Keep all normal request documentation

Only the output changes.

FastAPI should continue documenting:

path parameters

query parameters

request bodies

headers

cookies

dependencies

authentication

validation errors

additional JSON responses

Example:

Python
Run
@app.post("/users")
def create_user(
    form: CreateUser,
    service: UserService = Depends(get_user_service),
) -> UserTable:
    service.create(form)
    return UserTable(users=service.list())

The docs should show:

Request
  application/x-www-form-urlencoded
  or application/json

  CreateUser
    name: string
    email: string
    role: admin | member

Response 200
  text/html
  UserTable component

Hedron should enhance FastAPI’s output documentation without replacing its input-model machinery.

Document component props separately from endpoint inputs

This distinction matters.

Python
Run
def user_card(user_id: int) -> UserCard:
    return UserCard(
        user=get_user(user_id),
        compact=True,
    )

Here:

user_id is an HTTP endpoint input.

UserCard.user and UserCard.compact are component props.

Not every component prop is directly supplied by the HTTP client.

Therefore, the OpenAPI operation should not falsely claim that all component props are request parameters.

Instead:

JSON
{
  "x-hedron": {
    "component": "UserCard",
    "propsSchema": {
      "$ref": "#/components/schemas/UserCardProps"
    }
  }
}

The component schema is documentation metadata, not necessarily the endpoint request schema.

Addressable component endpoints

For automatically registered component resources:

Python
Run
@addressable
def UserTable(
    team_id: int,
    page: int = 1,
    service: UserService = Depends(get_user_service),
) -> UserTableComponent:
    ...

Hedron can document the endpoint normally:

GET /_hedron/components/user-table

Query parameters
  team_id: integer, required
  page: integer, default 1

Response
  text/html
  UserTableComponent

This is where FastAPI’s OpenAPI generation becomes especially valuable: addressable component functions are genuine typed endpoints, so their inputs can be documented exactly like ordinary API operations.

Separate public pages from internal component resources

Not every addressable component route should clutter the primary Swagger interface.

Hedron should support three visibility levels:

Python
Run
@addressable(docs="public")

Appears in the normal FastAPI docs.

Python
Run
@addressable(docs="component")

Appears in Hedron’s component explorer but not the normal Swagger list.

Python
Run
@addressable(docs="hidden")

Excluded from both public documentation views.

Defaults could be:

Route type	Swagger/OpenAPI	Component explorer
Public page	Yes	Yes
Explicit public component endpoint	Yes	Yes
Auto-generated component resource	No	Yes
Internal helper component	No	Optional
Static/internal runtime route	No	No

FastAPI routes already support being excluded from the generated schema, so Hedron can use that mechanism for internal component resources while maintaining its own registry.

Tagging

Hedron should automatically organize routes using tags:

Pages
Components
Actions
API
Hedron Internal

Example:

Python
Run
@app.page("/users")
def users() -> UsersPage:
    ...

Automatically:

Python
Run
tags=["Pages"]
Python
Run
@addressable
def UserTable(...) -> UserTableComponent:
    ...

Automatically:

Python
Run
tags=["Components"]
Python
Run
@app.action("/users/{id}", method="delete")
def delete_user(...) -> UserTable:
    ...

Automatically:

Python
Run
tags=["Actions"]

Users must be able to override these.

Swagger’s “Try it out”

Swagger UI will send the request and display the HTML response, but it will generally present that response as text rather than render it as an interactive component.

That is acceptable for API-level testing, but not enough for component development.

Hedron should add a link through an OpenAPI extension:

JSON
{
  "x-hedron-preview-url": "/_hedron/preview/UserCard"
}

Then Hedron’s docs customization or component explorer can offer:

Preview component

Open endpoint

View HTML

View props

Test HTMX interaction

A dedicated Hedron component explorer

FastAPI docs answer:

What HTTP request does this route accept?

Hedron’s explorer should answer:

What component does this route render, and how does it behave?

Development URL:

/_hedron/components

Example entry:

UserTable

Kind
  Addressable component

Endpoint
  GET /_hedron/components/user-table

Props
  team_id: int
  page: int = 1
  search: str | None = None

Response
  text/html

HTMX
  Default target: self
  Default swap: outerHTML

Used by
  UsersPage
  AdminDashboard

Actions
  Preview
  Test request
  View rendered HTML
  View source
  Copy component call

This should use the same route and component metadata that generate OpenAPI, avoiding two independent documentation systems.

Full pages versus fragments

An endpoint may return different HTML shapes depending on the request:

Python
Run
@app.page("/users")
def users() -> UsersPage:
    return UsersPage(...)

Normal request:

text/html — complete HTML document

HTMX request:

text/html — UsersPage fragment

OpenAPI cannot naturally express “the representation depends on HX-Request” as strongly as Hedron’s own metadata can.

Document the shared media type normally, then add:

JSON
{
  "x-hedron-render-modes": {
    "default": "document",
    "htmx": "fragment",
    "requestHeader": "HX-Request"
  }
}

The endpoint description can say:

Returns a complete HTML document for ordinary requests and the page component fragment for HTMX requests.

Hedron should also ensure responses vary correctly based on the HTMX request header where caching is involved.

Multiple possible component responses

This should work:

Python
Run
@app.get("/users/{user_id}")
def user(
    user_id: int,
) -> UserCard | NotFoundPanel:
    user = find_user(user_id)

    if user is None:
        return NotFoundPanel(user_id=user_id)

    return UserCard(user=user)

OpenAPI still sees one HTML media type, while Hedron metadata lists possible components:

JSON
{
  "x-hedron-components": [
    "UserCard",
    "NotFoundPanel"
  ]
}

However, normal HTTP semantics would often be clearer:

Python
Run
@app.get(
    "/users/{user_id}",
    responses={
        404: component_response(NotFoundPanel),
    },
)
def user(user_id: int) -> UserCard:
    ...

Then the documentation shows:

200 text/html → UserCard
404 text/html → NotFoundPanel

Hedron should provide a helper:

Python
Run
@app.get(
    "/users/{user_id}",
    responses={
        404: HTMLResponseOf(NotFoundPanel),
    },
)
JSON and HTML from one endpoint

Hedron should discourage ambiguous content negotiation by default, but support it explicitly.

Python
Run
@app.get(
    "/users/{user_id}",
    responses={
        200: {
            "content": {
                "text/html": component_content(UserCard),
                "application/json": model_content(UserResponse),
            }
        }
    },
)
def user(...) -> UserCard | UserResponse:
    ...

This is valid but adds complexity for clients and docs.

The simpler convention should be:

/users/{id}      → HTML component
/api/users/{id}  → JSON model
Plain FastAPI integration

For:

Python
Run
app = FastAPI()

@app.get(
    "/users/{id}",
    response_class=HTMLResponse,
)
def user(id: int):
    return HTML(UserCard(...))

Hedron cannot infer everything from the application subclass because there is no Hedron() wrapper.

We should provide a route helper:

Python
Run
from hedron.fastapi import component_response

@app.get(
    "/users/{id}",
    **component_response(UserCard),
)
def user(id: int):
    return HTML(UserCard(...))

Or a concise decorator:

Python
Run
from hedron.fastapi import documents_component

@app.get("/users/{id}")
@documents_component(UserCard)
def user(id: int):
    return HTML(UserCard(...))

My preference:

Python
Run
@app.get(
    "/users/{id}",
    response_class=HTML,
    responses=HTML.documents(UserCard),
)

But that may be too magical. A clear helper is better:

Python
Run
@app.get(
    "/users/{id}",
    **hedron_response(UserCard),
)

This keeps plain FastAPI integration explicit.

OpenAPI operation IDs

Hedron should generate stable, readable operation IDs:

page_users
component_user_table
action_delete_user
api_get_user

FastAPI supports customizing operation-ID generation, and those IDs are important to generated clients and tooling.
FastAPI

Do not derive them solely from generated component URLs, because internal routing paths may change.

Proposed implementation structure
hedron/
└── openapi/
    ├── route_metadata.py
    ├── component_schema.py
    ├── responses.py
    ├── extensions.py
    ├── operation_ids.py
    └── explorer.py

Core metadata:

Python
Run
@dataclass(frozen=True)
class HedronOperation:
    component_type: type[Component]
    addressable: bool
    render_mode: RenderMode
    props_type: type[Props] | None
    default_target: str | None
    default_swap: str | None
    docs_visibility: DocsVisibility

The route stores this metadata, and both OpenAPI generation and the component explorer consume it.

Recommended design rules

Never document a component response as JSON.

Always document Hedron-rendered output as text/html.

Use standard OpenAPI fields for HTTP semantics.

Use x-hedron-* extensions for component semantics.

Do not expose every generated component route in Swagger by default.

Keep FastAPI’s input and dependency documentation intact.

Generate one internal metadata model used by OpenAPI and the component explorer.

Allow all inferred documentation to be overridden.

Cache the generated OpenAPI document using FastAPI’s normal schema-cache approach.
FastAPI

Treat Swagger as the HTTP explorer and Hedron Explorer as the component explorer.

The result should feel seamless:

Python
Run
@app.get("/users/{id}")
def user(id: int) -> UserCard:
    return UserCard(user=get_user(id))

From that declaration, Hedron can derive:

the FastAPI route inputs,

text/html output,

the expected root component,

OpenAPI response metadata,

component explorer registration,

preview support,

return-type validation,

and HTMX behavior.

That preserves FastAPI’s strongest documentation feature while extending it to understand Hedron’s component-oriented HTML layer.

Sources

## 77. You

Okay, add your recommendation to the hedron plan document

## 78. ChatGPT

I updated the plan with the OpenAPI strategy that I think gives Hedron the best long-term developer experience.

The major additions are:

OpenAPI & Documentation Strategy

Hedron extends FastAPI's OpenAPI instead of replacing it.

Component responses are documented as text/html.

Component return annotations become HTML response contracts.

Hedron adds x-hedron-* metadata for component-specific information.

Auto-generated component resource endpoints stay out of Swagger by default.

Hedron Component Explorer

Separate from Swagger/ReDoc.

Shows:

Registered components

Props

Component endpoints

Live previews

Generated HTML

HTMX behavior

Component relationships

Uses the same metadata that powers the OpenAPI extensions, so there is a single source of truth.

Guiding philosophy

JSON endpoints return models. HTML endpoints return components.

Swagger documents HTTP. Hedron Explorer documents components.

I think this separation is an important architectural decision. It keeps FastAPI's excellent API documentation intact while giving Hedron a richer UI-focused explorer that OpenAPI was never designed to provide.

You can download it here:

📄
Hedron_Architecture_Plan_v9.docx

One thing I would seriously consider for the next revision is making the Hedron Component Explorer one of the flagship features. Imagine opening /_hedron during development and seeing:

📄 Pages

🧩 Components

⚡ Actions

🔄 Addressable Components

🎨 Live Preview

🏷 Props

🌐 Generated Routes

📋 Generated HTML

♿ Accessibility Report

📈 Render Timing

That would give Hedron something that neither React nor FastAPI currently offers: a development environment centered around components as first-class server resources rather than just routes or client-side trees.

Hedron_Architecture_Plan_v9.docx
Document

## 79. You

Okay, let’s explore a  Hedron Component Explorer more

## 80. ChatGPT

The Hedron Component Explorer could become one of the framework’s strongest adoption features. It should combine the best parts of Storybook, FastAPI’s /docs, React DevTools, and an HTMX request inspector—but remain entirely server-first and automatically generated.

Core idea

FastAPI’s Swagger UI answers:

What HTTP routes exist, and what data do they accept?

The Hedron Explorer answers:

What UI resources exist, how do they render, and how do they interact?

FastAPI /docs
    Routes
    Parameters
    Request bodies
    JSON schemas
    Status codes

Hedron /_hedron
    Pages
    Components
    Actions
    Props
    Live previews
    HTMX interactions
    Rendered HTML
    Dependencies
    Diagnostics
Main navigation

I would organize the Explorer around six primary areas:

Components

All registered renderable and addressable components.

Components
├── Layout
│   ├── AppShell
│   ├── Navbar
│   └── Sidebar
├── Users
│   ├── UserCard
│   ├── UserTable
│   └── UserForm
└── Shared
    ├── Button
    ├── Alert
    └── Modal

Each component should indicate:

renderable or addressable

built-in, application, or dependency-provided

Python-rendered or HDN-rendered

endpoint status

usage count

warnings or errors

Pages

Page-level components and their public routes:

/                   HomePage
/users              UsersPage
/users/{user_id}    UserDetailPage
/settings           SettingsPage

This view should show layouts, authentication dependencies, title metadata, and the components used by each page.

Actions

Typed mutations and server interactions:

create_user
delete_user
update_profile
refresh_dashboard

For each action:

HTTP method

URL

accepted model

return component

HTMX target

swap behavior

CSRF behavior

usages

Routes

A Hedron-focused version of FastAPI’s route list:

GET     /users                  UsersPage
GET     /_hedron/c/user-table   UserTable
POST    /users                  create_user → UserTable
DELETE  /users/{id}             delete_user → UserTable
Diagnostics

Framework-wide issues:

missing props

duplicate component keys

invalid HTMX targets

inaccessible form labels

unused addressable components

route conflicts

template compilation failures

slow component rendering

Settings

Development-only configuration:

default preview viewport

active theme

component discovery paths

HDN reload behavior

HTML formatting

debug marker visibility

Component detail page

Selecting UserTable could open a detail workspace with several tabs.

Preview

A live, isolated render of the component.

Controls should include:

viewport width

theme

ordinary request versus HTMX request

loading, empty, error, and populated states

configurable props

refresh button

open endpoint directly

Example:

UserTable

[Desktop] [Tablet] [Mobile]    [Light] [Dark]
[Normal request] [HTMX request]

┌──────────────────────────────────────────┐
│ Users                            Refresh │
├──────────────────────────────────────────┤
│ Ada Lovelace     ada@example.com         │
│ Grace Hopper     grace@example.com       │
└──────────────────────────────────────────┘
Props

Automatically generated from Hedron’s Props model:

rows       list[User]       required
compact    bool             false
page       int              1
search     str | None       null

The Explorer should generate editable controls:

text box for strings

checkbox for booleans

numeric input for numbers

select for Literal and enum values

structured editor for nested models

repeatable inputs for lists

Changing props rerenders the preview.

This makes the Explorer function like Storybook controls without requiring stories for every basic component.

Component states and examples

Automatic prop controls are useful, but realistic scenarios need named examples.

Python
Run
from hedron import example


@example(UserTable, name="Populated")
def populated_table() -> UserTable:
    return UserTable(rows=sample_users)


@example(UserTable, name="Empty")
def empty_table() -> UserTable:
    return UserTable(rows=[])


@example(UserTable, name="Large dataset")
def large_table() -> UserTable:
    return UserTable(rows=sample_users * 50)

The Explorer displays:

Examples
├── Default
├── Populated
├── Empty
└── Large dataset

Examples could also provide dependencies or mock services:

Python
Run
@example(UserDashboard)
def dashboard_example() -> UserDashboard:
    with mock_dependency(UserService, DemoUserService()):
        return UserDashboard(team_id=1)
Request simulator

Addressable components are HTTP resources, so the Explorer should allow developers to exercise the actual endpoint.

Request

Method: GET
Path: /_hedron/components/user-table

Query
team_id: 12
page:    1
search:  Ada

Headers
HX-Request: true
HX-Target: user-table-team

[Send request]

Results:

Status       200
Content-Type text/html
Render time  3.8 ms
Size         4.2 KB

Tabs:

Preview

Response HTML

Headers

Component trace

Server logs

This is where Hedron surpasses a conventional component catalog: it tests both the visual component and the real HTTP interaction.

HTMX inspector

The Explorer should understand HTMX as a first-class system.

For an addressable component, show:

HTMX configuration

Resource URL      /_hedron/components/user-table
Default target    self
Default swap      outerHTML
Trigger           refresh-users
Polling           none
Lazy load         disabled
History           disabled

For an action button, show the compiled result:

Python
Run
Button(
    "Delete",
    action=delete_user(user_id=42),
)
HTML
<button
    hx-delete="/users/42"
    hx-target="#hedron-user-table-team"
    hx-swap="outerHTML"
    hx-disabled-elt="this">
    Delete
</button>

The inspector should explain where each inferred attribute came from:

hx-delete       Inferred from action method
hx-target       Inferred from owning addressable component
hx-swap         Default for component replacement
hx-disabled-elt Hedron action-button default

That makes automatic behavior transparent rather than magical.

Component graph

Hedron knows which components contain or reference other components. The Explorer should visualize this.

UsersPage
├── AppLayout
│   ├── Navbar
│   └── Sidebar
└── UserTable
    ├── SearchField
    ├── Table
    ├── Pagination
    └── RefreshButton

The inverse view is equally useful:

UserTable is used by:
├── UsersPage
├── AdminDashboard
└── TeamDetailPage

For addressable components, show action and endpoint relationships:

UserTable
├── rendered by GET /users
├── resource GET /_hedron/components/user-table
├── refreshed by refresh_users
└── returned by delete_user

This becomes a server-component dependency graph.

Render trace

A component render should be inspectable like a miniature execution trace:

UsersPage                         5.4 ms
├── AppLayout                     1.3 ms
├── UserToolbar                   0.4 ms
└── UserTable                     3.1 ms
    ├── SearchField               0.2 ms
    ├── Table                     2.5 ms
    └── Pagination                0.3 ms

For each node:

render duration

output bytes

child count

template used

props model

cache hit or miss

source file

This should be development-only and sampled to avoid adding production overhead.

Source inspection

A Source tab could show:

component Python source

HDN template

generated component specification

generated HTML

endpoint definition

registered examples

The Explorer should link diagnostics to exact locations:

components/users/UserTable.hdn:24

Unknown prop `stripedRows` on component Table.

Did you mean `striped`?
Accessibility tooling

Hedron controls the generated markup, so the Explorer should include static checks before requiring browser automation.

Potential checks:

inputs without labels

duplicate IDs

images without alternative text

buttons without accessible names

invalid ARIA attributes

heading-level jumps

dialogs without labels

error messages not associated with fields

invalid table structure

Example result:

Accessibility

✓ All form controls have labels
✓ No duplicate element IDs
⚠ Heading jumps from h1 to h3
✕ Icon-only button has no accessible name

Later, browser-based axe integration could provide deeper checks, but static server-side validation is a strong MVP.

Automatic states

Hedron can derive some standard states from component contracts.

For a table-like component:

Default
Empty
Loading
Error

For forms:

Blank
Valid values
Validation errors
Submitting
Success

These should be generated only when the component declares applicable capabilities. Hedron should not fabricate arbitrary business data.

Named examples remain the source of truth for realistic scenarios.

Built-in versus application components

The Explorer should distinguish ownership:

Origin

Application
  app.components.UserTable

Hedron built-in
  hedron.components.Button

Package
  hedron_admin.components.AdminSidebar

Application components should appear first. Built-ins can be hidden or filtered by default so the Explorer does not become noisy.

Discovery and registration

The Explorer should consume the same central registry as rendering and OpenAPI.

Python
Run
@dataclass
class ComponentDefinition:
    component_type: type[Component]
    props_type: type[Props] | None
    kind: ComponentKind
    source: SourceLocation
    endpoint: ComponentEndpoint | None
    template: TemplateDefinition | None
    examples: list[ComponentExample]
    dependencies: list[ComponentReference]
    metadata: ComponentMetadata

This registry should be the single source of truth for:

rendering

endpoint registration

OpenAPI extensions

component previews

route inspection

diagnostics

CLI tools

Development-only by default

The Explorer should default to enabled only in development:

Python
Run
app = Hedron(
    dev=True,
)

Available at:

/_hedron

Production behavior:

Python
Run
app = Hedron(
    explorer=False,
)

Or authenticated production access:

Python
Run
app = Hedron(
    explorer=ExplorerConfig(
        enabled=True,
        dependency=require_admin,
    )
)

It should never expose source paths, props, diagnostics, or internal routes publicly by accident.

Explorer extensibility

Plugins should eventually be able to contribute panels.

Examples:

SQLAlchemy
  Queries triggered during render

Redis
  Component cache activity

Authentication
  Required permissions

Datadog/OpenTelemetry
  Trace links

Design system
  Tokens and variants

Accessibility
  Additional organization-specific rules

A small protocol could look like:

Python
Run
class ExplorerPanel:
    name: str

    def supports(self, component: ComponentDefinition) -> bool:
        ...

    def render(self, context: ExplorerContext) -> Component:
        ...

Importantly, the Explorer itself should be built using Hedron components. It becomes the framework’s best real-world reference application.

CLI integration

The browser Explorer and CLI should share functionality.

Bash
hedron components
hedron inspect UserTable
hedron preview UserTable
hedron routes
hedron graph UsersPage
hedron check

Example:

$ hedron inspect UserTable

Kind:       Addressable
Props:      UserTableProps
Template:   components/users/UserTable.hdn
Endpoint:   GET /_hedron/components/user-table
Used by:    UsersPage, AdminDashboard
Examples:   Default, Empty, Populated
Warnings:   0
Recommended MVP

The first Explorer release should remain focused:

Component and page registry

Search and filtering

Component details

Prop schemas

Named examples

Isolated preview

Addressable endpoint request simulator

Rendered HTML viewer

HTMX metadata

Source locations and diagnostics

Defer initially:

interactive graph visualization

performance flame graphs

browser accessibility automation

plugin marketplace

visual component editing

production monitoring

Suggested internal routes
/_hedron
/_hedron/components
/_hedron/components/{component_id}
/_hedron/components/{component_id}/preview
/_hedron/components/{component_id}/request
/_hedron/pages
/_hedron/actions
/_hedron/routes
/_hedron/diagnostics
/_hedron/openapi

Internal API routes should be hidden from the application’s normal OpenAPI schema.

Product positioning

The Explorer could support a very compelling onboarding loop:

Write a component.

Start the application.

Open /_hedron.

See the component automatically.

Change props interactively.

inspect the generated HTML and HTMX behavior.

Copy the usage example into the application.

That significantly reduces the amount of documentation a new user must read before becoming productive.

The product principle should be:

Every automatic behavior Hedron introduces should be visible and explainable in the Component Explorer.

That addresses the risk of excessive framework magic. Hedron can remain highly automatic while giving developers a precise window into what it inferred, why it inferred it, and how to override it.

## 81. You

Add this to the plan document

## 82. ChatGPT

Worked for 1m 11s

I added the full Hedron Component Explorer design to the architecture plan, including:

Explorer goals and navigation

Component, page, action, route, diagnostics, and settings views

Live previews and generated prop controls

Named examples and component states

Addressable endpoint request simulation

HTMX inspection and inference explanations

Component graphs and render traces

Accessibility and framework diagnostics

Shared registry architecture

Development-only safeguards

Plugin extensibility

CLI integration

MVP scope and deferred capabilities

Suggested internal /_hedron routes

The updated plan is available here:

Hedron_Architecture_Plan_v10.docx

Hedron_Architecture_Plan_v10.docx
Document

## 83. You

Do we have the react feature of styled components?

## 84. ChatGPT

Not yet—but I think we can do something better suited to a server-first framework.

The question isn't "How do we copy styled-components?"

It's "What problem was styled-components solving?"

It solved:

Component-scoped styling

Dynamic styling based on props

Colocation of styles and components

Dead CSS elimination

Avoiding global CSS collisions

Hedron can solve those problems differently because it owns the rendering pipeline.

Option 1: Traditional CSS (default)

For beginners:

UserCard/
    component.py
    styles.css

Hedron automatically loads:

CSS
.user-card {
    padding: 1rem;
}

No magic.

Option 2: Component-local CSS

I actually like this better.

UserCard/

    component.py

    template.hdn

    styles.css

Only components using UserCard include that CSS.

The Explorer could even show:

UserCard

HTML
CSS
Props
HTMX
Preview
Option 3: Python styles

This is where it gets interesting.

Python
Run
class UserCard(Component):

    styles = css(
        """
        .root {
            padding: 1rem;
            border-radius: 12px;
        }

        .title {
            font-weight: bold;
        }
        """
    )

Very similar to styled-components, but server-side.

Option 4: CSS objects

React has:

JavaScript
<div style={{
    padding: 16
}}

Hedron could do

Python
Run
Card(
    style={
        "padding": "1rem",
        "border-radius": "12px",
    }
)

Simple.

No compiler needed.

Option 5: Component-scoped classes

I think this is where Hedron could differentiate.

Suppose:

UserCard/
    styles.css

contains

CSS
.root {
    padding: 1rem;
}

.title {
    font-weight: bold;
}

During startup Hedron rewrites it.

.hdn-UserCard-root-84af2

.hdn-UserCard-title-84af2

Then the HDN compiler rewrites

JavaScript
<section class="root">

<h2 class="title">

into

HTML
<section class="hdn-UserCard-root-84af2">

<h2 class="hdn-UserCard-title-84af2">

Now:

no CSS collisions

no runtime

no Shadow DOM

no CSS modules build step

That's really compelling.

Option 6: CSS Modules

Honestly...

This is basically CSS Modules.

Except:

implemented in Python

server-side

integrated into HDN

I think that's a better story than copying styled-components.

Dynamic styles

Styled Components shine here.

JavaScript
const Button = styled.button`
    color: ${props => props.primary ? "red" : "blue"};
`

I wouldn't copy that.

Instead:

Python
Run
Button(
    variant="danger"
)

Template

JavaScript
<button class={variant}>

Theme

Python
Run
Theme(
    Button={
        "danger": "btn btn-danger",
        "primary": "btn btn-primary",
    }
)

The framework should encourage:

semantic variants

instead of

arbitrary CSS generation.

Tokens

I think Hedron should have first-class design tokens.

Python
Run
Theme(

    colors={

        "primary": "#3B82F6",

        "danger": "#EF4444",

    },

    radius={

        "small": "4px",

        "large": "12px",

    }

)

Components consume tokens.

Not raw colors.

Automatic CSS tree shaking

Because Hedron knows:

UsersPage

↓

UserTable

↓

Button

it knows exactly which CSS files are needed.

Unlike React.

It can generate

UsersPage.css

containing

UserTable.css

Button.css

Nothing else.

Theme switching

Since Hedron owns rendering:

Python
Run
return Dashboard(
    theme="dark"
)

becomes

HTML
<html data-theme="dark">

Everything else just works.

Component assets

I actually think every component should become a folder.

UserCard/

    component.py

    template.hdn

    styles.css

    browser.js

    tests.py

    examples.py

Everything lives together.

Exactly like React.

Except Python.

The Explorer

This is where it becomes awesome.

Imagine

UserCard

-------------------------

Preview

HTML

HDN

CSS

Props

Accessibility

HTMX

Dependencies

Click CSS

Shows

CSS
.root {

...
}

Click HTML

Shows generated HTML.

Click HDN

Shows template.

Click Preview

Live updates.

That's an incredible development experience.

My recommendation

I would not implement a runtime equivalent of styled-components.

Instead I'd build what is effectively server-side CSS Modules with component-scoped styles.

Advantages:

no runtime cost

no generated <style> tags on every render

cacheable CSS

deterministic output

component isolation

excellent integration with HDN

perfect fit for the Component Explorer

I actually think this is stronger than styled-components for Hedron because it aligns with the framework's core philosophy: do as much work as possible ahead of time on the server, and send simple, standards-based HTML and CSS to the browser.

## 85. You

Explore server-side CSS Modules with component-scoped styles more

## 86. ChatGPT

This could be a major Hedron subsystem, but I would describe it publicly as Hedron Scoped Styles rather than claiming literal compatibility with JavaScript CSS Modules.

Traditional CSS Modules locally scope class names and animation names, then expose a mapping for application code to reference. Hedron can adopt the same core idea while integrating it directly with Python components, HDN templates, addressable endpoints, and server-side asset discovery.
GitHub
+1

The core model

Each component may own a stylesheet:

components/
└── UserCard/
    ├── component.py
    ├── template.hdn
    ├── styles.css
    └── examples.py

styles.css:

CSS
.root {
    display: grid;
    gap: 1rem;
    padding: 1rem;
    border: 1px solid var(--hedron-color-border);
    border-radius: var(--hedron-radius-medium);
}

.header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.name {
    font-weight: 600;
}

.compact {
    padding: 0.5rem;
}

template.hdn:

JavaScript
<article class={styles.root}>
    <header class={styles.header}>
        <Avatar user={props.user} />
        <h2 class={styles.name}>{props.user.name}</h2>
    </header>

    <p>{props.user.email}</p>
</article>

Hedron compiles this into something like:

HTML
<article class="h_UserCard_root_d7k3p">
    <header class="h_UserCard_header_j2m8c">
        ...
        <h2 class="h_UserCard_name_r4s1q">Ada Lovelace</h2>
    </header>

    <p>ada@example.com</p>
</article>

And rewrites the CSS accordingly:

CSS
.h_UserCard_root_d7k3p {
    display: grid;
    gap: 1rem;
    padding: 1rem;
    border: 1px solid var(--hedron-color-border);
    border-radius: var(--hedron-radius-medium);
}

.h_UserCard_header_j2m8c {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.h_UserCard_name_r4s1q {
    font-weight: 600;
}

There is no browser-side style runtime and no generated <style> element on each render.

Beginner experience

New users should not have to understand style compilation.

They can begin with component props:

Python
Run
Card(
    title="Users",
    variant="outlined",
    padding="medium",
)

Or ordinary global classes:

Python
Run
Card(
    title="Users",
    class_="dashboard-card",
)

Scoped styles appear only when they create a component folder or attach a stylesheet:

Python
Run
from hedron import Component, scoped_styles

styles = scoped_styles("styles.css")


class UserCard(Component):
    ...

HDN automatically receives the styles binding:

JavaScript
<article class={styles.root}>

That feels close to CSS Modules without requiring imports inside HDN.

Python-only components

Scoped styles must also work without HDN.

Python
Run
from hedron import Component, Div, H2, scoped_styles

styles = scoped_styles("styles.css")


class UserCard(Component):
    def render(self):
        return Div(
            H2(self.props.user.name, class_=styles.name),
            class_=styles.root,
        )

The object represented by styles should be typed enough that editors can autocomplete known class names:

Python
Run
styles.root
styles.header
styles.name

Unknown names should fail early:

Python
Run
styles.heder
HEDRON3402: Unknown scoped class `heder`.

styles.css defines:
    root
    header
    name
    compact

Did you mean `header`?
Class composition

The everyday pattern should be concise:

JavaScript
<article
    class={[
        styles.root,
        props.compact && styles.compact,
        props.selected && styles.selected
    ]}
>

Hedron normalizes this to a space-separated class string, omitting false and null values.

Python:

Python
Run
Div(
    class_=[
        styles.root,
        styles.compact if props.compact else None,
    ]
)

A helper can also exist:

JavaScript
class={cx(
    styles.root,
    props.compact && styles.compact
)}

But accepting class lists directly is simpler and more framework-native.

CSS-level composition

Traditional CSS Modules support composing one local class from another.
GitHub

Hedron could support:

CSS
.button {
    display: inline-flex;
    align-items: center;
}

.danger {
    composes: button;
    color: var(--hedron-color-danger-text);
    background: var(--hedron-color-danger);
}

Then:

JavaScript
<button class={styles.danger}>Delete</button>

renders both generated class names:

HTML
<button class="h_Button_button_m2a9 h_Button_danger_p7c1">

However, this syntax should be optional. Plain CSS remains the default.

Local and global selectors

Classes should be local by default:

CSS
.root {}
.title {}

Sometimes a component must target a global class from HTMX, a third-party widget, or application markup.

Use an explicit escape:

CSS
:global(.htmx-request) .spinner {
    display: inline-block;
}

.root :global(.third-party-widget) {
    margin-block: 1rem;
}

Hedron should never silently decide that a selector is global.

Global styles belong in an application stylesheet:

styles/
├── reset.css
├── tokens.css
├── typography.css
└── application.css

A strong boundary would be:

Component stylesheet: local classes by default.

Application stylesheet: global by default.

Explicit :global(...) and :local(...) escapes available when needed.

Scoping the root

It may be useful to give every component instance a stable component marker:

HTML
<article
    class="h_UserCard_root_d7k3p"
    data-hedron-component="UserCard"
>

But CSS scoping should primarily rely on transformed classes, not deeply prefixing every selector with the component marker.

Avoid output such as:

CSS
[data-hedron-component="UserCard"] .root .header .name

That increases selector specificity and makes overrides harder.

Generated class names provide isolation with low specificity.

Stable naming strategy

Development class names should be readable:

h_UserCard_root_d7k3p
h_UserCard_title_y4v8a

Production may optionally shorten them:

h_a81
h_b03

I would keep readable names by default, even in production. The gzip savings from extremely short classes are usually less valuable than inspectability.

The hash should derive from stable inputs:

package identity
component identity
stylesheet-relative path
local symbol name
scoping algorithm version

It should not depend on:

absolute developer-machine paths

file modification time

import order

process ID

random values

That ensures reproducible builds and prevents class names from changing unnecessarily.

Animation names must be scoped too

CSS Modules traditionally scope animation names as well as classes.
GitHub

Input:

CSS
@keyframes fade-in {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

.root {
    animation: fade-in 180ms ease-out;
}

Output:

CSS
@keyframes h_UserCard_fade_in_k2d4 {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

.h_UserCard_root_d7k3p {
    animation: h_UserCard_fade_in_k2d4 180ms ease-out;
}

The compiler must update references in:

animation

animation-name

relevant nested rules

vendor-prefixed forms, if supported

Native CSS nesting

Hedron should accept standards-based CSS nesting directly:

CSS
.root {
    padding: 1rem;

    &:hover {
        border-color: var(--hedron-color-accent);
    }

    .title {
        margin: 0;
    }
}

Native nesting is now part of the CSS platform and is interpreted by browsers rather than requiring Sass-style preprocessing.
MDN Web Docs
+1

Hedron has two possible policies:

Preserve native nesting

Ship it unchanged after transforming local class selectors.

Advantages:

less compiler work

aligns with modern CSS

no custom preprocessor behavior

Flatten nesting

Compile nested rules into ordinary selectors for older browser support.

Advantages:

broader compatibility

predictable output for constrained environments

My recommendation is:

preserve native nesting by default

optionally flatten it when a browser-target configuration requires it

do not invent Sass features such as mixins, variables, or arbitrary functions in the MVP

Themes and design tokens

Dynamic style values should primarily use CSS custom properties, not generate new classes for each prop combination.

CSS custom properties participate in the normal cascade and may be scoped to particular elements, making them a natural fit for theming.
MDN Web Docs
+1

Global token definition:

CSS
:root {
    --hedron-color-surface: #ffffff;
    --hedron-color-text: #1f2937;
    --hedron-color-border: #d1d5db;
    --hedron-color-accent: #2563eb;

    --hedron-space-small: 0.5rem;
    --hedron-space-medium: 1rem;
    --hedron-radius-medium: 0.5rem;
}

[data-theme="dark"] {
    --hedron-color-surface: #111827;
    --hedron-color-text: #f9fafb;
    --hedron-color-border: #374151;
}

Component CSS:

CSS
.root {
    color: var(--hedron-color-text);
    background: var(--hedron-color-surface);
    border-color: var(--hedron-color-border);
}

This separates three concepts:

Scoped classes provide structural isolation.

Variants select semantic component states.

Tokens provide shared visual values and themes.

Component-level token overrides
Python
Run
UserCard(
    user=user,
    tokens={
        "accent": "#7c3aed",
    },
)

Could render:

HTML
<article
    class="h_UserCard_root_d7k3p"
    style="--hedron-component-accent: #7c3aed"
>

But this should be an escape hatch. Most visual choices should use variants or themes.

Variants

Styled-components often derive arbitrary CSS from props. Hedron should prefer finite semantic variants.

Python
Run
Button(
    "Delete",
    variant="danger",
    size="small",
)

Template:

JavaScript
<button
    class={[
        styles.root,
        styles[`variant_${props.variant}`],
        styles[`size_${props.size}`]
    ]}
>
    {children}
</button>

CSS:

CSS
.root {
    display: inline-flex;
}

.variant_primary {
    background: var(--hedron-color-primary);
}

.variant_danger {
    background: var(--hedron-color-danger);
}

.size_small {
    min-height: 2rem;
}

.size_medium {
    min-height: 2.5rem;
}

The compiler can validate that every allowed Literal variant has a corresponding style when the component asks for exhaustive style checking.

Python
Run
class ButtonProps(Props):
    variant: Literal["primary", "secondary", "danger"] = "primary"

Diagnostic:

HEDRON3417: Style variant is incomplete.

ButtonProps.variant supports:
    primary
    secondary
    danger

styles.css defines:
    variant_primary
    variant_secondary

Missing:
    variant_danger

That would be a powerful Hedron-specific improvement.

Cascade layers

Hedron should establish a predictable application-wide layer order.

CSS cascade layers allow authors to define precedence between groups of rules without relying only on selector specificity or source order.
MDN Web Docs
+1

A default structure might be:

CSS
@layer reset, tokens, base, components, utilities, overrides;

Hedron-generated component CSS lives inside:

CSS
@layer components {
    .h_UserCard_root_d7k3p {
        ...
    }
}

Application overrides:

CSS
@layer overrides {
    .admin-dashboard .h_UserCard_root_d7k3p {
        ...
    }
}

This gives users an intentional escape hatch without specificity wars.

Recommended order:

reset
tokens
base
components
utilities
overrides

Third-party design systems could register their own layers, but Hedron must keep ordering deterministic.

Asset collection

Because Hedron knows the rendered component graph, it can collect required styles.

UsersPage
├── AppLayout
│   ├── Navbar
│   └── Sidebar
└── UserTable
    ├── Table
    ├── Pagination
    └── Button

The page asset manifest becomes:

AppLayout.css
Navbar.css
Sidebar.css
UserTable.css
Table.css
Pagination.css
Button.css

Duplicates are removed.

This enables two delivery strategies.

Application bundle

Create one stylesheet containing all registered component styles:

HTML
<link rel="stylesheet" href="/_hedron/assets/app.7d92c.css">

Best for:

small and medium applications

predictable caching

simple deployment

avoiding style-loading flashes

This should be the MVP default.

Route-aware bundles

Generate per-page bundles based on known component dependencies:

HTML
<link
    rel="stylesheet"
    href="/_hedron/assets/pages/users.a18d2.css"
>

Best for:

large applications

package ecosystems

minimizing unused CSS

However, static dependency analysis can miss dynamically chosen components. Route-aware bundling therefore needs a safe fallback or declared dynamic dependencies.

HTMX and dynamically loaded components

This is the hardest part.

Suppose UserStats is loaded later:

HTML
<section
    hx-get="/_hedron/components/user-stats"
    hx-trigger="load"
>
</section>

Its CSS might not be present in the original page.

Hedron needs an explicit policy.

Strategy A: all component CSS loaded up front

Simple, reliable, and ideal for the MVP.

Initial page includes the application component bundle.
Any later HTMX fragment already has its styles.
Strategy B: fragment declares missing assets

An addressable component response can include an asset header:

http
Hedron-Assets: user-stats.4c91.css

A tiny Hedron browser bridge loads it before or alongside the swap.

Advantages:

smaller initial payload

true component-level code splitting

Disadvantages:

requires client runtime support

potential flash of unstyled content

race conditions

cache and CSP complexity

Strategy C: out-of-band stylesheet injection

The response could contain:

HTML
<link
    rel="stylesheet"
    href="/_hedron/assets/user-stats.4c91.css"
    hx-swap-oob="beforeend:head"
>

This uses HTMX behavior, but stylesheet loading timing around the fragment swap still requires careful testing.

My recommendation:

MVP: load one deduplicated application stylesheet.

Later: route-aware bundles.

Advanced future: dynamic component asset negotiation.

Do not let sophisticated CSS splitting block a working first release.

Stylesheet compilation

Hedron should parse CSS structurally, not use regular expressions.

The compiler must understand:

class selectors

selector lists

pseudo-classes

pseudo-elements

nested selectors

:global() and :local()

keyframes

animation references

@media

@supports

@container

@layer

URLs

comments and source locations

Pipeline:

styles.css
    ↓
CSS parser
    ↓
stylesheet AST
    ↓
local-symbol discovery
    ↓
stable-name generation
    ↓
selector and animation rewriting
    ↓
dependency and asset analysis
    ↓
compiled CSS + style symbol manifest

Manifest:

JSON
{
  "component": "app.components.UserCard",
  "classes": {
    "root": "h_UserCard_root_d7k3p",
    "header": "h_UserCard_header_j2m8c",
    "name": "h_UserCard_name_r4s1q"
  },
  "animations": {
    "fade-in": "h_UserCard_fade_in_k2d4"
  },
  "assets": [],
  "content_hash": "..."
}

HDN and Python components consume the manifest.

URL handling

Relative resources should be component-relative:

CSS
.avatar {
    background-image: url("./default-avatar.svg");
}

Hedron resolves that asset from the component folder, fingerprints it, and rewrites the URL:

CSS
.h_UserCard_avatar_t1p9 {
    background-image:
        url("/_hedron/assets/default-avatar.51f9a.svg");
}

The same should work for:

fonts

images

SVGs

other static CSS resources

Remote URLs and data URLs may remain unchanged, subject to application security policy.

Development behavior

Development mode should prioritize inspectability.

Python
Run
app = Hedron(
    dev=True,
    styles="scoped",
)

Behavior:

watch component styles

recompile changed files

preserve readable generated names

emit source mappings where practical

invalidate only affected component manifests

show diagnostics in the Explorer

refresh previews automatically

The Explorer’s Styles panel could show:

Authored CSS
Compiled CSS
Class map
Animations
Tokens used
Assets
Consumers
Diagnostics

It should also explain exactly why a class appears on an element.

Production behavior

Production build:

Bash
hedron build

Produces:

dist/
├── assets/
│   ├── app.2a81f.css
│   ├── logo.3b92e.svg
│   └── manifest.json
└── hedron-manifest.json

Features:

deterministic fingerprints

minification

duplicate removal

optional route bundles

integrity hashes

immutable cache headers

no runtime CSS compilation

Server-rendered pages reference fingerprinted assets.

Component packages

A third-party package could ship styles with components:

hedron_admin/
└── components/
    └── AdminSidebar/
        ├── component.py
        ├── template.hdn
        └── styles.css

When installed, Hedron registers:

component definition

style manifest

assets

theme tokens

Explorer examples

Package CSS should remain isolated by default.

This supports design systems such as:

hedron-uswds
hedron-bootstrap
hedron-carbon

But these packages may often wrap global external design-system classes rather than transform every external stylesheet. Hedron must support both:

locally scoped component styles

explicitly global framework styles

Overrides

Users need controlled ways to override packaged component styles.

Semantic props

Preferred:

Python
Run
Button(
    variant="danger",
    size="small",
)
Extra class
Python
Run
Button(
    class_="admin-delete-button",
)
CSS variables
Python
Run
Button(
    style={
        "--hedron-button-radius": "0",
    }
)
Cascade override layer
CSS
@layer overrides {
    .admin-delete-button {
        min-width: 12rem;
    }
}
Eject styles
Bash
hedron eject Button --styles

Copies the built-in component stylesheet locally.

Avoid introducing a complex “theme override language” until real use cases establish what is necessary.

Shadow DOM and Web Components

Scoped styles and Shadow DOM solve different problems.

Hedron components:

usually render into light DOM

use transformed class names

work naturally with HTMX and global themes

Web Components:

may use Shadow DOM

may own their styles internally

can optionally consume shared custom properties

For a Shadow DOM component:

CSS
:host {
    color: var(--hedron-color-text);
}

Hedron should not try to rewrite CSS inside an independently packaged Web Component unless that package opts into Hedron’s style compiler.

Security and CSP

Server-side scoped styles are favorable for strict Content Security Policy because they can be served as external stylesheets rather than injecting dynamic style tags.

Prefer:

HTML
<link rel="stylesheet" href="/assets/app.2a81f.css">

over:

HTML
<style>...</style>

Inline style attributes should remain available but may conflict with strict CSP configurations. Hedron should document that and offer a mode that rejects dynamic inline styles.

Python
Run
app = Hedron(
    security=SecurityConfig(
        allow_inline_styles=False,
    )
)

Then:

Python
Run
Div(style={"color": props.color})

produces a clear diagnostic recommending a class, variant, or CSS custom property strategy.

What should be automatic

Hedron can safely infer:

stylesheet ownership from component folder

local class mappings

required page styles

duplicate removal

stable asset fingerprints

style dependencies

keyframe renaming

component preview styles

development reload behavior

Hedron should not infer:

design intent

which arbitrary color represents “danger”

which style should override another package

whether a global selector is safe

whether arbitrary prop values should become CSS

The same framework rule applies:

Infer mechanics from explicit intent; do not infer design intent.

Proposed public API
Convention-only
UserCard/
├── component.py
└── styles.css

No registration required.

Explicit attachment
Python
Run
from hedron import Component, scoped_styles

styles = scoped_styles("./UserCard.css")


class UserCard(Component):
    styles = styles
HDN
JavaScript
<article class={styles.root}>
    <h2 class={styles.title}>{props.name}</h2>
</article>
Python
Python
Run
return Article(
    H2(props.name, class_=styles.title),
    class_=styles.root,
)
Inline global class
Python
Run
return UserCard(
    class_="dashboard-user-card",
)
Recommended MVP scope

Build:

One styles.css file per component

Local class names by default

styles.name references in HDN and Python

Stable generated class names

Keyframe scoping

Explicit :global(...)

Global application stylesheet

CSS custom-property themes

One application CSS bundle

Development recompilation

Explorer Styles panel

Clear diagnostics

Defer:

CSS composition across component files

route-level CSS splitting

dynamic HTMX asset loading

Sass/Less support

arbitrary CSS-in-Python

automatic unused-selector removal

advanced minification

browser-side hot style replacement

a full design-token compiler

Final positioning

I would describe it this way:

Hedron Scoped Styles provide CSS Modules-style isolation without Node.js or a browser-side styling runtime. Each component owns ordinary CSS, Hedron compiles its local classes and animations into collision-free names, and the server automatically delivers the styles required by the application.

That directly fits the larger framework:

Props define component inputs.
HDN or Python defines component structure.
Scoped Styles define component presentation.
FastAPI defines component transport.
HTMX defines component interaction.
The Explorer makes every inferred behavior visible.
Sources

## 87. You

Add your recommendations to the plan document

## 88. ChatGPT

Worked for 46s

I added Hedron Scoped Styles to the architecture plan as a first-class subsystem.

The new section covers:

Component-local styles.css

Typed styles.root references in HDN and Python

Stable collision-free class names

Scoped keyframes and animation references

:global(...) escape behavior

Semantic variants, design tokens, and themes

Cascade layers and override rules

Component asset discovery and fingerprinting

HTMX fragment styling strategy

CSS compilation pipeline and manifests

Component Explorer Styles panel

Development and production behavior

CSP considerations

Web Component and Shadow DOM boundaries

Explicit MVP and deferred-feature scopes

Hedron_Architecture_Plan_v11.docx

Hedron_Architecture_Plan_v11.docx
Document

## 89. You

Let’s explore security aspects and features

## 90. ChatGPT

Security should be designed into Hedron’s component model rather than added later as middleware. Hedron introduces some unusual attack surfaces because components can become endpoints, HTMX generates requests automatically, and the Explorer exposes internal application structure.

The security goal should be:

Secure defaults for framework mechanics, while authentication and business authorization remain explicit application responsibilities.

1. Context-aware output escaping

Every ordinary value rendered into HDN or Python components must be escaped automatically.

JavaScript
<p>{props.comment}</p>

If props.comment contains:

HTML
<script>alert("xss")</script>

Hedron must render it as text, not executable markup. OWASP recommends context-sensitive server-side output encoding because the correct escaping depends on whether data is inserted into HTML text, an attribute, a URL, CSS, or JavaScript.
OWASP Cheat Sheet Series
+1

Hedron should distinguish these contexts:

HTML text
HTML attribute
URL attribute
CSS value
JSON embedded in HTML
JavaScript — preferably unsupported in HDN expressions

The compiler should know the context:

JavaScript
<p>{props.message}</p>
<a href={props.url}>Open</a>
<div data-value={props.value}></div>

It should not use one generic html.escape() operation everywhere.

Trusted HTML

Raw HTML must require an explicit trusted type:

Python
Run
from hedron import TrustedHtml

class ArticleProps(Props):
    body: TrustedHtml
JavaScript
<article>{html(props.body)}</article>

This should be impossible with a normal str.

Python
Run
Article(body=user_supplied_text)

should not silently become trusted HTML.

Hedron should also offer an optional sanitizer integration:

Python
Run
safe_body = sanitize_html(
    user_html,
    policy="article",
)

But sanitization and trust-marking must remain separate concepts.

2. Safe URL handling

Escaping a URL is not enough. A malicious value such as a javascript: URL may remain dangerous even when HTML-escaped.

Hedron should provide a URL type:

Python
Run
from hedron import SafeUrl

class LinkProps(Props):
    href: SafeUrl

Default policy:

Permit relative HTTP paths.

Permit https.

Permit http in development or when configured.

Permit mailto and tel only when explicitly supported.

Reject javascript:, vbscript:, unsafe data: URLs, and control-character obfuscation.

For URL-bearing attributes, Hedron should validate schemes automatically:

JavaScript
<a href={props.href}>Open</a>
<img src={props.image_url} alt={props.alt}>
<form action={props.action}>

Developers could explicitly relax the policy, but unsafe schemes should never work by accident.

3. CSRF protection for HTMX actions

HTMX makes state-changing requests easy, but cookie-authenticated POST, PUT, PATCH, and DELETE endpoints still need CSRF protection. SameSite cookies help, but OWASP cautions that SameSite operates at the site level rather than strictly at the origin level, so it should not be treated as the only defense.
OWASP Cheat Sheet Series
+1

Hedron should provide built-in CSRF support:

Python
Run
app = Hedron(
    security=SecurityConfig(
        csrf=True,
    )
)

Generated requests include a token automatically:

HTML
<button
    hx-delete="/users/42"
    hx-headers='{"X-CSRF-Token":"..."}'>
    Delete
</button>

Recommended validation:

Synchronizer token or signed double-submit token.

Validate the token on unsafe methods.

Validate Origin when present.

Fall back to strict Referer validation where appropriate.

Reject missing or invalid tokens.

Use constant-time token comparisons.

Rotate tokens when session identity changes.

Actions should declare whether they mutate state:

Python
Run
@app.action(
    "/users/{user_id}",
    method="delete",
)
def delete_user(...) -> UserTable:
    ...

Hedron can infer that CSRF protection is required from the method. It should never infer that a GET endpoint is allowed to mutate state.

4. Authorization on addressable components

Automatically created component resources must not accidentally bypass authorization used by their parent page.

Consider:

Python
Run
@app.page(
    "/admin",
    dependencies=[Depends(require_admin)],
)
def admin_page() -> AdminPage:
    return AdminPage(
        users=UserTable()
    )

If UserTable becomes independently addressable at:

/_hedron/components/user-table

it must not become public simply because the page was protected.

Hedron needs explicit authorization inheritance rules.

Recommended rule

Addressable components should require one of:

Python
Run
@addressable(
    dependencies=[Depends(require_admin)],
)
def UserTable(...) -> UserTableComponent:
    ...

or:

Python
Run
@addressable(
    inherit_security=True,
)

But inherit_security=True is only meaningful when the component has one unambiguous security context.

If a component is used in both public and admin contexts, Hedron should require explicit security:

HEDRON4102: UserTable is addressable but has no explicit authorization policy.

It is rendered from routes with different security requirements:
    /users
    /admin/users

Declare dependencies on the component resource or disable addressability.
Secure default

Do not expose a component endpoint merely because a component appears in a page.

Addressability should require:

an explicit decorator,

an explicit component base class,

or an explicit configuration entry.

5. Component props are untrusted HTTP input

When addressable component props come from query parameters or form data, they must be validated exactly like FastAPI request inputs.

Python
Run
@addressable
def UserTable(
    team_id: int,
    page: int = 1,
    page_size: int = Query(default=25, ge=1, le=100),
) -> UserTableComponent:
    ...

The component constructor itself may accept richer internal data:

Python
Run
UserTable(rows=users)

But its public endpoint should not automatically expose every internal prop.

This distinction is critical:

Component props
≠
Public HTTP input contract

For example:

Python
Run
class UserTableProps(Props):
    rows: list[User]
    can_delete: bool
    current_user: User

Hedron must not generate a public endpoint accepting arbitrary rows, can_delete, or current_user from the client.

Instead, addressable component factories define public inputs:

Python
Run
@addressable
def user_table_resource(
    team_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_user),
) -> UserTable:
    rows = service.list_for_user(team_id, current_user)

    return UserTable(
        rows=rows,
        can_delete=current_user.can_delete_users,
    )

This prevents mass assignment and client-controlled privilege props.

6. Typed actions should be capability-safe

A rendered action reference should contain only what the browser needs.

Python
Run
Button(
    "Delete",
    action=delete_user(user_id=user.id),
)

It should compile to a route and validated public parameters—not serialize:

dependency objects,

database models,

authorization decisions,

Python callables,

arbitrary internal state.

Hedron should distinguish:

Action definition
Action binding
HTTP representation

A binding can be signed when it contains sensitive or server-derived parameters:

Python
Run
action=download_report.bind(
    report_id=report.id,
    scope=Signed("finance"),
)

However, signatures must not replace authorization. A valid signed argument only proves that Hedron created it; the endpoint must still verify that the current user may perform the action.

7. Dangerous HTMX attributes

Injected HTMX attributes can create requests or modify the page even without a <script> tag. Therefore, untrusted users must never control arbitrary attribute names or raw HTMX configuration.

Unsafe:

Python
Run
Div(attrs=user_supplied_attributes)

Safer:

Python
Run
Div(
    aria=user_supplied_aria_values,
    data=validated_data_attributes,
)

Hedron should have separate policies for:

standard HTML attributes,

aria-*,

data-*,

HTMX attributes,

event attributes,

raw attributes.

Dynamic attribute names should be rejected by default.

Python
Run
Element(
    "div",
    attrs={props.attribute_name: props.value},
)

Diagnostic:

HEDRON4207: Dynamic attribute names are not permitted in portable components.

Use an explicit attribute, a validated data attribute, or TrustedAttributes.

Any hx-* attributes derived from raw strings should be visible in the Explorer and included in security diagnostics.

8. Content Security Policy

Hedron’s server-rendered architecture and external scoped-style bundles can work well with a strict Content Security Policy because the framework does not need to inject arbitrary runtime JavaScript or a CSS-in-JS runtime.

A secure production configuration should support:

Python
Run
app = Hedron(
    security=SecurityConfig(
        content_security_policy="strict",
        allow_inline_scripts=False,
        allow_inline_styles=False,
    )
)

Hedron should generate or help configure:

Content-Security-Policy

X-Content-Type-Options: nosniff

Referrer-Policy

clickjacking protection through frame-ancestors

Permissions-Policy

optional COOP/COEP policies

OWASP recommends security response headers as an important defense against XSS, clickjacking, information disclosure, and related browser risks.
OWASP Cheat Sheet Series

Avoid inline behavior by default

The following should be discouraged or prohibited in strict mode:

HTML
onclick="..."
style="..."
<script>...</script>

Hedron should serve:

HTMX as a pinned external asset,

Hedron’s browser bridge as an external asset,

compiled scoped CSS as external stylesheets.

Dynamic browser behavior belongs in registered Web Components with CSP-compatible asset loading.

9. HTMX history and sensitive content

HTMX can save page snapshots in browser storage for history restoration. Its documentation notes that hx-history="false" can prevent sensitive data from entering that history cache.
htmx

Hedron should allow components and pages to declare sensitivity:

Python
Run
class AccountPage(Page):
    sensitive = True

or:

Python
Run
@app.page(
    "/account",
    history_cache=False,
)

Hedron emits:

HTML
<body hx-history="false">

Potential automatic warnings:

HEDRON4314: Page contains fields marked `secret` but HTMX history caching is enabled.

Sensitive components include:

account recovery data,

medical or financial details,

one-time credentials,

administrative reports,

personally identifiable information on shared devices.

10. Explorer security

The Component Explorer may expose:

source file locations,

internal endpoint names,

component props,

dependency graphs,

rendered data,

request simulators,

error traces,

configuration,

database-backed examples.

It must be disabled in production by default.

Python
Run
app = Hedron(
    dev=False,
)

should result in no Explorer routes being registered.

Production enablement should require explicit configuration and authentication:

Python
Run
app = Hedron(
    explorer=ExplorerConfig(
        enabled=True,
        dependencies=[
            Depends(require_platform_admin),
        ],
        expose_source=False,
        allow_requests=False,
    )
)

Recommended controls:

Authentication required.

Authorization separate from ordinary user roles.

CSRF protection for simulated mutations.

No secret or credential fields shown.

Redact request headers such as Authorization and cookies.

Disable arbitrary request headers.

Rate-limit request simulation.

Audit Explorer actions.

Never expose local absolute paths in production.

Prevent loading arbitrary modules or files by name.

Use a separate route namespace that cannot conflict with application routes.

11. Secret-aware fields

Hedron models should support fields that are never rendered, logged, serialized into the Explorer, or included in component debug markers.

Python
Run
class LoginForm(FormModel):
    username: str
    password: Secret = Field(
        autocomplete="current-password",
    )

Secret values should:

have redacted repr,

be excluded from component diagnostics,

not appear in OpenAPI examples by default,

not be persisted in history snapshots,

not be included in component identity hashes,

not be echoed back into invalid forms unless deliberately allowed.

The Explorer should display:

password: [REDACTED]

not the original value.

12. Safe form defaults

Generated forms should automatically include:

CSRF tokens when applicable.

Correct autocomplete values.

method="post" for mutation forms.

No secrets in query strings.

File-upload size and content-type constraints.

Accessible error messages without reflecting raw HTML.

Safe redirect handling after submission.

Login and password forms should never default to GET.

13. Redirect safety

Typed actions may return redirects:

Python
Run
return Redirect(next_url)

If next_url originates from a query parameter, this can create an open redirect.

Hedron should provide:

Python
Run
return LocalRedirect(next_url)

which accepts only:

application-relative URLs,

or configured trusted origins.

External redirects require an explicit type:

Python
Run
return ExternalRedirect(
    trusted_partner_url,
)

This makes risky behavior visible in code review.

14. Scoped-style security

The CSS compiler introduces additional security concerns:

path traversal through url(...),

arbitrary file inclusion,

remote asset fetching,

malicious CSS in third-party component packages,

inline-style injection,

CSS data exfiltration techniques.

Recommended defaults:

Component-relative assets must remain inside registered asset roots.

Reject ../ paths escaping the component/package root.

Never fetch remote CSS assets during application startup by default.

Fingerprint and serve local assets.

Disallow user-controlled raw CSS.

Treat third-party component CSS as executable browser content for trust purposes.

Allow strict mode to reject inline styles and remote font/style URLs.

15. Template and file-system safety

HDN includes and component discovery must never accept request-controlled filesystem paths.

Unsafe conceptual behavior:

/_hedron/preview?template=../../etc/passwd

All templates, components, and assets should be resolved through prebuilt registries with opaque identifiers.

component_id = "app.users.UserCard"

not arbitrary filesystem paths.

The compiler should:

resolve symlinks,

enforce configured roots,

reject path escapes,

avoid executing imported application modules merely to inspect untrusted packages where possible.

16. Caching and user-specific fragments

Addressable components may render user-specific or permission-specific HTML.

Hedron must not cache such fragments publicly by default.

Safe default:

http
Cache-Control: private, no-store

for authenticated component responses unless the developer declares otherwise.

Public components can opt into caching:

Python
Run
@addressable(
    cache=CachePolicy.public(max_age=300),
)
def PublicStats(...) -> Stats:
    ...

Cache keys must account for all declared varying dimensions:

route and query parameters,

locale,

theme if it affects markup,

authorization scope,

relevant headers,

component version.

Hedron should warn when a response uses authentication dependencies with public caching:

HEDRON4408: Component UserMenu depends on the authenticated user but declares a public cache policy.
17. Authentication should remain framework-native

Hedron should not invent a separate authentication system.

For FastAPI, it should preserve:

Depends

Security

OAuth2 schemes

security scopes

application-specific session or token systems

FastAPI provides standard security utilities and supports OAuth2 scopes and other authentication approaches.
FastAPI
+1

Hedron’s responsibility is to:

preserve security dependencies on component endpoints,

document them correctly,

make inferred endpoint exposure visible,

prevent UI abstractions from bypassing authorization.

Flask and Django adapters should use their native security mechanisms. Django’s built-in CSRF middleware, for example, should remain authoritative in the Django integration rather than being replaced by an incompatible Hedron implementation.
Django Project

18. Secure dependency and package model

Third-party Hedron component packages can ship:

Python code,

HDN templates,

CSS,

JavaScript/Web Components,

Explorer plugins.

They are not passive theme files; installing one is equivalent to installing executable application code.

Hedron should support:

Bash
hedron audit-components

Possible output:

Package: hedron-admin 1.4.0

Python code              yes
HDN templates            18
Scoped styles            18
Browser JavaScript       yes
Explorer plugin          yes
Remote assets            none
Unsafe raw HTML APIs      1 usage
Dynamic attributes        0

This does not replace dependency-scanning tools, but it helps developers understand what capabilities a Hedron package uses.

19. Security diagnostics in the Explorer

A dedicated Security panel should report:

UserTable

✓ Text expressions are escaped
✓ No unsafe URL schemes
✓ CSRF enabled on all mutations
✓ Authorization dependency declared
✓ No secret props exposed
⚠ HTMX history cache enabled
✕ Raw HTML used at template.hdn:42

Framework-wide checks:

Public addressable components without explicit exposure intent.

Mutation routes without CSRF protection.

Components with security-context ambiguity.

Raw HTML usage.

Dynamic HTMX attributes.

Unsafe URLs.

Public caching of authenticated content.

Explorer enabled without authentication.

Missing security headers.

Sensitive fields included in history-enabled pages.

Inline scripts/styles under strict CSP.

External assets without integrity or allowlisting.

Every diagnostic should explain:

What Hedron found.

Why it matters.

Where it occurs.

The secure default.

How to override it deliberately.

20. Security modes

Hedron could offer opinionated profiles:

Python
Run
app = Hedron(
    security="standard",
)
Development
Useful diagnostics
Explorer enabled locally
Readable tracebacks
Relaxed asset CSP where necessary
No production secrets
Standard
Automatic escaping
CSRF enabled
Secure headers
Explorer disabled
Strict component exposure
Private authenticated caching
Strict
No raw HTML without an allowlisted sanitizer
No inline scripts or styles
No remote component assets
Explicit public-route declarations
Explicit URL schemes
No dynamic attributes
Security warnings treated as build failures

A government or high-assurance environment could use:

Python
Run
app = Hedron(
    security=SecurityConfig.strict(),
)
21. Build-time security checks
Bash
hedron check --security

should run without starting the application where possible.

It could analyze:

component specifications,

HDN ASTs,

scoped CSS,

route metadata,

action methods,

OpenAPI metadata,

Explorer configuration,

static asset manifests.

CI mode:

Bash
hedron check --security --fail-on warning

Output formats:

Bash
hedron check --security --format text
hedron check --security --format json
hedron check --security --format sarif

SARIF output would allow integration with code-scanning systems.

Recommended MVP security scope

The first release should include:

Context-aware escaping for text and attributes.

Explicit TrustedHtml.

Safe URL validation.

CSRF support for unsafe HTMX methods.

Explicit addressable-component exposure.

FastAPI dependency preservation.

Secret/redacted model fields.

Secure response headers.

Explorer disabled outside development.

Private/no-store defaults for authenticated component resources.

Filesystem-safe template and asset resolution.

Security diagnostics for raw HTML, missing CSRF, exposed Explorer, and ambiguous authorization.

hedron check --security.

Defer initially:

an HTML sanitizer maintained by Hedron itself,

signed action payload systems,

advanced package capability sandboxing,

runtime browser security scanning,

automated CSP nonce orchestration,

full software supply-chain attestation.

Hedron should integrate proven sanitizers and authentication tools rather than implementing cryptography or sanitization algorithms itself.

Recommended security principle

Add this to the architecture plan:

Hedron may automate security mechanics when the secure interpretation is unambiguous, but it must never infer authorization or trust. Untrusted values remain escaped, endpoint exposure remains explicit, mutations remain CSRF-protected, and every security-sensitive inference remains inspectable in the Component Explorer.

This preserves the ease of the Hedron-first experience without allowing convenience features—especially addressable components and automatic HTMX wiring—to quietly weaken the application’s security model.

Sources

## 91. You

Add security first features to our entire plan

## 92. ChatGPT

Worked for 1m 59s

I rewrote the complete Hedron plan so security is now embedded throughout the architecture rather than isolated in a single section.

Major security-first additions include:

Context-aware escaping across HTML text, attributes, URLs, CSS, and embedded data

Explicit TrustedHtml, SafeUrl, and redacted Secret types

CSRF protection for unsafe HTMX actions

Explicit exposure and authorization requirements for addressable components

Separation between internal component props and public endpoint inputs

Secure typed-action and redirect behavior

CSP-compatible external scripts and scoped styles

Secure defaults for HTMX history, caching, component identity, and user-specific fragments

Explorer authentication, redaction, request-simulation controls, and production safeguards

Scoped-style asset-root enforcement and path-traversal protections

Framework-native security rules for FastAPI, Flask, and Django

Component package and supply-chain auditing

development, standard, and strict security profiles

CI security checks with JSON and SARIF output

Security requirements integrated into every implementation phase and acceptance criterion

The final document was rendered and visually verified across all 14 pages.

Hedron_Architecture_Plan_v12_Security_First.docx

Hedron_Architecture_Plan_v12_Security_First.docx
Document

## 93. You

Research other python packages we might use as dependencies or optional integrations

## 94. ChatGPT

I think Hedron should have a very small required dependency set and a rich optional ecosystem.

If we make the core tiny, we can keep installs fast while allowing people to opt into features like Markdown, authentication, image processing, or rich text only when they need them.

Core dependencies

I would keep these mandatory.

Package	Why
FastAPI
 (hedron package only)	Primary web framework
Pydantic
	Hedron models
Starlette
	Underlying ASGI
HTMX
 (bundled asset)	Browser interaction

Nothing else.

Excellent optional dependencies
File watching

Development mode.

I actually prefer watchfiles over watchdog today because it's faster and designed for modern Python.

hedron[dev]

Could install

watchfiles

rich

typer

Watchdog is still a perfectly reasonable fallback if platform compatibility becomes an issue.
Watchdog
+1

Markdown
hedron[markdown]

Could install

markdown-it-py

pymdown-extensions

Now:

Python
Run
Markdown("""
# Hello
""")
Syntax highlighting
hedron[code]

Uses

Pygments

Great for documentation components.

HTML sanitization

I actually would not use Bleach.

Mozilla announced that Bleach is no longer maintained, including for future security fixes.
PyPI
+1

Instead I'd abstract sanitization:

Python
Run
sanitize_html(html)

and allow pluggable implementations.

Email validation

Pydantic already supports this via its optional extras.

hedron[email]

would simply enable

pydantic[email]

which installs email-validator.
Pydantic

Images
hedron[images]

Pillow

Automatic:

Python
Run
Image(
    src=user.avatar
)

Could:

resize

optimize

fingerprint

Icons

Optional integration.

Python
Run
HeroIcon("user")

or

Python
Run
LucideIcon("user")

Could automatically inline SVG.

Authentication

I think this becomes huge.

hedron-auth

Could integrate

FastAPI Users

Authlib

OAuth

JWT

Instead of inventing auth.

Database integration

Not ORM.

UI.

Python
Run
AutoTable(User)

Works with

SQLAlchemy

SQLModel

Tortoise

Adapters.

Tables

I actually think we should integrate Polars.

Especially because of your background.

Python
Run
DataTable(df)

where

Python
Run
df

can be

list

pandas

polars

Charts

Optional.

hedron[charts]

Support

Plotly

Vega-Lite

ECharts

Wrapped as Web Components.

Rich text editor

Huge feature.

hedron[editor]

Integrate

TipTap

or

ProseMirror

Code editor

Definitely.

Python
Run
CodeEditor(
    language="python"
)

Uses Monaco.

Maps

Optional.

Leaflet

MapLibre

OpenLayers

Wrapped as Web Components.

Accessibility

This one excites me.

hedron[a11y]

Could run

server-side

accessibility linting.

Testing

I think

hedron[test]

should install

pytest

pytest-httpx

syrupy

Snapshot testing.

CLI
hedron[cli]

Installs

Typer.

Explorer

Separate dependency.

hedron[explorer]

Adds

Explorer UI

Preview server

Diagnostics

Production apps don't need it.

LSP

Eventually

hedron-lsp

Separate package.

Formatter

Like

gofmt

rustfmt

We should have

hedron fmt

Probably its own package.

Interesting integrations

These are where I think Hedron could become amazing.

Faker

Imagine Explorer:

Preview

Generate fake props

Automatically.

Factory Boy

Testing.

SQLAlchemy inspection

Imagine:

Python
Run
AutoForm(User)

generated directly.

Babel

Localization.

msgspec

This one is interesting.

Maybe

Future.

Not now.

AnyIO

Already through FastAPI.

NiceGUI inspiration

One thing I noticed while researching UI frameworks:

Most try to own

everything.

I think Hedron should be

the opposite.

Instead of

Hedron Charts

Use

Plotly.

Instead of

Hedron Auth

Use

FastAPI Users.

Instead of

Hedron ORM

Use

SQLAlchemy.

Instead of

Hedron Markdown

Use

markdown-it-py.

Become

the glue.

Not

the replacement.

What I would avoid

I would not depend directly on:

Jinja

BeautifulSoup

lxml

Jinja is an excellent template engine with autoescaping, but Hedron is creating its own rendering model, so it shouldn't depend on Jinja just because it's popular.
Jinja

Similarly, BeautifulSoup and lxml are fantastic for parsing arbitrary HTML, but Hedron should generally render from its own component tree rather than round-tripping through HTML parsers.

One thing I think we should steal

While searching I found a small project called htmforge. It independently arrived at some ideas we've been discussing: typed HTML components, Pydantic models, FastAPI/Flask/Django adapters, and typed HTMX attributes.
Reddit
+1

I don't think Hedron should copy its API, but it's worth studying because:

it validates that people want this style of development,

it may reveal usability issues,

and it gives us another perspective on what worked and what didn't.

My recommendation

I'd divide the ecosystem like this:

hedron
│
├── Core
│   ├── FastAPI
│   ├── Pydantic
│   ├── Components
│   ├── Rendering
│   ├── HDN
│   └── HTMX
│
├── Official Plugins
│   ├── hedron-explorer
│   ├── hedron-auth
│   ├── hedron-markdown
│   ├── hedron-charts
│   ├── hedron-editor
│   ├── hedron-testing
│   ├── hedron-icons
│   ├── hedron-lsp
│   └── hedron-cli
│
└── Third-party
    ├── hedron-bootstrap
    ├── hedron-tailwind
    ├── hedron-uswds
    ├── hedron-admin
    └── hedron-crud

I think that's a much more sustainable ecosystem than trying to ship every feature inside the core framework.

Sources

## 95. You

Let’s also explore data visualization packages

## 96. ChatGPT

Worked for 19s

Data visualization could become one of Hedron’s strongest integration areas, especially for internal dashboards and analytical FastAPI applications. I would avoid creating a proprietary charting grammar immediately. Hedron should normalize data and lifecycle behavior while allowing established visualization libraries to supply the actual chart specifications.

Recommended architecture

Hedron should expose one component contract:

Python
Run
Chart(
    figure,
    title="Monthly revenue",
    lazy=True,
    refreshable=True,
)

The figure may be a Plotly figure, Altair chart, Bokeh model, Matplotlib figure, or another registered visualization object. Hedron selects an installed adapter:

Chart
  ↓
Visualization adapter
  ↓
Portable chart specification or rendered asset
  ↓
Hedron chart Web Component
  ↓
HTML + browser visualization runtime

This keeps the component API stable without forcing all chart libraries into the same lowest-common-denominator API.

Best candidates
1. Plotly: primary interactive integration

Plotly should probably be Hedron’s first official interactive chart integration. Its Python library supports more than 40 chart types, and figures can be exported as interactive HTML or static images. That makes it suitable for normal dashboards, scientific visualizations, finance charts, geographic charts, and exploratory interfaces.
Plotly
+2
Plotly
+2

Bash
pip install "hedron[plotly]"
Python
Run
import plotly.express as px
from hedron import PlotlyChart

figure = px.line(
    revenue,
    x="month",
    y="amount",
)

return PlotlyChart(
    figure,
    responsive=True,
)

Hedron should not use Plotly’s full standalone HTML export for every chart because that can repeat scripts and surrounding markup. The adapter should extract the figure’s JSON specification, register one Plotly browser asset for the page, and initialize each chart through a Hedron Web Component.

HTML
<hedron-plotly
    chart-id="monthly-revenue"
    spec-url="/_hedron/charts/monthly-revenue/spec">
</hedron-plotly>

This also fits addressable components:

Python
Run
@addressable
def RevenueChart(
    period: str = "12m",
    service: RevenueService = Depends(get_revenue_service),
) -> PlotlyChart:
    data = service.for_period(period)
    return PlotlyChart(build_revenue_figure(data))

HTMX could replace the complete chart component or only update its specification.

Plotly Resampler

For high-frequency time series, plotly-resampler is worth a later optional integration. It wraps Plotly figures and dynamically aggregates time-series data according to the current view, improving responsiveness during zooming and panning.
Predict Idlab
+1

That likely requires a dedicated Hedron endpoint for relayout events rather than treating it as a static Plotly figure:

Python
Run
LargeTimeSeriesChart(
    data=measurements,
    x="timestamp",
    y="value",
    resample=True,
)

I would defer this until basic Plotly support is stable.

2. Vega-Altair: best declarative integration

Altair may be the most architecturally natural fit for Hedron. It is a declarative Python visualization library built on the Vega-Lite grammar, meaning the Python object compiles into a portable JSON visualization specification.
Vega-Altair
+2
Vega-Altair
+2

Bash
pip install "hedron[altair]"
Python
Run
import altair as alt
from hedron import AltairChart

figure = (
    alt.Chart(data)
    .mark_line()
    .encode(
        x="month:T",
        y="revenue:Q",
        color="segment:N",
    )
)

return AltairChart(figure)

Hedron can serialize the Vega-Lite specification and pass it to a browser component:

HTML
<hedron-vega-lite
    spec-url="/_hedron/charts/revenue/spec">
</hedron-vega-lite>

Altair’s declarative nature gives Hedron several advantages:

specifications can be validated before rendering;

charts can be inspected in the Component Explorer;

generated JSON can be cached;

chart fields can be checked against DataFrame columns;

chart specifications can be exported or tested without a browser.

For larger datasets, Altair documents VegaFusion as its recommended transformer. VegaFusion evaluates many data transformations outside the browser, often reducing how much data must be included in the final chart specification.
Vega-Altair
+1

Bash
pip install "hedron[altair-large]"

That extra could install:

altair
vegafusion
vl-convert-python

vl-convert-python can also produce SVG or PNG output without an external Node-based conversion process, making it valuable for static exports, email, PDFs, and accessibility fallbacks.
Vega-Altair

3. Matplotlib: primary static-chart integration

Matplotlib should be the standard static integration. Its noninteractive backends can produce PNG, SVG, PDF, and other hardcopy formats, and its documentation includes patterns for embedding output in web applications.
Matplotlib
+2
Matplotlib
+2

Bash
pip install "hedron[matplotlib]"
Python
Run
from hedron import MatplotlibChart

figure, axis = plt.subplots()
axis.plot(months, revenue)

return MatplotlibChart(
    figure,
    format="svg",
    alt="Revenue rose steadily from January through June.",
)

SVG should be preferred when:

the chart is primarily lines, text, or shapes;

scalable output is desirable;

the SVG size remains reasonable.

PNG should be preferred when:

the figure contains dense raster-like data;

the SVG would contain extremely many elements;

Matplotlib rasterization materially reduces payload size.

Hedron should render charts to an asset endpoint rather than embedding unrestricted SVG automatically:

HTML
<figure>
    <img
        src="/_hedron/charts/revenue.svg"
        alt="Revenue rose steadily from January through June."
    >
</figure>

An explicit trusted SVG path could be added later, but SVG is active XML content and should not be treated as ordinary harmless text.

4. Pygal: lightweight server-generated SVG

Pygal is interesting because it is Python-native and renders charts directly to SVG. Its documented output API can return SVG as bytes or Unicode.
Pygal
+2
GitHub
+2

Bash
pip install "hedron[pygal]"
Python
Run
chart = pygal.Bar()
chart.add("Revenue", [12, 18, 23, 27])

return PygalChart(
    chart,
    alt="Quarterly revenue increased in each period.",
)

It could be a good option for:

lightweight dashboards;

reports;

environments where large JavaScript chart runtimes are undesirable;

simple interactive SVG charts;

strict no-Node deployments.

I would support Pygal after Plotly, Altair, and Matplotlib. Its scope is useful, but it should not become Hedron’s default chart engine.

5. Bokeh: advanced interactive option

Bokeh supports embedding standalone documents and server-backed content into web pages. Its embedding APIs can produce JSON blocks used to embed standalone models.
Bokeh
+1

Bash
pip install "hedron[bokeh]"
Python
Run
return BokehChart(figure)

Standalone Bokeh charts are feasible, but Bokeh server applications introduce their own server-side session and callback model. Hedron should initially support only standalone embedded Bokeh models. It should not attempt to transparently merge Bokeh Server’s application lifecycle into FastAPI and HTMX.

A later advanced adapter might allow a separately deployed Bokeh server to be embedded, but that is closer to service integration than ordinary component rendering.

6. ECharts and pyecharts: broad chart catalog

Apache ECharts provides more than 20 built-in chart types and composable visualization components. pyecharts is a Python plotting library built around ECharts and advertises more than 30 chart kinds along with broad map support.
Pyecharts
+2
Apache ECharts
+2

There are two possible Hedron integrations:

Accept pyecharts objects
Bash
pip install "hedron[pyecharts]"
Python
Run
return EChart(chart)
Provide a direct ECharts specification component
Python
Run
return EChart(
    option={
        "xAxis": {"data": months},
        "yAxis": {},
        "series": [{
            "type": "line",
            "data": revenue,
        }],
    }
)

The direct specification approach may be cleaner long term because ECharts’ browser representation is already a JSON-like options object. Pyecharts can remain an optional converter into that representation.

ECharts is especially attractive for:

gauges;

graph and network visualization;

tree maps;

Sankey diagrams;

geographic visualizations;

highly customized enterprise dashboards.

I would make it the second interactive backend after Plotly or Altair, not an MVP dependency.

Large-data visualization
Datashader

Datashader is specifically designed as a rendering pipeline for meaningful representations of very large datasets. It projects records into a plotting grid, aggregates them, and transforms the aggregation into a viewable image.
Datashader
+2
Datashader
+2

Bash
pip install "hedron[datashader]"
Python
Run
return DatashaderChart(
    data=points,
    x="longitude",
    y="latitude",
    aggregation="count",
    width=1000,
    height=600,
)

The natural Hedron model would be an addressable image or tile resource:

GET /_hedron/charts/traffic-density
GET /_hedron/charts/traffic-density?x_min=...&x_max=...

A browser chart could request rerendered images when the viewport changes.

Datashader should be a specialized official integration, not a general chart backend. It is ideal for:

millions of points;

dense time series;

geographic densities;

large graph layouts;

server-side rasterization.

HoloViews and hvPlot

HoloViews and hvPlot provide high-level visualization abstractions across the PyData ecosystem. hvPlot supports data sources including Pandas, Polars, XArray, Dask, GeoPandas, and NetworkX, with Bokeh, Matplotlib, and Plotly backends.
hvPlot
+2
hvPlot
+2

Instead of integrating every HoloViz application concept, Hedron could accept an hvPlot/HoloViews object and convert it through one of its supported renderers:

Python
Run
plot = df.hvplot.line(
    x="timestamp",
    y="value",
)

return HoloViewsChart(plot)

This gives data scientists a familiar workflow, but the HoloViz ecosystem is large and has its own dashboard framework in Panel. Panel is designed to build complete Python applications and dashboards, so Hedron should avoid depending on it or trying to embed its full application model.
Panel
+2
HoloViz
+2

I would classify HoloViews/hvPlot support as an interoperability plugin, not part of Hedron’s core visualization architecture.

Geospatial visualization
Folium

Folium combines Python-side data manipulation with Leaflet-based interactive web maps and can produce standalone HTML suitable for web applications.
Bokeh
+2
Folium
+2

Bash
pip install "hedron[maps-folium]"
Python
Run
return FoliumMap(map_object)

However, accepting a complete standalone Folium HTML document would create asset duplication and security concerns. The adapter should ideally extract the map HTML, required assets, and configuration into an isolated Hedron map component.

Long term, a direct MapLibreMap Web Component may give Hedron more control than wrapping Folium. Folium remains valuable for easy compatibility with existing Python geospatial workflows.

DataFrame compatibility

Hedron should not force chart data into Pandas.

The cleanest integration layer may be Narwhals, which provides a lightweight compatibility API across Pandas, Polars, PyArrow, cuDF, Modin, and several lazy frameworks without depending on all of them.
Narwhals Dev
+1

Python
Run
Chart(
    data=df,
    x="month",
    y="revenue",
)

The same call should accept:

list[dict]
Pandas DataFrame
Polars DataFrame
PyArrow Table
cuDF DataFrame
Modin DataFrame

An internal normalization layer could use Narwhals to inspect:

column names;

data types;

nullability;

row count;

categorical values;

temporal columns.

Hedron should avoid eagerly converting everything to Pandas. Instead, each visualization adapter receives the most appropriate representation.

For example:

Altair adapter       → Arrow-compatible records/spec
Plotly adapter       → arrays or records
Datashader adapter   → supported DataFrame backend
Matplotlib adapter   → NumPy-like arrays

Narwhals could be either a small core dependency for the visualization plugin or an optional dependency of hedron-data. It should not be required by users who never visualize tabular data.

Proposed package structure
hedron-charts
├── shared Chart component
├── chart registry
├── data normalization
├── asset management
├── security policies
└── accessibility contracts

hedron-plotly
hedron-altair
hedron-matplotlib
hedron-pygal
hedron-bokeh
hedron-echarts
hedron-datashader
hedron-holoviews
hedron-folium

For simpler installation, these could initially be extras of one package:

Bash
pip install "hedron-charts[plotly]"
pip install "hedron-charts[altair]"
pip install "hedron-charts[matplotlib]"
pip install "hedron-charts[all]"
Unified chart protocol

Hedron should define a narrow adapter protocol:

Python
Run
class VisualizationAdapter(Protocol):
    name: str

    def supports(self, value: object) -> bool:
        ...

    def compile(
        self,
        value: object,
        *,
        context: ChartContext,
    ) -> CompiledVisualization:
        ...

A compiled result might contain:

Python
Run
class CompiledVisualization:
    mode: Literal[
        "json-spec",
        "svg",
        "image",
        "html-fragment",
    ]

    specification: dict[str, object] | None
    asset_url: SafeUrl | None
    browser_runtime: BrowserAsset | None
    fallback: Component | None
    metadata: VisualizationMetadata

This lets Hedron handle lifecycle and security consistently across libraries.

HTMX behavior

Charts should work like addressable components:

Python
Run
RevenueChart(
    period="12m",
    refreshable=True,
)

Could render:

HTML
<hedron-chart
    data-hedron-component="RevenueChart"
    hx-get="/_hedron/components/revenue-chart?period=12m"
    hx-trigger="refresh"
    hx-target="this"
    hx-swap="outerHTML">
</hedron-chart>

For filter changes:

Python
Run
Select(
    options=periods,
    action=RevenueChart.update(
        include={"period": "this.value"},
    ),
)

The normal approach should replace the chart component with a new specification. Fine-grained in-place chart updates can be added for backends that support them, but should not complicate the initial model.

Explorer integration

Every chart should have a Visualization tab showing:

Backend                 Altair
Output mode             Vega-Lite JSON
Rows received           125,000
Rows sent to browser    240
Specification size      18.4 KB
Browser runtime         Vega-Lite
Server transform        VegaFusion
Fallback                SVG

Additional panels:

chart specification;

source data schema;

data sample;

accessibility summary;

asset dependencies;

render timing;

payload size;

generated fallback;

security warnings.

The Explorer should warn about:

extremely large browser payloads;

missing accessible description;

unbounded row serialization;

remote scripts;

unsafe embedded HTML;

charts containing sensitive fields;

public caching of user-specific data.

Accessibility requirements

Interactive visualizations must not rely solely on visual marks.

Hedron’s base chart API should require or strongly encourage:

Python
Run
Chart(
    figure,
    title="Monthly revenue",
    description=(
        "Revenue increased from $1.2 million in January "
        "to $1.8 million in June."
    ),
)

Optional structured alternatives:

Python
Run
Chart(
    figure,
    fallback=DataTable(
        rows=monthly_revenue,
    ),
)

For static figures:

Python
Run
MatplotlibChart(
    figure,
    alt="Revenue increased steadily across all six months.",
)

Hedron can generate a collapsible accessible data table for simple chart specifications, but it should not pretend to infer the meaning of arbitrary scientific visualizations.

Security

Interactive chart integrations often embed JSON and load JavaScript runtimes. Hedron should:

serialize specifications with a real JSON encoder;

never concatenate untrusted values into <script> tags;

prefer external runtime assets compatible with CSP;

prohibit arbitrary raw JavaScript callbacks by default;

allow only registered formatter and interaction identifiers;

validate external URLs and image references;

redact secret columns in Explorer previews;

cap browser-bound row counts;

make remote runtime loading opt-in;

fingerprint locally shipped JavaScript assets.

A Plotly or Vega specification may contain references, templates, HTML-like labels, URLs, or expressions. Each adapter needs its own validation policy rather than assuming all third-party specifications are inherently safe.

Recommended priority

I would implement visualization support in this order:

Matplotlib — easiest secure static integration.

Plotly — broad interactive chart support and strong recognition.

Altair/Vega-Lite — clean declarative specifications and excellent Explorer integration.

Narwhals data normalization — Pandas/Polars/Arrow compatibility.

ECharts — advanced enterprise and specialized chart types.

Datashader — large-data rendering.

Folium or direct MapLibre integration — geospatial visualization.

Pygal, Bokeh, and HoloViews adapters — ecosystem interoperability.

Product recommendation

Hedron should offer three levels:

Beginner
Python
Run
LineChart(
    data,
    x="month",
    y="revenue",
)

Hedron selects a configured default backend.

Familiar-library integration
Python
Run
PlotlyChart(plotly_figure)
AltairChart(altair_chart)
MatplotlibChart(matplotlib_figure)
Advanced custom specification
Python
Run
EChart(option=...)
VegaLiteChart(spec=...)

All three levels should compile through the same chart resource model.

The design principle should be:

Hedron owns chart lifecycle, transport, security, accessibility, and HTMX behavior. Established visualization libraries own graphical expression.

This avoids rebuilding Plotly, Altair, Matplotlib, or ECharts while still giving Hedron a coherent, beginner-friendly visualization experience.

Sources

## 97. You

Add all your package integration recommendations to the plan document

## 98. ChatGPT

Worked for 1m 56s

I added the full package-integration and data-visualization strategy to the Hedron plan.

The new revision includes:

Required versus optional dependency boundaries

hedron, hedron-core, hedron-flask, and hedron-django packaging

Development integrations such as Watchfiles, Rich, Typer, pytest, and Syrupy

Markdown, syntax highlighting, image processing, email validation, and icon integrations

Authlib, FastAPI security, SQLAlchemy, SQLModel, Django ORM, Pandas, Polars, PyArrow, and Narwhals recommendations

A unified Hedron visualization adapter protocol

Matplotlib, Plotly, Altair, ECharts, Datashader, Folium, Bokeh, HoloViews, hvPlot, and Pygal integration plans

Beginner, familiar-library, and advanced chart APIs

Large-data, geospatial, accessibility, security, HTMX, and Explorer behavior

Official extras and package roadmap

Integration acceptance criteria and updated implementation sequence

Hedron_Architecture_Plan_v13_Integrations.docx

Hedron_Architecture_Plan_v13_Integrations.docx
Document

## 99. You

I’d like an editable dataframe visualization like what what streamlit has

## 100. ChatGPT

Yes—Hedron should have a first-class DataEditor component modeled after Streamlit’s st.data_editor, but adapted to Hedron’s component-resource and HTMX architecture.

Streamlit’s editor accepts dataframe-like structures, provides column configuration, supports editable and categorical columns, and returns the edited data.
Streamlit Docs
+1

Proposed beginner API
Python
Run
from hedron import DataEditor

@app.page("/users")
def users() -> UsersPage:
    return UsersPage(
        editor=DataEditor(
            users_df,
            key="users",
        )
    )

For a saveable editor:

Python
Run
DataEditor(
    users_df,
    key="users",
    on_save=save_users,
)

With inferred column behavior:

Python
Run
class UserRow(Model):
    id: int = Field(read_only=True)
    name: str
    email: Email
    role: Literal["admin", "member"]
    active: bool = True
Python
Run
DataEditor(
    users_df,
    row_model=UserRow,
    on_save=save_users,
)

Hedron could infer:

numeric, text, Boolean and date editors;

dropdowns from Literal or enums;

required and read-only columns;

validation rules;

formatting;

column labels;

row identifiers.

Use a Web Component internally

This is one of the cases where a Web Component is clearly justified:

HTML
<hedron-data-editor
    component-id="users"
    schema-url="/_hedron/data-editors/users/schema"
    data-url="/_hedron/data-editors/users/data"
    save-url="/_hedron/data-editors/users/changes">
</hedron-data-editor>

The browser component owns:

cell selection;

keyboard navigation;

editing;

copy and paste;

local undo/redo;

temporary unsaved state;

virtualization.

Hedron and FastAPI own:

data loading;

validation;

authorization;

persistence;

conflict handling;

audit logging.

Trying to rerender the entire grid through HTMX after every keystroke would feel slow and would discard the best parts of spreadsheet-style editing.

Recommended grid engine: Tabulator

I would use Tabulator as the default engine for the initial implementation.

It provides direct cell editing, callbacks, filtering, grouping, Ajax loading and virtualized rendering. It is MIT-licensed and may be used commercially without a fee. It can also be shipped as ordinary browser JavaScript and CSS files, so Hedron users would not need Node.js.
Tabulator
+3
Tabulator
+3
GitHub
+3

Reasons it fits Hedron:

permissive licensing;

vanilla JavaScript rather than React-specific integration;

direct distribution files;

editable cells;

virtualized large tables;

remote data support;

filters and header filters;

built-in event model.
Tabulator
+2
Tabulator
+2

Hedron should wrap Tabulator rather than expose its API directly:

Python
Run
DataEditor(
    data,
    columns={
        "role": SelectColumn(
            options=["admin", "member"],
        ),
        "active": CheckboxColumn(),
        "salary": NumberColumn(
            minimum=0,
            format="currency",
        ),
    },
)

This allows Hedron to replace or supplement the browser grid later without breaking application code.

AG Grid as an optional backend

AG Grid Community would be a good optional integration for teams that already use it. Its Community edition is MIT-licensed and includes core functionality such as editing, filtering, sorting and pagination. More advanced server-side and enterprise features require its commercial edition.
AG Grid
+3
GitHub
+3
AG Grid
+3

Possible API:

Bash
pip install "hedron-data[ag-grid]"
Python
Run
DataEditor(
    data,
    backend="ag-grid",
)

I would not make AG Grid the default because:

the Community/Enterprise boundary complicates documentation;

users may inadvertently design around paid capabilities;

Hedron’s open-source baseline should remain fully functional.

Avoid Handsontable as the default

Handsontable has perhaps the closest spreadsheet feel, including autofill, editing, shortcuts and formulas, but commercial production use generally requires a paid license.
Handsontable
+1

It could still be an optional adapter:

Bash
pip install hedron-handsontable

but should not shape the core DataEditor API.

Change-set architecture

The browser should not submit the entire dataframe every time. It should maintain a typed change set:

JSON
{
  "version": "users:42",
  "updated": [
    {
      "row_id": 7,
      "column": "role",
      "old_value": "member",
      "new_value": "admin"
    }
  ],
  "inserted": [
    {
      "temporary_id": "new-1",
      "values": {
        "name": "Grace",
        "email": "grace@example.com",
        "role": "member"
      }
    }
  ],
  "deleted": [12]
}

Hedron validates this into:

Python
Run
class CellUpdate(Model):
    row_id: RowId
    column: str
    old_value: JsonValue
    new_value: JsonValue


class DataChanges(Model):
    version: str | None
    updated: list[CellUpdate]
    inserted: list[InsertedRow]
    deleted: list[RowId]

The save endpoint:

Python
Run
@app.data_action("/users/save")
def save_users(
    changes: DataChanges[UserRow],
    service: UserService = Depends(get_user_service),
) -> DataSaveResult[UserRow]:
    return service.apply_changes(changes)
Save strategies

Support three modes.

Explicit save
Python
Run
DataEditor(
    data,
    save="manual",
    on_save=save_users,
)

The user edits several cells and clicks Save changes.

Best default because it is predictable.

Cell commit
Python
Run
DataEditor(
    data,
    save="cell",
    on_change=update_user_cell,
)

Each completed cell edit sends a request.

Useful for small administrative interfaces.

Row commit
Python
Run
DataEditor(
    data,
    save="row",
    on_change=update_user,
)

A full row is saved together. AG Grid supports a comparable full-row editing mode.
AG Grid

Validation behavior

Validation should happen at two levels.

Browser-level

Derived from the Hedron row model:

required fields;

number bounds;

enum options;

date formats;

simple patterns.

Server-level

Always authoritative:

Python
Run
class EmployeeRow(Model):
    employee_id: int = Field(read_only=True)
    name: str = Field(min_length=1)
    salary: Decimal = Field(minimum=0)
    clearance: Literal["None", "Secret", "TS"]

On invalid changes, return structured errors:

JSON
{
  "accepted": false,
  "errors": [
    {
      "row_id": 4,
      "column": "salary",
      "message": "Salary must be zero or greater."
    }
  ]
}

The Web Component marks those cells, preserves unsaved edits and moves focus to the first invalid cell.

Dataframe support

The API should accept:

list[dict];

list[HedronModel];

Pandas;

Polars;

PyArrow;

SQL query-backed resources.

Narwhals would be helpful for normalizing dataframe schemas without forcing conversion to Pandas:

Python
Run
DataEditor(
    polars_df,
    row_key="id",
)

For small data, Hedron can serialize the complete dataset.

For large data:

Python
Run
DataEditor(
    source=user_table_source,
    pagination="server",
)

The grid requests:

GET /_hedron/data/users
    ?offset=0
    &limit=100
    &sort=name:asc
    &filter=active:eq:true

The response:

JSON
{
  "rows": [...],
  "total": 128440,
  "version": "users-2026-08-02T17:20:41Z"
}
A typed data source protocol
Python
Run
class DataEditorSource(Protocol[RowT]):
    row_model: type[RowT]

    async def fetch(
        self,
        query: DataQuery,
    ) -> DataPage[RowT]:
        ...

    async def apply(
        self,
        changes: DataChanges[RowT],
    ) -> DataSaveResult[RowT]:
        ...

Adapters could include:

InMemorySource
PandasSource
PolarsSource
SQLAlchemySource
SQLModelSource
DjangoQuerySetSource

This avoids pretending that a million-row SQL table should first become an in-memory dataframe.

Concurrency and conflict handling

Editable data requires optimistic concurrency.

Every row should optionally carry a version:

Python
Run
class UserRow(Model):
    id: int
    version: int = Field(hidden=True)
    name: str
    role: str

If another user changes the row first:

JSON
{
  "accepted": false,
  "conflicts": [
    {
      "row_id": 42,
      "column": "role",
      "submitted": "admin",
      "current": "member",
      "version": 9
    }
  ]
}

The UI offers:

reload server value;

keep local edit and retry;

compare changes;

cancel.

Hedron must not silently overwrite newer data by default.

Security

The grid must never infer that visible data is editable data.

Developers explicitly define writable fields:

Python
Run
class UserRow(Model):
    id: int = Field(read_only=True)
    name: str
    role: Literal["admin", "member"] = Field(
        writable=True,
    )
    calculated_score: float = Field(read_only=True)

Server-side rules remain authoritative even if a malicious client manually submits changes to a read-only column.

Required protections:

CSRF for save, insert and delete requests;

explicit authorization dependencies;

row- and column-level write validation;

bounded page sizes;

sort/filter field allowlists;

safe JSON serialization;

no arbitrary formatter JavaScript;

redaction of secret fields;

audit logs for mutations;

no public caching for user-specific data.

Column-level permissions
Python
Run
DataEditor(
    source=users,
    permissions={
        "role": require_admin,
        "active": require_manager,
    },
)

The browser can disable unavailable cells, but the server must independently enforce the same policy.

Component API
Minimal
Python
Run
DataEditor(df)
Configured
Python
Run
DataEditor(
    df,
    key="employees",
    row_key="employee_id",
    columns={
        "employee_id": NumberColumn(
            label="ID",
            editable=False,
        ),
        "name": TextColumn(
            required=True,
        ),
        "department": SelectColumn(
            options=departments,
        ),
        "salary": NumberColumn(
            minimum=0,
            format="currency",
        ),
        "active": CheckboxColumn(),
    },
    allow_add=True,
    allow_delete=True,
    on_save=save_employees,
)
Model-driven
Python
Run
class EmployeeRow(Model):
    employee_id: int = Field(
        label="ID",
        read_only=True,
    )

    name: str = Field(
        min_length=1,
    )

    department: Literal[
        "Engineering",
        "Finance",
        "Operations",
    ]

    salary: Decimal = Field(
        minimum=0,
        display="currency",
    )

    active: bool = True
Python
Run
DataEditor(
    employees,
    row_model=EmployeeRow,
    on_save=save_employees,
)
HTMX integration

HTMX should handle the resource-level lifecycle:

loading the editor;

replacing it after a major filter or dataset change;

saving batches;

displaying success/error summaries;

refreshing related components.

The grid Web Component handles cell-level interaction.

After save, the endpoint can return HTMX trigger headers:

http
HX-Trigger: employeesChanged

Other components can react:

Python
Run
EmployeeSummary(
    refresh_on="employeesChanged",
)

This is a clean split:

Web Component
    Cell editing and local state

HTMX
    Server interaction and component refresh

Hedron
    Models, validation, authorization and persistence
Explorer integration

The Explorer should have a dedicated Data tab:

EmployeeEditor

Backend              Tabulator
Source               SQLAlchemySource
Row model            EmployeeRow
Rows loaded           100 of 84,242
Editable columns      name, department, salary, active
Read-only columns     employee_id
Save mode             manual
Pending changes       4
Conflict policy       optimistic

Additional views:

schema;

column configuration;

sample data;

active filters;

pending change set;

validation results;

generated endpoint URLs;

security policy;

render and query timing.

It should allow demo edits against isolated sample data, never the production database by default.

Package layout
hedron-data
├── DataTable
├── DataEditor
├── column models
├── change-set models
├── source protocol
└── dataframe normalization

hedron-data-tabulator
└── default browser grid

hedron-data-aggrid
└── optional AG Grid integration

hedron-data-handsontable
└── separately licensed integration

A simpler initial distribution:

Bash
pip install "hedron[data]"

could install:

hedron-data;

locally bundled Tabulator assets;

Narwhals.

No npm or Node.js installation would be required.

MVP

Build first:

Tabulator-backed Web Component

Pandas, Polars and list[dict] inputs

Model-derived column types

Text, number, Boolean, date and select editors

Read-only columns

Manual batch save

Insert and delete rows

Structured validation errors

Stable row keys

Optimistic concurrency hooks

CSRF and authorization integration

Explorer support

Accessible keyboard editing

CSV download

Defer:

formulas;

merged cells;

Excel formatting parity;

real-time collaborative editing;

pivot tables;

nested tree grids;

arbitrary custom JavaScript editors;

automatic database persistence;

spreadsheet file import/export beyond CSV;

AG Grid Enterprise features.

Recommendation

Make DataEditor a flagship Hedron component.

It directly serves the same audience as Streamlit—Python developers building data tools—but improves on Streamlit’s model by fitting into ordinary FastAPI routing, typed server actions, reusable components, persistent applications, explicit security and scalable server-side data sources.

The positioning could be:

Streamlit-like editable dataframes, built for FastAPI applications rather than rerun-based scripts.

Sources

## 101. You

Add your recommendations to the plan document

## 102. ChatGPT

Worked for 1m 10s

I added the full editable dataframe recommendation to the Hedron plan.

The new DataEditor subsystem includes:

Streamlit-like beginner ergonomics

Tabulator as the recommended default browser grid

Optional AG Grid and Handsontable adapters

Model-driven column inference

Typed change sets instead of resending entire dataframes

Manual, cell, and row save modes

Pandas, Polars, PyArrow, Hedron models, and list[dict] support

Narwhals-based dataframe normalization

Large-data source protocols and server-side pagination

SQLAlchemy, SQLModel, and Django QuerySet source adapters

Optimistic concurrency and conflict resolution

Column-level write permissions

CSRF, authorization, audit, and caching requirements

HTMX-triggered cross-component refreshes

Dedicated Component Explorer data tooling

Packaging, MVP scope, deferred features, and responsibility boundaries

Hedron_Architecture_Plan_v14_DataEditor.docx

Hedron_Architecture_Plan_v14_DataEditor.docx
Document

## 103. You

What else can we learn from streamlit?

## 104. ChatGPT

I think Streamlit is worth studying carefully—not because Hedron should imitate it, but because Streamlit removed a tremendous amount of friction for Python developers.

The key is to copy the reasons people love Streamlit, not its rerun execution model.

1. Dataframe-first philosophy ⭐⭐⭐⭐⭐

This is probably Streamlit's biggest insight.

Almost every object "just works."

Python
Run
st.dataframe(df)

st.line_chart(df)

st.bar_chart(df)

st.map(df)

Hedron should adopt this philosophy.

Python
Run
DataTable(df)

LineChart(df)

BarChart(df)

Map(df)

The user shouldn't need adapters or serializers.

Thanks to Narwhals, this could work with:

Pandas

Polars

Arrow

list[dict]

SQLAlchemy results

without caring which backend they have.

2. "Magic" object rendering ⭐⭐⭐⭐⭐

Streamlit can display almost anything.

Python
Run
st.write(obj)

It detects:

dataframe

markdown

matplotlib

plotly

altair

PIL image

dict

list

Hedron needs something similar.

Python
Run
Auto(obj)

or maybe

Python
Run
Render(obj)

Internally:

if dataframe:
    DataTable

elif plotly:
    PlotlyChart

elif markdown:
    Markdown

elif PIL:
    Image

elif Hedron component:
    render

...

This makes exploratory development much faster.

3. Automatic forms

Streamlit is fantastic here.

Python
Run
st.text_input()

st.selectbox()

st.checkbox()

Hedron can go much further because it has typed models.

Python
Run
AutoForm(User)

Already discussed.

Huge feature.

4. Session state ⭐⭐⭐⭐☆

This is where I would not copy Streamlit.

Streamlit's state exists because the entire script reruns.

Hedron already has:

FastAPI sessions

cookies

server state

HTMX

Instead I'd provide:

Python
Run
SessionState

that simply wraps FastAPI's session mechanisms.

5. Caching ⭐⭐⭐⭐⭐

This one I absolutely would copy.

Imagine:

Python
Run
@cache_data
def load_users():
    ...

or

Python
Run
@cache_component
class UserTable:
    ...

The Explorer could even show cache hits.

6. Download buttons ⭐⭐⭐⭐☆

People love:

Python
Run
st.download_button(...)

Hedron:

Python
Run
DownloadButton(
    data=df,
    filename="users.csv"
)

Automatically.

7. File uploader ⭐⭐⭐⭐⭐

Should be first-class.

Python
Run
FileUpload(
    accept=["csv"]
)

Combined with

Python
Run
AutoTable()

This becomes really compelling.

8. Metrics
Python
Run
Metric(
    label="Revenue",
    value="$1.2M",
    delta="+12%"
)

Simple.

Useful.

9. Expanders
Python
Run
Expander(
    "Advanced Settings"
)

Very nice API.

10. Tabs

Straightforward.

11. Sidebar

React users usually build sidebars.

Streamlit made it automatic.

Hedron could have

Python
Run
Sidebar(
    ...
)
12. Columns

Streamlit:

Python
Run
col1, col2 = st.columns(2)

I actually wouldn't copy this.

I prefer explicit layout.

Python
Run
Grid(
    columns=2,
    children=[...]
)
13. Progress

Very useful.

14. Toasts

Simple.

15. Status

Loading

Success

Warning

Error

16. Code viewer

Excellent.

17. JSON viewer

Also excellent.

What I think Streamlit gets wrong

This is actually more important.

Script reruns

No.

FastAPI is much better.

Global state

No.

Component state should stay local.

Widgets everywhere

Everything is:

Python
Run
st.text_input()

st.checkbox()

st.button()

Hedron should embrace composition instead.

Layout

Sometimes feels hacked together.

Hedron should use components.

Navigation

Weak.

FastAPI routing is much better.

Biggest missed opportunity

This one excites me.

Streamlit has

Python
Run
st.dataframe(df)

Imagine Hedron

Python
Run
Auto(df)

returns

DataFrame

↓

DataEditor

Automatically.

Or

Python
Run
Auto(plotly)

↓

PlotlyChart

Really interesting idea

Imagine

Python
Run
Inspector(df)

Explorer could understand

schema

nulls

distributions

charts

Automatically.

AI integration

Since Hedron already has Explorer.

Imagine

Why is this component slow?

↓

AI examines

component tree

queries

render times

HTMX


Very cool.

Streamlit's biggest lesson

I think this is the one sentence I'd put into the Hedron philosophy.

Users should almost never have to decide which component to use for common Python objects.

That's a much bigger idea than it sounds.

Because it means:

Python
Run
Page(
    users
)

works.

If

Python
Run
users

is

DataFrame

↓

DataTable

Plotly

↓

PlotlyChart

Markdown

↓

Markdown

PIL

↓

Image

Component

↓

Render

list[str]

↓

List

dict

↓

DescriptionList

The developer spends less time learning Hedron and more time building.

One feature I think Hedron should surpass Streamlit on

This is where I think Hedron can become genuinely unique.

Intelligent rendering
Python
Run
Auto(df)

doesn't just create a table.

Explorer inspects:

row count

column types

cardinality

geospatial columns

datetime columns

Maybe

10 rows

↓

DataEditor
5 million rows

↓

Virtualized DataEditor
lat/lon

↓

Interactive map
timeseries

↓

LineChart suggestion
categorical

↓

BarChart suggestion

This could be powered by the same inspection engine you already envisioned for the Component Explorer.

I actually think this deserves its own subsystem in the architecture: a Data Intelligence Layer.

Instead of simply rendering Python objects, Hedron would understand them well enough to recommend or automatically choose appropriate components while always letting the developer override the decision. That feels very much in line with Hedron's broader philosophy of reducing boilerplate without taking away control.

## 105. You

Add all the recommended streamlit features to the hedron plan document

## 106. ChatGPT

I incorporated the Streamlit-inspired recommendations into the Hedron architecture plan as a new major section focused on developer productivity, while keeping them aligned with Hedron's server-first philosophy rather than Streamlit's rerun model.

The additions include:

Automatic object rendering

Auto() / intelligent rendering of common Python objects

Automatic rendering for:

Pandas

Polars

PyArrow

list[dict]

Plotly

Altair

Matplotlib

Markdown

PIL Images

Hedron components

Extensible renderer registry for third-party integrations

Streamlit-inspired core components

DataEditor

DataTable

Metric

FileUpload

DownloadButton

JSONViewer

CodeViewer

Progress

Status

Toast

Expander

Tabs

Sidebar

Smart defaults

Automatic dataframe inspection

Automatic chart suggestions

Automatic map detection for latitude/longitude data

Virtualized tables for large datasets

Sensible component selection with explicit override support

Caching

@cache_data

@cache_component

Future cache inspection in the Component Explorer

Data Intelligence Layer (new subsystem)

A new subsystem that analyzes Python objects and recommends or automatically selects the best Hedron component.

Examples:

Small dataframe → DataEditor

Huge dataframe → Virtualized DataEditor

Time-series → Line chart suggestion

Geographic data → Map component

Mostly categorical → Bar chart suggestion

Design philosophy

A new principle has been added:

Developers should almost never have to decide which Hedron component to use for common Python objects. Hedron should provide intelligent defaults while always allowing explicit control.

What Hedron intentionally does not adopt from Streamlit

The plan also explicitly rejects:

Script rerun execution

Global mutable application state

Widget-centric programming

Implicit layout model

Instead, it reinforces:

FastAPI routing

Component composition

Explicit server state

HTMX-driven interactions

Addressable components

This makes Hedron feel as approachable as Streamlit for data applications while remaining a true web framework built on FastAPI rather than a rerun-based scripting environment.

## 107. You

Explore how we can better leverage the built in async functionality of fastapi with hedron

## 108. ChatGPT

FastAPI’s async support could become much more than “Hedron accepts async def endpoints.” Hedron can turn asynchronous I/O into a component-level capability while keeping the beginner API simple.

The guiding principle should be:

Hedron automatically awaits declared asynchronous work, but concurrency, streaming, and background execution remain explicit where their behavior affects correctness.

FastAPI already supports asynchronous path operations, dependencies, lifespan resources, streaming responses, WebSockets, and post-response background tasks. Hedron should build directly on those mechanisms rather than creating a parallel async runtime.
FastAPI
+5
FastAPI
+5
FastAPI
+5

1. Components should support async factories

The most natural starting point is allowing component-producing endpoints and factories to be asynchronous.

Python
Run
@app.page("/users/{user_id}")
async def user_page(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserPage:
    user = await service.get(user_id)
    activity = await service.get_recent_activity(user_id)

    return UserPage(
        user=user,
        activity=activity,
    )

This already fits FastAPI’s normal programming model: when a library exposes awaitable operations, the path operation should use async def and await them.
FastAPI

Addressable components should work the same way:

Python
Run
@addressable
async def UserTable(
    team_id: int,
    service: UserService = Depends(get_user_service),
) -> UserTableComponent:
    users = await service.list_team_users(team_id)
    return UserTableComponent(rows=users)

Hedron should not expose a separate concept like AsyncComponent. A component’s factory may be synchronous or asynchronous; the resulting component remains the same type.

2. Allow asynchronous component rendering—but cautiously

Most component rendering should remain synchronous because transforming an existing component tree into HTML is CPU-local and predictable.

However, advanced components may need async preparation:

Python
Run
class ReportPanel(Component):
    async def prepare(
        self,
        context: RenderContext,
    ) -> PreparedComponent:
        report = await context.reports.load(self.props.report_id)

        return PreparedComponent(
            props=self.props,
            state={"report": report},
        )

    def render(
        self,
        prepared: PreparedComponent,
    ) -> Node:
        return ReportView(report=prepared.state["report"])

This separation is better than placing arbitrary await calls inside the HTML renderer:

prepare()   → async I/O
render()    → deterministic component tree generation
serialize() → deterministic HTML generation

Benefits:

easier profiling;

predictable rendering;

simpler caching;

clearer cancellation;

fewer hidden database calls during template traversal.

For the MVP, I would support async endpoint factories and async data sources first. Async component lifecycle hooks can come later.

3. Parallel component data loading

A dashboard often contains independent sections:

Dashboard
├── RevenueSummary
├── OpenIncidents
├── UserActivity
└── DeploymentStatus

Loading them sequentially wastes time when each performs independent I/O.

Python
Run
@app.page("/dashboard")
async def dashboard(
    revenue: RevenueService = Depends(get_revenue_service),
    incidents: IncidentService = Depends(get_incident_service),
    activity: ActivityService = Depends(get_activity_service),
) -> Dashboard:
    async with asyncio.TaskGroup() as tasks:
        revenue_task = tasks.create_task(revenue.summary())
        incidents_task = tasks.create_task(incidents.open_items())
        activity_task = tasks.create_task(activity.recent())

    return Dashboard(
        revenue=revenue_task.result(),
        incidents=incidents_task.result(),
        activity=activity_task.result(),
    )

asyncio.TaskGroup gives structured concurrency: tasks are scoped to the block, awaited as a group, and coordinated when one fails. Python’s documentation recommends structured concurrency tools such as TaskGroup, with cancellation behavior treated carefully.
Python documentation
+2
Python documentation
+2

Hedron could provide a small ergonomic helper:

Python
Run
results = await hedron.gather(
    revenue=revenue.summary(),
    incidents=incidents.open_items(),
    activity=activity.recent(),
)
Python
Run
return Dashboard(
    revenue=results.revenue,
    incidents=results.incidents,
    activity=results.activity,
)

Internally it should use structured concurrency rather than unmanaged asyncio.create_task() calls.

Declarative parallel loaders

A higher-level future API could be:

Python
Run
class Dashboard(Page):
    revenue = AsyncValue(load_revenue)
    incidents = AsyncValue(load_incidents)
    activity = AsyncValue(load_activity)

But I would not begin there. It risks obscuring where I/O occurs. Explicit endpoint-level concurrency is easier to understand and debug.

4. Async dependencies remain first-class

Hedron should preserve FastAPI’s dependency model exactly:

Python
Run
async def get_database() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session
Python
Run
@addressable
async def UserTable(
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(require_user),
) -> UserTableComponent:
    ...

FastAPI dependencies may be synchronous or asynchronous, and yield dependencies support setup and cleanup around request processing.
FastAPI
+1

Hedron must ensure cleanup does not happen before:

an ordinary component response has rendered;

a streaming component response has completed;

an async iterator backing a stream has closed.

This is especially important for database sessions and streamed query results.

5. Async data protocols throughout Hedron

Every data-facing Hedron protocol should support asynchronous implementations.

DataEditor
Python
Run
class AsyncDataEditorSource(Protocol[RowT]):
    row_model: type[RowT]

    async def fetch(
        self,
        query: DataQuery,
    ) -> DataPage[RowT]:
        ...

    async def apply(
        self,
        changes: DataChanges[RowT],
    ) -> DataSaveResult[RowT]:
        ...
Chart source
Python
Run
class AsyncVisualizationSource(Protocol):
    async def load(
        self,
        query: VisualizationQuery,
    ) -> VisualizationData:
        ...
Selection options
Python
Run
Select(
    options=AsyncOptions(load_departments),
)
File download
Python
Run
DownloadButton(
    source=AsyncDownload(generate_report),
)
Auto-render integration
Python
Run
Auto(await service.load_dataframe())

Hedron should avoid naming everything with an Async prefix in user-facing APIs where runtime inspection can safely await the declared source.

For example:

Python
Run
DataEditor(source=users_source)

may accept either:

Python
Run
def fetch(...) -> DataPage:

or:

Python
Run
async def fetch(...) -> DataPage:

The adapter handles both.

6. Async lazy components

Addressable components map naturally to deferred asynchronous loading.

Python
Run
RevenueChart(
    lazy=True,
    period="12m",
)

Initial page:

HTML
<section
    hx-get="/_hedron/components/revenue-chart?period=12m"
    hx-trigger="load"
    hx-swap="outerHTML"
    aria-busy="true">
    ...
</section>

The component resource may perform async database or service calls independently of the initial page response.

This gives Hedron a server-native equivalent of deferred component loading:

Initial page renders quickly
        ↓
Browser requests lazy component
        ↓
Async FastAPI component endpoint loads data
        ↓
HTMX swaps in final HTML

Hedron can offer:

Python
Run
RevenueChart(
    lazy=True,
    fallback=RevenueSkeleton(),
)

This is probably more valuable than trying to stream every page from the beginning.

7. Async component groups

For common dashboard layouts:

Python
Run
AsyncRegion(
    RevenueSummary(),
    OpenIncidents(),
    DeploymentStatus(),
    strategy="independent",
)

Could render independent lazy component resources immediately.

Possible strategies:

together

Await all component loaders and render the complete region.

Python
Run
AsyncRegion(
    ...,
    strategy="together",
)
independent

Render placeholders and let each addressable component load separately.

Python
Run
AsyncRegion(
    ...,
    strategy="independent",
)
ordered

Load and reveal components in declared priority order.

Python
Run
AsyncRegion(
    primary,
    secondary,
    tertiary,
    strategy="ordered",
)

For the MVP, independent can be implemented using ordinary HTMX lazy loading rather than inventing a complicated streaming protocol.

8. Streaming HTML responses

Hedron could eventually stream page output as sections become ready:

Python
Run
@app.page("/report", streaming=True)
async def report() -> StreamingPage:
    return StreamingPage(
        Header(...),
        await Summary(...),
        async_section(load_large_table),
    )

FastAPI supports StreamingResponse, including async generators. FastAPI’s documentation also emphasizes that cancellation can only be observed at an await, so long or infinite streams must yield control and respond correctly to cancellation.
FastAPI

A possible implementation:

Python
Run
async def stream_page(
    page: Page,
) -> AsyncIterator[bytes]:
    yield render_document_start(page).encode()

    async for chunk in page.iter_chunks():
        yield chunk.encode()
        await anyio.sleep(0)

    yield render_document_end(page).encode()

However, full streamed HTML introduces difficult concerns:

layouts must remain structurally valid;

styles and scripts must be available before streamed components;

errors may occur after headers are sent;

dependencies must remain open;

client disconnects must cancel pending work;

HTMX may be a simpler fit for deferred regions.

My recommendation:

Use lazy addressable components as Hedron’s default asynchronous UI model. Add streamed documents only after real applications show a need.

9. Async iterables and incremental lists

A more focused streaming capability may be valuable for large result sets.

Python
Run
async def stream_logs() -> AsyncIterator[LogRow]:
    async for row in repository.follow_logs():
        yield row
Python
Run
LiveList(
    source=stream_logs(),
)

Potential transports:

chunked HTML;

Server-Sent Events;

WebSockets.

For one-way updates such as logs, progress, notifications, and job status, Server-Sent Events are usually conceptually simpler than bidirectional sockets. For interactive collaborative features, WebSockets are more appropriate.

FastAPI provides WebSocket endpoints and allows dependencies within them.
FastAPI

A future API could be:

Python
Run
LiveRegion(
    source=job_progress(job_id),
    transport="sse",
)
Python
Run
CollaborativeEditor(
    channel=project_channel(project_id),
    transport="websocket",
)

These should be later packages, not MVP core behavior.

10. Component actions can be async automatically
Python
Run
@app.action("/users/{user_id}", method="delete")
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserTable:
    await service.delete(user_id)
    users = await service.list_users()

    return UserTable(rows=users)

The action returns a Hedron component after asynchronous work. Hedron handles:

awaiting the action;

validation;

CSRF;

component rendering;

HTMX response headers;

refresh triggers;

cancellation.

Nothing about the component API needs to change.

11. Background tasks after component responses

Some work does not need to delay the UI response:

Python
Run
@app.action("/users")
async def create_user(
    form: CreateUser,
    background: BackgroundTasks,
) -> UserTable:
    user = await service.create(form)

    background.add_task(
        send_welcome_email,
        user.id,
    )

    return UserTable(rows=await service.list_users())

FastAPI’s BackgroundTasks runs tasks after the response has been sent and is intended for work the client does not need to wait for.
FastAPI
+1

Hedron could make this more component-friendly:

Python
Run
return UserTable(rows=users).after_response(
    send_welcome_email,
    user.id,
)

But this should compile into FastAPI/Starlette background tasks rather than create its own executor.

Important boundary:

small post-response tasks: FastAPI BackgroundTasks;

durable, retryable, distributed, or heavy jobs: external task queue;

CPU-intensive work: process worker or external service.

Hedron should not pretend in-process background tasks are a reliable job system.

12. Job components

For longer operations, Hedron can make asynchronous jobs easy without owning the queue implementation.

Python
Run
@app.action("/reports/build")
async def build_report(
    request: ReportRequest,
    jobs: JobService = Depends(get_job_service),
) -> JobStatus:
    job = await jobs.enqueue("build-report", request)

    return JobStatus(
        job_id=job.id,
        poll="2s",
    )

JobStatus becomes an addressable polling component:

HTML
<section
    hx-get="/jobs/abc123/status"
    hx-trigger="every 2s"
    hx-swap="outerHTML">
</section>

When complete, it returns:

Python
Run
ReportReady(
    download=report_url,
)

This fits Hedron and HTMX better than holding an HTTP request open for minutes.

Official integrations could later include:

Celery;

Dramatiq;

ARQ;

Taskiq;

cloud queues.

The core only needs a JobBackend protocol.

13. Request cancellation and client disconnects

This is critical for async component resources.

If a user navigates away or HTMX cancels a request, Hedron should allow the request task and its child tasks to be cancelled. Python’s structured-concurrency and timeout tools rely on cancellation, and swallowing CancelledError can break their behavior.
Python documentation
+2
Python documentation
+2

Rules:

Do not swallow asyncio.CancelledError.

Use try/finally for resource cleanup.

Cancel parallel child loaders when the owning request is cancelled.

Do not leave orphan tasks running after component requests end.

Ensure streaming generators reach an await.

Do not shield normal component work from cancellation.

Bad:

Python
Run
try:
    return await load_report()
except BaseException:
    return ErrorPanel()

This may consume cancellation.

Better:

Python
Run
try:
    return await load_report()
except asyncio.CancelledError:
    raise
except ReportError as exc:
    return ReportErrorPanel(error=exc)

The Explorer should detect unusually long work that continued after request cancellation where observable.

14. Timeouts

Addressable components should support timeout policies:

Python
Run
@addressable(
    timeout=3.0,
)
async def ExternalStatus(...) -> StatusPanel:
    ...

Or component-level fallback:

Python
Run
ExternalStatus(
    timeout=3,
    timeout_fallback=StatusUnavailable(),
)

Internally, Hedron could use asyncio.timeout() or the corresponding AnyIO cancellation scope, depending on its compatibility layer. Python’s timeout context cancels overdue work and translates the cancellation into a timeout failure at the boundary.
Python documentation
+1

Timeout behavior must be explicit:

timeout="error"      → standard error response
timeout="fallback"   → render fallback component
timeout="stale"      → use cached value if available
timeout="partial"    → render page without failed region

Recommended default for a normal endpoint: fail the request.

Recommended default for an independent lazy component: render a retryable error component.

15. Async cache integration

Async data loaders need cache stampede protection.

Python
Run
@cache_data(ttl=60)
async def load_summary(team_id: int) -> Summary:
    ...

If 100 requests arrive simultaneously for the same uncached key, Hedron should not execute the loader 100 times. It should support single-flight behavior:

First request starts load
Other requests await same in-flight task
Result cached once
All waiters receive result

But cache cancellation must be handled carefully:

one disconnected waiter should not necessarily cancel shared work;

complete request cancellation should not poison the cache;

failed loads should not be cached unless configured;

authenticated data must include security context in cache keys.

This is a later feature but an important design constraint.

16. Async lifespan resources

Hedron should use FastAPI’s recommended lifespan mechanism for long-lived async resources such as:

database pools;

HTTP clients;

Redis pools;

chart-data services;

job backends;

component registries that require async initialization.

FastAPI recommends the application lifespan async context manager for startup and shutdown behavior.
FastAPI

Python
Run
@asynccontextmanager
async def lifespan(app: Hedron):
    app.state.http = httpx.AsyncClient()
    app.state.jobs = await create_job_backend()

    yield

    await app.state.http.aclose()
    await app.state.jobs.close()


app = Hedron(
    lifespan=lifespan,
)

Hedron should compose its own internal lifespan behavior with the application’s supplied lifespan rather than forcing users to choose between them.

Internal startup may include:

component discovery;

async plugin initialization;

Explorer registry loading;

cache client setup;

asset manifest validation.

17. Async plugin lifecycle

Official integrations should support:

Python
Run
class HedronPlugin:
    async def startup(
        self,
        app: Hedron,
    ) -> None:
        ...

    async def shutdown(
        self,
        app: Hedron,
    ) -> None:
        ...

This matters for:

database adapters;

Redis caching;

chart backends;

authentication providers;

Explorer panels;

job systems.

Hedron’s plugin manager should start plugins in dependency order and shut them down in reverse order.

18. Sync compatibility

Hedron must remain pleasant for users with synchronous code.

FastAPI supports both def and async def path operations. Hedron should preserve that behavior instead of telling every user to write async code.
FastAPI

Python
Run
@app.page("/")
def home() -> HomePage:
    return HomePage(...)

should remain completely valid.

Important rule:

Hedron should never call blocking synchronous I/O directly on the event loop merely because a component endpoint is async.

Framework adapters should preserve FastAPI’s sync/async execution behavior. Explicit helpers can exist for unavoidable blocking calls:

Python
Run
result = await hedron.run_sync(
    legacy_client.load_report,
    report_id,
)

But this should not be encouraged for CPU-heavy processing.

19. Async rendering diagnostics in the Explorer

The Explorer should make asynchronous behavior visible.

For a dashboard render:

Dashboard request                         214 ms
├── FastAPI dependencies                   18 ms
├── Revenue loader                        106 ms
├── Incident loader                        71 ms
├── Activity loader                        93 ms
├── Component rendering                     4 ms
└── HTML serialization                      2 ms

Concurrent loader wall time               106 ms
Sequential equivalent                     270 ms

For every loader:

sync or async;

start and end time;

timeout;

cancelled or completed;

dependency source;

cache hit or miss;

bytes or rows loaded;

blocking-event-loop warning.

Security-sensitive values must remain redacted.

Async warnings
HEDRON5201
Async component loader executed a blocking database operation for 842 ms.

Component:
    RevenueChart

Suggestion:
    Use an async database driver or move the call into run_sync().
HEDRON5204
Detached task was created during UserTable rendering and outlived the request.

Use a TaskGroup, BackgroundTasks, or a durable job backend.
20. Async testing

Hedron’s testing package should support FastAPI’s async testing patterns:

Python
Run
@pytest.mark.anyio
async def test_user_table(
    async_client,
):
    response = await async_client.get(
        "/_hedron/components/user-table"
    )

    assert response.status_code == 200

FastAPI documents using async tests when the application and database interactions are asynchronous.
FastAPI

Hedron should add helpers for:

async component factories;

timeout behavior;

cancellation cleanup;

concurrent loaders;

async source protocols;

background task registration;

WebSocket and SSE components;

cache single-flight behavior.

Recommended API surface
Endpoint
Python
Run
@app.page("/dashboard")
async def dashboard() -> Dashboard:
    ...
Addressable component
Python
Run
@addressable
async def RevenueChart(...) -> Chart:
    ...
Typed action
Python
Run
@app.action("/users", method="post")
async def create_user(...) -> UserTable:
    ...
Data source
Python
Run
class UsersSource(DataEditorSource[UserRow]):
    async def fetch(...):
        ...

    async def apply(...):
        ...
Lazy component
Python
Run
RevenueChart(
    lazy=True,
    fallback=RevenueSkeleton(),
)
Parallel work
Python
Run
data = await hedron.gather(
    users=load_users(),
    metrics=load_metrics(),
)
Timeout
Python
Run
ExternalStatus(
    timeout=3,
    timeout_fallback=Unavailable(),
)
Post-response task
Python
Run
return SuccessPanel().after_response(
    send_notification,
    user_id,
)
What to include in the MVP

Build early:

Full support for sync and async component-returning endpoints.

Async addressable component factories.

Async typed actions.

Async FastAPI dependencies and yield cleanup.

Async DataEditorSource and visualization source protocols.

Lazy components through HTMX.

Cancellation-safe request handling.

Component timeouts and retryable fallback components.

Lifespan integration for Hedron plugins and resources.

Async testing helpers.

Explorer timing traces for async component endpoints.

Add shortly afterward:

Structured hedron.gather().

Async cache and single-flight support.

Job backend protocol and polling components.

Background-task helpers.

Defer:

general-purpose streamed document rendering;

server-managed async state graphs;

automatic concurrency inferred from the component tree;

WebSocket component framework;

SSE live-region framework;

distributed task implementation;

arbitrary async calls inside HDN expressions.

Strongest design choice

Hedron should not automatically inspect a component tree and execute every async child concurrently. That sounds attractive but creates hidden database activity, ordering problems, authorization ambiguity, unpredictable load, and difficult cancellation behavior.

Concurrency should arise from one of three explicit mechanisms:

The endpoint uses structured concurrency.

A component is independently addressable and lazy-loaded.

A declared AsyncRegion says that its children may load independently.

That keeps the system intuitive.

Updated Hedron principle

Hedron embraces asynchronous I/O at component boundaries: endpoints, actions, data sources, dependencies, and addressable resources may be async. Rendering remains deterministic, concurrency remains structured, long work becomes jobs, and client cancellation propagates through all request-owned work.

This could become a major advantage over Streamlit-style rerun applications: Hedron can offer similarly simple data components while retaining FastAPI’s mature asynchronous request model, dependency lifecycle, streaming options, and concurrent I/O capabilities.

Sources

## 109. You

Add all the recommended features to the plan document

## 110. ChatGPT

Worked for 1m 40s

I added the full async-first FastAPI strategy to the Hedron architecture plan, including:

Sync and async component-returning endpoints

Async addressable components and typed actions

Structured parallel loading with hedron.gather()

Async dependencies and lifespan resources

Async DataEditorSource and visualization protocols

Lazy HTMX components and async regions

Timeouts, cancellation, and client disconnect handling

Background tasks and durable job backends

Streaming, SSE, and WebSocket roadmap

Async caching and single-flight behavior

Blocking-I/O safeguards and hedron.run_sync()

Explorer async traces and diagnostics

Async security requirements

Async testing support

MVP, roadmap, and acceptance criteria

The updated 23-page document was rendered and visually verified.

Hedron_Architecture_Plan_v15_Async_First.docx

Hedron_Architecture_Plan_v15_Async_First.docx
Document

## 111. You

Research the current fastapi docs to make sure we are fully utilizing its features with hedron

## 112. ChatGPT

After reviewing the current FastAPI documentation, I actually think we can push Hedron much further than we've planned. There are several FastAPI capabilities that map almost perfectly onto Hedron's architecture.

1. Build Hedron around a custom APIRoute ⭐⭐⭐⭐⭐

This is probably the biggest architectural improvement.

FastAPI already lets you provide a custom APIRoute class that controls request handling, dependency resolution, response serialization, and OpenAPI generation for a route.
FastAPI
+1

Instead of:

Python
Run
class Hedron(FastAPI):
    ...

I would build around:

Python
Run
class HedronRoute(APIRoute):
    ...

Then:

Python
Run
app = Hedron()

router = HedronRouter(
    route_class=HedronRoute
)

Now Hedron controls:

Component return detection

HTML rendering

OpenAPI extensions

HTMX handling

Component diagnostics

Render timing

Explorer metadata

without modifying FastAPI itself.

This is a much cleaner architecture.

2. Build everything around routers ⭐⭐⭐⭐⭐

Instead of

Python
Run
app.components(...)

I think we should embrace routers.

Imagine:

Python
Run
users = HedronRouter(
    prefix="/users"
)
Python
Run
@users.page("/")
def users():
    ...

Now:

Python
Run
app.include_router(users)

This automatically gives:

tags

dependencies

authorization

prefixes

OpenAPI grouping

Explorer grouping

Exactly like FastAPI intends.
FastAPI

3. Component routers ⭐⭐⭐⭐⭐

This one excites me.

Imagine:

Python
Run
UserComponents/

    router.py

    UserCard.py

    UserTable.py

Then

Python
Run
app.include_component_router(
    UserComponents
)

Every addressable component becomes:

/_hedron/components/users/...

Almost no configuration.

4. Lifespan ⭐⭐⭐⭐⭐

FastAPI has largely moved away from startup/shutdown events in favor of lifespan context managers.
FastAPI
+1

Hedron should lean heavily into this.

During startup:

component discovery

HDN compilation

CSS compilation

Explorer registry

chart registration

plugin loading

route generation

theme loading

All happens inside lifespan.

5. Mount sub-applications ⭐⭐⭐⭐☆

FastAPI supports mounting sub-applications.
FastAPI

Imagine:

Python
Run
admin = Hedron()

docs = Hedron()

analytics = Hedron()

root.mount("/admin", admin)

Each Hedron app has:

own Explorer

own themes

own component registry

own layouts

Really nice.

6. Response classes ⭐⭐⭐⭐⭐

We already discussed

Python
Run
HTML(...)

But I think we should have multiple response classes.

Python
Run
ComponentResponse

StreamingComponentResponse

FileComponentResponse

FragmentResponse

PageResponse

Each maps naturally to FastAPI's response system.

7. Custom docs ⭐⭐⭐⭐⭐

FastAPI allows replacing Swagger UI.
FastAPI

This means

/docs

could become

Hedron Docs

with tabs.

API

Components

Pages

Actions

Explorer

Rather than inventing another URL.

Huge.

8. OpenAPI Callbacks ⭐⭐⭐⭐☆

This one is really interesting.

FastAPI supports OpenAPI callbacks.
FastAPI

Imagine HTMX Actions automatically documenting callback behavior.

Probably not MVP.

But worth noting.

9. OpenAPI Webhooks ⭐⭐⭐⭐☆

Also interesting.

Imagine

Python
Run
WebhookPanel(...)

Automatically documenting webhook payloads.

10. Generate SDKs ⭐⭐⭐⭐☆

FastAPI can generate client SDKs from OpenAPI.
FastAPI

Imagine

hedron generate react-sdk

for component endpoints.

Probably future.

11. Middleware ⭐⭐⭐⭐⭐

I think Hedron should ship middleware.

Examples

RenderTimingMiddleware

ExplorerMiddleware

ThemeMiddleware

HTMXMiddleware

ComponentIdentityMiddleware

SecurityHeadersMiddleware

Instead of putting everything in routes.

Middleware already sits at exactly the right layer for cross-cutting request/response concerns.
FastAPI

12. Strict content type ⭐⭐⭐⭐⭐

I found something interesting.

Recent FastAPI versions expose

strict_content_type

on APIRouter.
FastAPI
+1

Hedron should enable this.

It helps reject invalid requests earlier.

13. generate_unique_id_function ⭐⭐⭐⭐⭐

This one is fantastic.

FastAPI lets you customize OpenAPI operation IDs.
FastAPI

Instead of

read_users_users_get

Hedron could generate

component_UserTable

page_UsersPage

action_DeleteUser

Explorer instantly benefits.

14. APIRouter dependencies ⭐⭐⭐⭐⭐

I think every component router should support:

Python
Run
users = HedronRouter(

    dependencies=[

        Depends(require_user)

    ]

)

Every addressable component automatically inherits.

Very clean.

15. include_in_schema ⭐⭐⭐⭐⭐

Perfect.

Internal component routes

include_in_schema=False

Explorer still shows them.

Swagger doesn't.

Exactly what we wanted.
FastAPI

16. Metadata/docs URLs ⭐⭐⭐⭐☆

Hedron should expose

/docs

→ API
/explorer

→ Components

Or maybe

/docs

API

Components

Explorer

Integrated.

17. BackgroundTasks ⭐⭐⭐⭐⭐

I actually think we should keep using FastAPI's

BackgroundTasks

for lightweight work.

Only abstract it slightly.

Don't invent another task system.

For durable work, define a pluggable job backend instead. FastAPI's built-in background tasks are intentionally lightweight and execute after the response; they are not a durable queue.
FastAPI
+2
Reddit
+2

18. StaticFiles ⭐⭐⭐⭐⭐

FastAPI already has

StaticFiles

Hedron should use it for:

compiled CSS

JS

images

themes

Explorer assets

Don't reinvent asset serving.
FastAPI

19. Dependency Overrides ⭐⭐⭐⭐⭐

Testing.

Explorer.

Examples.

Huge.

Python
Run
ExplorerExample(

    overrides={

        UserService:

            FakeUserService()

    }

)

FastAPI already has dependency overrides.

Use them.

20. Separate Input/Output schemas ⭐⭐⭐⭐☆

FastAPI supports separate input and output schema considerations.
FastAPI

That fits beautifully with Hedron.

FormModel

↓

Input

↓

Component

↓

Output
Biggest architectural realization

I actually think we've been slightly wrong about Hedron.

Instead of saying

Hedron extends FastAPI.

I think the better statement is

Hedron is a specialized collection of FastAPI routers, routes, response classes, middleware, documentation extensions, and developer tooling.

That changes everything.

Rather than competing with FastAPI...

We embrace every extension point FastAPI intentionally provides.

New architectural principle

I would actually add this to the very beginning of the architecture document:

Hedron should prefer extending FastAPI through its documented extension points—custom APIRoute classes, APIRouter, response classes, lifespan, middleware, dependency injection, OpenAPI customization, and documentation hooks—rather than replacing or bypassing FastAPI's architecture.

I think this is a major improvement to the design. It means Hedron stays aligned with FastAPI as it evolves, minimizes maintenance burden, and feels familiar to existing FastAPI developers instead of introducing parallel abstractions.

Sources

## 113. You

Rewrite the plan with all these

## 114. ChatGPT

I rewrote the architecture plan around what I now think is the correct long-term architectural direction:

Hedron is built on top of FastAPI's extension mechanisms—not beside them.

The new revision incorporates:

Core architectural shift

Custom APIRoute (HedronRoute) as the heart of request processing

HedronRouter as the primary organizational abstraction

Component routers with automatic discovery

Hedron response classes instead of custom rendering pipelines

Lifespan-driven startup for component discovery, HDN compilation, scoped CSS compilation, plugin loading, and Explorer initialization

FastAPI-native integrations

Middleware for:

HTMX

Themes

Render timing

Security headers

Component identity

Explorer

Continued use of:

Dependency Injection

BackgroundTasks

StaticFiles

Dependency overrides

OpenAPI customization

Operation ID generation

include_in_schema=False for internal component resources

Existing Hedron concepts retained

Addressable Components

Component Explorer

Scoped Styles

HDN

DataEditor

Visualization subsystem

Security-first architecture

Async-first architecture

Progressive disclosure

FastAPI-first packaging with hedron, hedron-core, hedron-flask, and hedron-django

Updated philosophy

The document now explicitly states:

Hedron should prefer extending FastAPI through its documented extension points—custom APIRoute classes, APIRouter, response classes, lifespan, middleware, dependency injection, OpenAPI customization, StaticFiles, and documentation hooks—rather than replacing or bypassing FastAPI's architecture.

I think this is a significant improvement over our earlier plans because it makes Hedron feel like a natural evolution of FastAPI rather than a competing application framework.

You can download it here:

📄
Hedron_Architecture_Plan_v16_FastAPI_Extensions.docx

One recommendation before writing much code: I'd freeze the architecture for a bit and spend time implementing a vertical slice—perhaps a small CRUD application with authentication, a DataEditor, a Plotly chart, an addressable component, and the Component Explorer. That kind of end-to-end prototype is likely to reveal API rough edges much earlier than continuing to expand the design document, while still validating the architectural decisions we've made.

Hedron_Architecture_Plan_v16_FastAPI_Extensions.docx
Document

## 115. You

Let’s create all the plan documents we need before we start coding.

## 116. ChatGPT

I actually think this is the right move.

You've done this successfully before with OntoCode: by the time implementation started, the architecture had already answered most of the hard questions.

For Hedron, I would go even further and treat it like a language/framework specification rather than a normal open-source project.

The architecture has now grown into several distinct systems:

Component model

HDN language

FastAPI integration

Component Explorer

Scoped Styles

DataEditor

Visualization

Security

Async

Plugin system

Trying to keep all of that in one document will quickly become unmanageable.

I would organize it like an RFC series
docs/

    README.md

    ROADMAP.md

    DECISIONS.md

    GLOSSARY.md

    PHILOSOPHY.md


rfc/

    RFC-0001 Vision

    RFC-0002 Core Architecture

    RFC-0003 Component Model

    RFC-0004 FastAPI Integration

    RFC-0005 HDN Language

    RFC-0006 Scoped Styles

    RFC-0007 Component Explorer

    RFC-0008 Addressable Components

    RFC-0009 HTMX Integration

    RFC-0010 Data Components

    RFC-0011 Visualization

    RFC-0012 Security

    RFC-0013 Async Architecture

    RFC-0014 Plugin Architecture

    RFC-0015 Routing

    RFC-0016 OpenAPI

    RFC-0017 CLI

    RFC-0018 Packaging

    RFC-0019 Testing

    RFC-0020 Performance

    RFC-0021 Browser Runtime

    RFC-0022 Theming

    RFC-0023 Accessibility

    RFC-0024 Developer Experience

    RFC-0025 Component Lifecycle

    RFC-0026 State Management

    RFC-0027 Data Sources

    RFC-0028 Deployment

    RFC-0029 Roadmap to 1.0

I think you'll ultimately end up with around 30 RFCs.

I would also write implementation specifications

Separate from architecture.

implementation/

    Rendering Engine

    HTML Serializer

    CSS Compiler

    HDN Parser

    Component Registry

    Router Generator

    OpenAPI Generator

    Explorer Backend

    Explorer Frontend

    Asset Pipeline

    Plugin Loader

    Async Runtime

    Build System

These answer

"How do we build it?"

The RFCs answer

"What are we building?"

Then acceptance criteria

Every subsystem should have

acceptance/

    Component Model

    HDN

    Explorer

    Scoped Styles

    DataEditor

    Charts

    Security

    Async

Each one contains

functional requirements

non-functional requirements

performance goals

accessibility goals

security goals

testing checklist

API references

I would also write API specifications before coding.

Example

api/

    Component.md

    Props.md

    Field.md

    DataEditor.md

    Chart.md

    Page.md

    Action.md

    Theme.md

    Auto.md

These become the public documentation.

One thing I'd add

I think Hedron deserves something we didn't do for OntoCode.

A set of design principles.

Maybe 15–20 of them.

For example:

Progressive Disclosure

Beginners should never need to understand advanced features before becoming productive.

Server First

Prefer server rendering unless browser execution provides clear user value.

Standards First

Prefer HTML, CSS, HTTP, HTMX, and Web Components over proprietary protocols.

FastAPI Native

Prefer FastAPI extension points over framework replacement.

Typed Everything

Public APIs should be strongly typed wherever practical.

Explicit Business Logic

Framework mechanics may be inferred. Business behavior must remain explicit.

Component Ownership

Components own their:

template

styles

examples

tests

documentation

browser behavior

Security by Default

Unsafe behavior should require explicit opt-in.

Explain the Magic

Every automatic behavior must be inspectable in the Component Explorer.

I actually think this principle may become one of Hedron's defining characteristics.

I also think we need one document we haven't discussed
Non-goals

This is incredibly valuable.

For example:

Hedron is not an ORM.

Hedron is not a frontend framework.

Hedron is not trying to replace SQLAlchemy.

Hedron is not a JavaScript build tool.

Hedron is not a client-side state manager.

Hedron is not trying to replace Plotly.

Hedron is not trying to replace HTMX.

That document prevents feature creep.

Before writing RFCs, I would add four foundational documents

These sit above everything else because they guide every design decision.

FOUNDATIONS/

    01_VISION.md

    02_PHILOSOPHY.md

    03_DESIGN_PRINCIPLES.md

    04_NON_GOALS.md

Every future RFC should be evaluated against those four documents.

One suggestion

I would make the RFC process part of the project itself.

For example:

RFC Status

Draft

Accepted

Implemented

Deprecated

Rejected

Every RFC includes:

Motivation

Background

Proposed design

Alternatives considered

Security implications

Performance implications

Accessibility implications

Testing strategy

Migration strategy

Open questions

Acceptance criteria

That gives Hedron the same kind of engineering discipline seen in projects like Rust and Python. It also makes it much easier for contributors to understand not just what the framework does, but why each design decision was made. I think that will pay off as the project grows.

## 117. You

How do I share this entire conversation and the files you made with my desktop codex app?

## 118. ChatGPT

There are a few ways to do it, depending on how you use Codex. If your goal is for Codex to "know everything we've designed so far," I'd recommend creating a proper project rather than trying to paste a huge chat.

Option 1 (Recommended): Create a Hedron design repository

This is what I'd do.

Create a new Git repository called hedron-design.

Download all of the .docx files we've created.

Convert them to Markdown (Codex works much better with Markdown than Word documents).

Organize them like this:

hedron-design/
├── README.md
├── FOUNDATIONS/
├── RFC/
├── IMPLEMENTATION/
├── API/
├── ACCEPTANCE/
├── ROADMAP/
└── DECISIONS/

Then open that folder in the Codex desktop app.

This gives Codex persistent access to the design docs instead of relying on chat history.

Option 2: Use ChatGPT Projects (if available)

If your desktop Codex app supports ChatGPT Projects:

Create a new Project called Hedron.

Upload all of the design documents.

Continue working inside that project.

This keeps the files and future chats together.

Option 3: Share the conversation

If your ChatGPT interface has Share:

Open the conversation.

Click Share.

Copy the shared link.

You can then open that link on your desktop.

Note that a shared conversation does not automatically become editable context for Codex. It's mainly for reading.

Option 4: Build a proper knowledge base (my favorite)

Since we're planning Hedron before writing code, I'd actually create:

hedron/

    docs/

        foundations/

        rfc/

        api/

        architecture/

        implementation/

        acceptance/

        roadmap/

Every document we create goes there.

Then Codex can search the entire project instead of trying to remember a 200-message conversation.

I think this will work much better than relying on context windows.

One thing I'd change

Right now we've accumulated a lot of Word documents.

If we're serious about Hedron, I'd stop creating .docx files and switch to Markdown immediately.

Advantages:

Git-friendly

Diffable

Searchable

Codex reads it much better

Cursor reads it well

GitHub renders it

Easy to generate documentation later

Instead of:

RFC-0004.docx

you'd have:

RFC-0004_HDN.md

That becomes the permanent source of truth.

What I would do if I were starting today

I'd spend the next phase not writing code at all.

Instead, I'd produce a complete design repository:

~30 RFCs

~20 API specifications

~20 implementation specifications

Architecture Decision Records (ADRs)

Acceptance tests

Example applications

Component style guide

By the time you write the first line of Hedron code, most of the major design decisions will already be documented.

Given how ambitious Hedron has become, I think that investment will save a lot of redesign later.

In fact, I'd be happy to help you build this as a proper GitHub-style design repository in Markdown rather than continuing as a series of standalone documents. I think that's the right next phase for the project.
