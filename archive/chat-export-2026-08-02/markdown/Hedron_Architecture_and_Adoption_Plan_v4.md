**Hedron Architecture and Adoption Plan**

*Version 4 - Python-first, FastAPI flagship, framework-neutral core*

Purpose. This document consolidates the current Hedron direction into one implementation and adoption plan. It replaces the earlier Rust-first architecture with a Python-first framework that can later offload targeted work to Rust only when profiling justifies it.

# 1. Executive Summary

Hedron is a typed, component-based framework for building server-rendered Python web interfaces with HTML, HTMX, and progressive enhancement. The flagship installation, \`pip install hedron\`, provides the best possible FastAPI experience. Flask and Django users install dedicated adapter packages that depend on \`hedron-core\` and do not install FastAPI.

- Beginner-first: users can build useful pages with Python components before learning HDN, the compiler, or advanced browser integration.

- Pydantic-powered but Hedron-owned: users import Hedron model classes, not Pydantic directly, and only supported portable features are exposed.

- FastAPI-first but not FastAPI-bound: the public product centers FastAPI, while the core rendering and component system remain framework-neutral.

- Python-first implementation: all MVP logic is written in Python; optional Rust acceleration is a later optimization path.

- Progressive control: built-in components, configuration, composition, slots, HDN templates, Web Components, and compiler extensions form a gradual learning ladder.

# 2. Product Positioning

Initial public positioning:

> Hedron is a typed component framework for building FastAPI interfaces with HTML, HTMX, and progressive enhancement - without requiring Node.js.

Secondary positioning after the core product is stable:

> Hedron components can also run in Flask and Django through dedicated adapters.

Hedron should not initially lead with cross-language runtimes, Rust internals, or a universal specification. Those are future capabilities, not the first reason a developer installs the framework.

# 3. Governing Design Principles

- **Progressive disclosure:** Every advanced concept appears only after the user encounters the problem it solves.

- **One architecture:** Beginner and expert APIs compile through the same component and rendering model.

- **HTML first:** Hedron emits standards-based HTML and uses HTMX/Web Components as progressive enhancement.

- **Framework adapters, not forks:** FastAPI, Flask, and Django integrations share the same core semantics.

- **Semantic familiarity:** Adopt React-like concepts only when they naturally fit server-rendered component composition.

- **Measure before optimizing:** Rust is introduced only after profiling shows a meaningful bottleneck.

- **Escape hatches at every level:** Users can add raw attributes, native HTML, HDN, or Web Components without replacing the framework.

# 4. Packaging and Distribution

The package naming model should make the obvious install path the flagship FastAPI experience while allowing Flask and Django users to avoid installing FastAPI.

| Distribution | Installs | Primary purpose | Recommended import |
|----|----|----|----|
| hedron | hedron-core, FastAPI, Starlette | Flagship FastAPI framework | from hedron import Hedron, Page, Card |
| hedron-core | Pydantic and core utilities only | Framework-neutral component and rendering engine | Internal or advanced direct use |
| hedron-flask | hedron-core, Flask | Complete Flask adapter distribution | from hedron_flask import HedronFlask, Page |
| hedron-django | hedron-core, Django | Complete Django adapter distribution | from hedron_django import page, Page |

## 4.1 Dependency graph

> hedron  
> ├── hedron-core  
> ├── fastapi  
> └── starlette  
>   
> hedron-flask  
> ├── hedron-core  
> └── flask  
>   
> hedron-django  
> ├── hedron-core  
> └── django

## 4.2 Import ergonomics

Each adapter package re-exports the shared component API so users do not need to import directly from \`hedron_core\`.

**FastAPI:** from hedron import Hedron, Page, Card, Button, Props

**Flask:** from hedron_flask import HedronFlask, Page, Card, Button, Props

**Django:** from hedron_django import page, Page, Card, Button, Props

# 5. Python-First Architecture

The MVP should be pure Python. Native code is not part of the required architecture.

> Python component API  
> ↓  
> Hedron component tree  
> ↓  
> Python renderer / HDN compiler  
> ↓  
> Framework adapter  
> ↓  
> HTML response + HTMX headers

## 5.1 Core package boundaries

- **components:** Node types, built-in components, slots, variants, composition.

- **models:** Hedron-owned Model, Props, FormModel, Field, supported-type validation.

- **rendering:** HTML escaping, attribute normalization, page and fragment rendering.

- **hdn:** Lexer, parser, AST, compiler, diagnostics, cached render programs.

- **htmx:** Request detection, response headers, actions, redirects, swaps.

- **context:** Framework-neutral request and render context.

- **protocols:** Interfaces implemented by FastAPI, Flask, and Django adapters.

# 6. Hedron Model System

Developers should never need to subclass \`pydantic.BaseModel\` for ordinary Hedron component work. Hedron exposes a constrained, purpose-specific model API and uses Pydantic internally.

> from hedron import Props, Model, Field  
>   
> class User(Model):  
> id: int  
> name: str  
>   
> class UserCardProps(Props):  
> user: User  
> compact: bool = False

## 6.1 Public model classes

- \`Model\`: portable domain data used by components.

- \`Props\`: component input contracts.

- \`FormModel\`: validated form/action input.

- \`EventPayload\`: typed browser or server event payloads.

- \`Field\`: Hedron-owned constraints and metadata limited to supported behavior.

## 6.2 Supported MVP type system

- str, bool, int, float, None

- Literal and Enum

- list\[T\] and dict\[str, T\]

- T \| None

- Nested Hedron models

- ComponentNode and list\[ComponentNode\]

- TrustedHtml and selected URL/date-like Hedron types

## 6.3 Restrictions

Unsupported or non-portable constructs should fail at class creation time with Hedron-specific diagnostics. Initial restrictions should include arbitrary Python objects, callables as props, arbitrary serializers, unrestricted model configuration, and custom validators that cannot be represented consistently.

# 7. Beginner Experience and Progressive Disclosure

A user should obtain visible value before learning HDN, component specifications, Web Components, or compiler internals.

> from hedron import Hedron, Page, Card, Button  
>   
> app = Hedron()  
>   
> @app.page("/")  
> def home():  
> return Page(  
> Card(  
> title="Welcome",  
> children=\[Button("Load users", hx_get="/users")\],  
> )  
> )

## 7.1 Learning ladder

1.  **Level 1 - Use:** Built-in pages, cards, forms, buttons, tables, and layouts.

2.  **Level 2 - Configure:** Props, variants, design tokens, HTMX options, and slots.

3.  **Level 3 - Compose:** Create reusable Python components from existing components.

4.  **Level 4 - Customize:** Override or eject built-in templates into local HDN.

5.  **Level 5 - Extend:** Create Web Components, compiler plugins, or custom adapter features.

## 7.2 Documentation rule

The first tutorial must not introduce ASTs, Rust, the portable specification, or direct HDN authoring. Documentation should be organized around tasks and developer maturity rather than internal subsystems.

# 8. FastAPI Flagship Integration

\`pip install hedron\` should provide a batteries-included FastAPI application experience.

- \`Hedron()\` application class with all normal FastAPI capabilities.

- \`@app.page()\` for full pages and HTMX fragments.

- Direct component return values from route handlers.

- Native FastAPI dependency injection and request handling.

- Typed Hedron actions and route-aware URL generation.

- Automatic full-page versus fragment rendering based on HTMX request headers.

- Pydantic-backed forms exposed through Hedron FormModel.

- FastAPI lifespan integration for template compilation and development reload.

## 8.1 Existing FastAPI applications

Support a router-style integration in addition to \`Hedron()\` so existing applications can adopt Hedron incrementally.

> from fastapi import FastAPI  
> from hedron.fastapi import HedronRouter  
>   
> app = FastAPI()  
> ui = HedronRouter()  
> app.include_router(ui)

# 9. Flask and Django Adapters

Flask and Django are supported through separate distributions. They share component semantics but use framework-native routing, response, request, CSRF, URL reversing, and lifecycle behavior.

## 9.1 Flask adapter

> from flask import Flask  
> from hedron_flask import HedronFlask, Page, Card  
>   
> app = Flask(\_\_name\_\_)  
> ui = HedronFlask(app)  
>   
> @app.get("/")  
> @ui.page  
> def home():  
> return Page(Card(title="Hello"))

- Flask request context and sessions

- Blueprint support

- url_for integration

- Synchronous view support

- Optional Flask-WTF interoperability

## 9.2 Django adapter

> from hedron_django import page, Page, Card  
>   
> @page  
> def home(request):  
> return Page(Card(title="Hello"))

- Function and class-based views

- Django URL reversing

- CSRF and authentication context

- Django forms and model forms integration

- Messages framework and middleware compatibility

# 10. Framework Adapter Protocol

The core should define a small protocol so framework integrations remain thin and testable.

> class FrameworkAdapter(Protocol):  
> def make_response(self, result: RenderResult): ...  
> def request_context(self) -\> RequestContext: ...  
> def reverse_url(self, route_name: str, \*\*params): ...  
> def is_htmx_request(self) -\> bool: ...  
> def parse_form(self, model_type): ...

An adapter conformance suite should verify identical component rendering and HTMX semantics across FastAPI, Flask, and Django.

# 11. HDN Template Language

HDN remains an advanced customization tool, not an onboarding requirement. It should feel familiar to component-framework developers while remaining semantically native to Hedron.

- Lowercase tags represent HTML.

- Uppercase tags represent Hedron components.

- Hyphenated tags represent Web Components.

- Props, children, fragments, expressions, conditionals, iteration, and slots are supported where they naturally fit.

- Standard HTML names such as \`class\` and \`for\` are preferred over React-specific DOM aliases.

- React features are adopted only when they solve a real Hedron problem.

> \<Card title={props.title}\>  
> \<p\>{props.description}\</p\>  
> {props.showActions && (  
> \<Button hx-get={props.editUrl}\>Edit\</Button\>  
> )}  
> \</Card\>

## 11.1 HDN entry points

- \`hedron inspect Card\` explains the active built-in template.

- \`hedron eject Card\` creates a local editable \`.hdn\` file.

- Inline HDN fragments are available as an escape hatch for small custom markup.

- Built-in components continue to use the same HDN/rendering architecture underneath easy mode.

# 12. HTMX and Web Components

Hedron owns server-rendered structure. HTMX owns server interactions and fragment replacement. Web Components own persistent browser-side behavior when ordinary HTML and HTMX are insufficient.

- Use native HTMX attributes directly in advanced mode.

- Provide typed action helpers in beginner and intermediate modes.

- Prefer light DOM when HTMX must target content inside a custom element.

- Use Shadow DOM for isolated widgets that manage their own internal behavior.

- Bridge Web Component events to HTMX through explicit, typed event declarations.

# 13. Adoption Strategy

Adoption is the primary product risk. Hedron must win one clear audience before expanding its message.

- Primary beachhead: FastAPI developers who need modern interfaces without Node.js.

- 30-second first success: install, define one route, return components, see a page.

- Excellent built-in components for common CRUD, dashboard, form, and admin workflows.

- Incremental adoption in existing FastAPI, Flask, and Django applications.

- High-quality examples and migration guides from Jinja2 and raw HTMX.

- React-to-HDN migration tooling as a later adoption accelerator, especially for presentational component libraries.

- Stable escape hatches so teams never feel trapped by the standard component API.

## 13.1 Homepage message

> Build typed, component-based FastAPI interfaces without Node.js. Start with Python components; use HDN only when you need complete markup control.

# 14. Future Native Acceleration

Rust is explicitly deferred. The Python implementation should maintain clean internal protocols so selected workloads can later be accelerated without changing user-facing semantics.

- HTML escaping and large-tree rendering

- HDN parsing and compilation

- Formatter and language server

- Static analysis and source mapping

- Incremental compilation for large projects

A future \`hedron-native\` package may provide optional acceleration. The pure-Python path must remain supported and produce identical output.

# 15. Implementation Roadmap

6.  **Phase 1 - Core and FastAPI MVP:** hedron-core component tree, renderer, escaping, Hedron app, page routes, direct responses, HTML/HTMX primitives.

7.  **Phase 2 - Models, forms, and actions:** Model, Props, FormModel, Field, supported-type validation, AutoForm, validation errors, typed actions.

8.  **Phase 3 - Built-in component system:** Layouts, cards, forms, tables, navigation, slots, variants, design tokens, accessibility baseline.

9.  **Phase 4 - HDN customization:** Parser, AST, expressions, template overrides, inspect/eject workflow, syntax highlighting.

10. **Phase 5 - Flask and Django adapters:** Dedicated distributions, conformance tests, framework-native forms, URL reversing, CSRF, sessions.

11. **Phase 6 - Browser components:** Web Component helpers, event bridges, rich widget guidance, packaged components.

12. **Phase 7 - Adoption tooling:** Project scaffolding, migration guides, React-to-HDN analysis, component registry, examples.

13. **Phase 8 - Performance and optional native work:** Profile production workloads; offload only proven bottlenecks.

# 16. Initial Non-Goals

- Competing with React as a full client-side runtime.

- Requiring Node.js, bundlers, hydration, or a virtual DOM.

- Building Java and Node bindings before Python product-market fit.

- Publishing a rigid universal component standard before real-world usage stabilizes the model.

- Using Rust merely for marketing or theoretical performance.

- Replacing FastAPI, Flask, or Django routing and dependency systems with a proprietary application model.

# 17. Early Success Criteria

| Area | Success criterion |
|----|----|
| Onboarding | A new FastAPI user can install Hedron and render a useful page in under five minutes. |
| Simplicity | A CRUD application can be built without direct HDN authoring. |
| Control | An advanced user can eject and customize a component without rewriting the application. |
| Portability | The same shared component renders identically in FastAPI, Flask, and Django adapter tests. |
| Performance | Pure-Python rendering is adequate for representative dashboards and forms before any native work. |
| Adoption | Documentation, examples, and error messages consistently guide users to the next level of complexity only when needed. |

# 18. Final Direction

> Hedron begins as a Python-first, FastAPI-centered component framework. The \`hedron\` package installs the complete FastAPI experience. \`hedron-core\` contains the framework-neutral engine, while \`hedron-flask\` and \`hedron-django\` provide complete alternative integrations without installing FastAPI. Advanced capabilities - HDN, Web Components, portable specifications, and native acceleration - are introduced progressively and only when they solve demonstrated user needs.
