**HyperUI**

Architecture and Product Plan

*A cross-language server-driven component system with JSX-like templates, Pydantic contracts, HTMX, Web Components, and a Rust core*

**Revision 2.0 - August 2026**

# Executive Summary

HyperUI is a proposed cross-language component platform for building modern server-driven interfaces without requiring React or a Node.js toolchain. It combines React-style component composition with direct HTML authoring, HTMX for server interaction, Web Components for durable browser behavior, Pydantic for Python-side contracts, and a shared Rust implementation for compilation, validation, rendering, and code generation.

The central architectural correction in this revision is that a component contract alone is not enough. React components are productive because developers can directly express markup and compose components in a JSX-like syntax. HyperUI therefore treats the template language as a first-class pillar rather than an implementation detail.

## Core Thesis

**Pydantic defines what a component accepts. HyperUI Markup defines what it renders. HTMX defines how the server participates. Web Components define rich browser behavior. Rust provides the portable implementation core.**

## Primary Deliverables

- A canonical, language-neutral component specification.

- A JSX-inspired .hui template language that allows direct HTML authoring and component composition.

- A Rust compiler and renderer with ahead-of-time and development-time modes.

- A Pydantic-to-spec compiler and Python/FastAPI runtime.

- Idiomatic Java/Spring and Node/TypeScript adapters generated from the same component metadata.

- First-class HTMX and Web Component interoperation.

- A code-generation pipeline for bindings, documentation, tests, and design-system packages.

# 1. Product Vision

HyperUI should be positioned as a portable server-component ecosystem rather than merely a Rust HTML renderer. Its goal is to give backend teams a component-oriented authoring model while preserving standards-based HTML and minimizing client-side framework requirements.

## 1.1 Target Users

- Python/FastAPI teams in environments where Node.js is unavailable or disallowed.

- Java/Spring teams that want component ergonomics without adopting a client-rendered SPA framework.

- Mixed-language enterprises that need one design system across Python, Java, and Node services.

- Government and regulated environments where build-chain simplicity, auditability, and offline deployment matter.

- Open-source maintainers building reusable HTMX and Web Component libraries.

## 1.2 Product Promise

Developers should be able to write reusable components with familiar markup, receive compile-time validation against typed contracts, render identical accessible HTML from multiple backend languages, and progressively add browser behavior without adopting a full JavaScript application runtime.

\<UserCard user={props.user}\>  
\<Button  
variant="primary"  
hx-get={"/users/" + props.user.id}  
hx-target="#user-details"  
\>  
View user  
\</Button\>  
\</UserCard\>

# 2. Design Principles

**HTML first:** Native HTML remains visible and understandable. HyperUI does not replace the platform with an opaque virtual DOM.

**Direct markup authoring:** Developers can write HTML-like templates directly rather than constructing every element through object builders.

**Portable semantics:** Component contracts and templates cannot depend on Python, JavaScript, or Java execution semantics.

**Progressive enhancement:** Server-rendered HTML should remain useful before optional browser-side enhancement is applied.

**Thin language adapters:** Bindings provide idiomatic syntax but do not reimplement rendering rules.

**Compile when possible:** Templates and specifications are validated ahead of time for production while retaining fast development reloads.

**Safe by default:** Expression output is escaped; raw HTML requires an explicit trusted type.

**Accessible by construction:** The specification can encode required labels, roles, states, and keyboard behavior.

**No mandatory Node.js toolchain:** The compiler, renderer, and Python workflow must operate without npm, bundlers, or Node.js.

**Interoperable, not captive:** Generated output is standard HTML, HTMX attributes, CSS classes, and custom-element tags.

# 3. System Architecture

Host-language component contract  
(Pydantic / Java record / TypeScript interface)  
+  
.hui component template  
\|  
v  
HyperUI Rust compiler  
parse -\> resolve -\> type-check -\> validate  
\|  
v  
Canonical Component IR / Spec  
\|  
+---------+---------+  
\| \|  
v v  
Rust renderer Code generators  
\| Python / Java / TS  
v \|  
HTML + HTMX + v  
custom elements Native component APIs  
\|  
v  
Optional Web Component behavior

## 3.1 Architectural Layers

| **Layer** | **Responsibilities** |
|----|----|
| **Authoring layer** | Pydantic models, Java records/builders, TypeScript types, .hui templates |
| **Specification layer** | Canonical component definitions, props, slots, events, rendering semantics, accessibility metadata |
| **Compiler layer** | Template parser, expression parser, resolver, type checker, diagnostics, optimizer |
| **Runtime layer** | Rust renderer, streaming support, component registry, host-language bindings |
| **Browser layer** | HTML, CSS, HTMX, optional Web Components and ES modules |
| **Tooling layer** | CLI, formatter, language server, documentation generator, conformance suite |

# 4. Canonical Component Specification

The specification is the stable semantic foundation. It describes a component independently of any one host language. Pydantic is an excellent authoring surface for Python, but the canonical form must remain plain, portable, and implementable in Rust, Java, TypeScript, or other ecosystems.

## 4.1 Specification Contents

- Identity: component name, namespace, version, and kind.

- Contract: properties, types, defaults, nullability, validation constraints, and deprecations.

- Composition: unnamed children, named slots, accepted child categories, and cardinality.

- Rendering: native tag, attribute mappings, Boolean-attribute behavior, class mappings, and content placement.

- Events: event name, payload schema, bubbling, composition, and cancelability.

- HTMX semantics: typed mappings for hx-\* attributes, request parameters, triggers, targets, and swaps.

- Web Component semantics: custom-element tag, observed attributes, properties, methods, and emitted events.

- Accessibility: required accessible name, relationships, state mappings, semantic constraints, and keyboard expectations.

- Design-system profiles: token and class mappings that can vary without changing the public semantic API.

## 4.2 Example Canonical Specification

spec_version: "1.0"  
component:  
namespace: core  
name: Button  
tag: button  
version: "1.0.0"  
properties:  
variant:  
type: enum  
values: \[primary, secondary, danger\]  
default: primary  
rendering:  
target: css_class  
disabled:  
type: boolean  
default: false  
rendering:  
target: boolean_attribute  
html_name: disabled  
children:  
allowed: true  
content_types: \[text, component\]  
accessibility:  
requires_accessible_name: true

## 4.3 Compatibility Policy

- Adding an optional property with a default is normally backward compatible.

- Removing or renaming a public property is a breaking change.

- Changing rendered markup may be breaking even when the data contract is unchanged.

- Event payload changes follow semantic-versioning rules.

- Generated bindings include deprecation annotations and migration messages.

- The compiler records the specification version and refuses unsupported major versions.

# 5. Pydantic Authoring Layer

Pydantic provides the primary Python authoring experience for component contracts. It supplies validation, introspection, JSON Schema generation, nested models, discriminated unions, clear error messages, and a familiar Annotated-based metadata model.

## 5.1 Example Contract

from typing import Annotated, Literal  
from pydantic import BaseModel, Field, HttpUrl  
from hyperui.spec import component, HtmlAttribute, BooleanAttribute  
  
@component(name="UserCard", template="user_card.hui")  
class UserCardProps(BaseModel):  
user_id: str  
name: Annotated\[str, Field(min_length=1)\]  
email: str  
avatar_url: HttpUrl \| None = None  
featured: Annotated\[  
bool,  
BooleanAttribute("featured"),  
\] = False

## 5.2 Compilation Pipeline

1.  Inspect the component decorator and Pydantic model.

2.  Generate Pydantic JSON Schema for structural types and constraints.

3.  Read FieldInfo and HyperUI Annotated metadata.

4.  Normalize Python types into the canonical HyperUI type system.

5.  Resolve nested models, references, unions, defaults, and validation constraints.

6.  Load and type-check the associated .hui template.

7.  Produce the canonical ComponentSpec and compiled RenderProgram.

8.  Generate optional YAML, JSON, documentation, and language bindings.

## 5.3 Dependency Rule

The dependency direction is one-way: Pydantic models compile into the HyperUI specification. The specification must never require a Pydantic runtime. This preserves portability and allows future Rust, Java, Kotlin, TypeScript, or graphical authoring tools.

# 6. HyperUI Markup (.hui)

HyperUI Markup is a JSX-inspired, HTML-centric template language compiled by Rust. It restores the defining React component capability that object-only APIs miss: developers can directly author markup while embedding components, expressions, conditions, loops, and slots.

## 6.1 Tag Resolution Rules

| **Syntax** | **Meaning** | **Example** |
|----|----|----|
| **\<div\>** | Native HTML element | \<section\>, \<button\>, \<input\> |
| **\<Button\>** | Registered HyperUI component | \<Card\>, \<UserCard\>, \<DataGrid\> |
| **\<ontology-tree\>** | Web Component / custom element | \<code-editor\>, \<map-view\> |
| **\<slot\>** | Component insertion point | \<slot name="header"\> |

## 6.2 Basic Template

\<article class="user-card"\>  
\<header\>  
\<Avatar src={props.avatar_url} alt={props.name} /\>  
\<h2\>{props.name}\</h2\>  
\</header\>  
  
\<p\>{props.email}\</p\>  
  
\<Button  
variant="primary"  
hx-get={"/users/" + props.user_id}  
hx-target="#user-details"  
\>  
View user  
\</Button\>  
\</article\>

## 6.3 Expression Language

The expression language should be intentionally constrained and portable. It is not embedded Python or JavaScript. The initial implementation should support:

- Property and local-variable access: props.user.name and user.id.

- Literals: strings, numbers, booleans, null, lists, and maps where needed.

- Safe operators: equality, comparison, Boolean logic, null coalescing, and string concatenation.

- Calls to a small set of pure, compiler-known helper functions such as classes(), url(), format_date(), and default().

- No arbitrary filesystem, network, reflection, dynamic import, or host-language execution.

## 6.4 Control Flow

{#if props.users}  
\<ul\>  
{#for user in props.users}  
\<li key={user.id}\>  
\<UserCard user={user} /\>  
\</li\>  
{/for}  
\</ul\>  
{:else}  
\<EmptyState\>No users found.\</EmptyState\>  
{/if}

## 6.5 Slots and Children

\<Card\>  
\<slot name="header"\>  
\<h2\>{props.title}\</h2\>  
\</slot\>  
  
\<slot /\>  
  
{#if slots.footer}  
\<footer\>\<slot name="footer" /\>\</footer\>  
{/if}  
\</Card\>

## 6.6 Escaping and Trusted HTML

Expression output is HTML-escaped by default. Raw HTML requires an explicit TrustedHtml value and an explicit template directive. This avoids accidental injection while preserving a controlled escape hatch.

\<div\>{props.user_supplied_text}\</div\>  
  
\<!-- Only accepted when body is typed as TrustedHtml --\>  
\<div\>{@html props.body}\</div\>

## 6.7 Inline and External Templates

- External .hui files are the preferred form for substantial components.

- Inline hui("...") templates are supported for small Python components and tests.

- The same .hui file may be consumed by Python, Java, and Node adapters.

- The template compiler produces source maps so diagnostics point to the original .hui file.

# 7. Template Compiler and Intermediate Representation

The compiler transforms human-readable markup into a validated, language-neutral render program. The render program should be stable enough to cache and serialize, but internal enough that it can evolve without becoming the public specification format.

## 7.1 Compiler Stages

9.  Lex and parse HTML-like markup, directives, expressions, and comments.

10. Resolve native tags, registered HyperUI components, and custom elements.

11. Bind props, locals, slots, and loop variables.

12. Type-check attributes and expressions against component contracts.

13. Validate HTML semantics, void-element rules, custom-element naming, and accessibility constraints.

14. Lower templates into a typed Component IR.

15. Optimize static fragments, constant expressions, class merging, and attribute ordering.

16. Emit a RenderProgram, diagnostics, source map, and dependency manifest.

## 7.2 Conceptual IR

ComponentCall {  
component: "Button",  
props: {  
"variant": Literal("primary"),  
"hx-get": Concat("/users/", Get(props, "user_id")),  
"hx-target": Literal("#user-details")  
},  
children: \[Text("View user")\]  
}

## 7.3 Diagnostics

- Unknown component or property.

- Missing required property.

- Property type mismatch.

- Invalid child or slot cardinality.

- Invalid HTMX value or unsafe target selector.

- Invalid custom-element name.

- Potentially inaccessible icon-only control.

- Use of raw HTML with a non-TrustedHtml value.

- Unreachable branches and unused slots where statically detectable.

# 8. Rust Core

Rust is the reference implementation for parsing, validation, rendering, code generation, and native bindings. The core should not expose Rust-specific concepts in the public cross-language model.

## 8.1 Core Crates

| **Crate** | **Purpose** |
|----|----|
| **hyperui-spec** | Canonical specification types, validation, and versioning. |
| **hyperui-markup** | Lexer, parser, AST, formatter, and source maps for .hui. |
| **hyperui-expr** | Portable expression parser, type checker, and evaluator. |
| **hyperui-compiler** | Resolution, semantic analysis, diagnostics, lowering, and optimization. |
| **hyperui-render** | String and streaming renderers, escaping, attributes, and buffers. |
| **hyperui-html** | Native HTML metadata, void elements, attributes, and semantic validation. |
| **hyperui-htmx** | Typed HTMX attributes, triggers, swaps, and request semantics. |
| **hyperui-web-components** | Custom-element metadata and generated wrapper support. |
| **hyperui-codegen** | Python, Java, Kotlin, TypeScript, docs, and test generation. |
| **hyperui-cli** | Build, watch, format, inspect, validate, and generate commands. |

## 8.2 Rendering Model

- Render whole fragments in a single native call rather than crossing FFI for every node.

- Precompute static markup and attribute layouts during compilation.

- Use deterministic attribute ordering for reproducible snapshots and caches.

- Support direct string output, byte buffers, and streaming writers.

- Keep optional incremental or diff-based rendering out of the MVP unless real use cases demand it.

# 9. Host-Language APIs

## 9.1 Python and FastAPI

from fastapi import FastAPI  
from hyperui.fastapi import HyperUIResponse  
from components import UserCard  
  
app = FastAPI()  
  
@app.get("/users/{user_id}")  
def user_page(user_id: str):  
return HyperUIResponse(  
UserCard(  
user_id=user_id,  
name="Ada Lovelace",  
email="ada@example.com",  
)  
)

## 9.2 Java and Spring

@GetMapping("/users/{id}")  
public HyperUIResponse user(@PathVariable String id) {  
return HyperUIResponse.of(  
UserCard.builder()  
.userId(id)  
.name("Ada Lovelace")  
.email("ada@example.com")  
.build()  
);  
}

## 9.3 Node and TypeScript

app.get("/users/:id", (req, res) =\> {  
res.send(render(  
UserCard({  
userId: req.params.id,  
name: "Ada Lovelace",  
email: "ada@example.com",  
})  
));  
});

## 9.4 FFI Boundary

Each binding should batch component data into one render invocation per fragment. Binding crates convert host-language values into canonical runtime values, call the Rust engine, then map errors and results back into native exceptions or result types.

# 10. HTMX Integration

HTMX remains the preferred mechanism for server-driven requests, fragment updates, navigation, and form submission. HyperUI should provide validation and typed conveniences without hiding the generated HTML.

## 10.1 Template Example

\<Button  
hx-post="/users"  
hx-target="#users"  
hx-swap="beforeend"  
hx-include="#new-user-form"  
\>  
Create user  
\</Button\>

## 10.2 Typed Semantics

- Validate hx-swap against supported values.

- Validate hx-trigger syntax and modifier combinations.

- Allow component metadata to declare common request and target patterns.

- Generate hidden inputs or request parameters for CustomEvent payload bridging.

- Preserve direct hx-\* escape hatches for advanced HTMX usage.

- Expose HTMX lifecycle hooks to Web Components without introducing framework-specific client state.

# 11. Web Components Integration

Web Components provide the client-side component boundary for widgets that need persistent local state, browser APIs, third-party visualization libraries, or behavior that is inefficient to round-trip to the server.

## 11.1 Direct Use in .hui

\<ontology-tree  
ontology-id={props.ontology_id}  
editable={props.editable}  
data-url={props.tree_endpoint}  
/\>  
  
\<script module="/static/components/ontology-tree.js" /\>

## 11.2 Responsibility Boundary

| **Concern**                      | **Owner**                      |
|----------------------------------|--------------------------------|
| **Server data validation**       | Host-language model / Pydantic |
| **Markup and composition**       | .hui template                  |
| **Requests and fragment swaps**  | HTMX                           |
| **Persistent local interaction** | Web Component                  |
| **Compilation and rendering**    | Rust core                      |
| **Visual design**                | CSS / design-system profile    |

## 11.3 Light DOM Default

Light DOM should be the default for HTMX-first components because targets, forms, and server-rendered children remain visible to HTMX and global CSS. Shadow DOM is appropriate for highly isolated widgets whose internals are not directly targeted by HTMX.

## 11.4 Events

this.dispatchEvent(new CustomEvent("node-selected", {  
bubbles: true,  
composed: true,  
detail: { nodeId: selectedNode.id }  
}));

The specification can describe the event payload once and generate Python payload models, Rust structs, Java records, TypeScript CustomEvent types, and documentation.

# 12. Development and Production Workflows

## 12.1 Development Mode

hyperui dev app/  
  
\# Responsibilities:  
\# - watch .hui and specification files  
\# - incrementally compile changed components  
\# - expose diagnostics and source locations  
\# - notify the host development server  
\# - optionally trigger browser refresh

## 12.2 Production Build

hyperui build components/ --release  
  
.hyperui/  
├── manifest.json  
├── component-registry.bin  
├── render-programs.bin  
├── generated/  
└── static-manifest.json

## 12.3 No-Node Requirement

- The HyperUI CLI is a native Rust binary.

- Python wheels bundle or depend on compatible native binaries.

- Web Component JavaScript may be authored as browser-native ES modules.

- Optional JavaScript bundling can be supported later but is never required for the core workflow.

- All first-party examples must have a no-Node path.

# 13. Code Generation

The canonical specification enables generation of native APIs while the .hui template remains the shared render definition.

- Python Pydantic runtime classes and type stubs.

- Java builders, records, annotations, and Spring response adapters.

- Kotlin DSLs and data classes.

- TypeScript interfaces, factory functions, JSX typings where useful, and custom-element declarations.

- Rust structs and enums.

- Component documentation, examples, prop tables, event payloads, and accessibility notes.

- Cross-language conformance fixtures and snapshot tests.

- Design-system packages that implement the same semantic components with alternate markup and classes.

# 14. Design Systems

HyperUI can become a cross-language design-system engine. A semantic component API can remain stable while rendering profiles map it to USWDS, Bootstrap, Carbon, Tailwind conventions, or an organization-specific system.

\<Button variant="primary"\>Save\</Button\>  
  
\# USWDS profile  
\<button class="usa-button"\>Save\</button\>  
  
\# Bootstrap profile  
\<button class="btn btn-primary"\>Save\</button\>

## 14.1 Profile Constraints

- Profiles may change markup and classes only within declared compatibility boundaries.

- Accessibility requirements cannot be disabled by a profile.

- Profile-specific properties should be namespaced or modeled as extensions.

- The compiler should detect components unsupported by the selected profile.

- Conformance tests verify semantic parity across profiles.

# 15. Security and Safety

- HTML escaping is mandatory for ordinary expression output.

- Raw HTML requires TrustedHtml and an explicit {@html ...} directive.

- URL-valued properties receive scheme validation where applicable.

- Compiler helpers are pure and allowlisted; templates cannot execute arbitrary host code.

- Generated CSP guidance should avoid inline scripts where practical.

- HTMX request features should not silently bypass server-side authorization or CSRF protections.

- Web Component manifests identify required scripts and integrity metadata where deployment supports it.

- Production builds can prohibit dynamic template loading.

# 16. Accessibility

Accessibility should be represented in the specification and enforced during compilation where possible, rather than left entirely to runtime testing.

- Require an accessible name for buttons, links, inputs, and interactive custom components.

- Validate label-for and described-by references within statically known templates.

- Warn when click handlers or HTMX actions are attached to non-interactive elements.

- Allow component specs to declare keyboard interaction requirements.

- Generate ARIA state mappings from typed properties.

- Include accessibility examples and test cases in generated documentation.

- Provide optional integration with browser-based accessibility testing in CI.

# 17. Testing Strategy

## 17.1 Compiler Tests

- Parser golden tests.

- Expression type-checking tests.

- Diagnostic snapshot tests.

- Invalid HTML and custom-element cases.

- Specification-version compatibility fixtures.

## 17.2 Renderer Tests

- Deterministic HTML snapshots.

- Escaping and injection property tests.

- Void-element and Boolean-attribute tests.

- Streaming equivalence tests.

- Cross-platform output conformance.

## 17.3 Cross-Language Conformance

A common fixture describes inputs and expected HTML. Python, Java, Node, and Rust adapters must render byte-equivalent output unless the specification explicitly allows implementation variation.

## 17.4 Browser Integration

- HTMX fragment replacement tests.

- Custom-element lifecycle tests after swaps.

- CustomEvent-to-HTMX integration tests.

- Keyboard and focus tests.

- Progressive-enhancement tests with JavaScript disabled where applicable.

# 18. Repository Layout

hyperui/  
├── crates/  
│ ├── hyperui-spec/  
│ ├── hyperui-markup/  
│ ├── hyperui-expr/  
│ ├── hyperui-compiler/  
│ ├── hyperui-render/  
│ ├── hyperui-html/  
│ ├── hyperui-htmx/  
│ ├── hyperui-web-components/  
│ ├── hyperui-codegen/  
│ └── hyperui-cli/  
├── bindings/  
│ ├── python/  
│ ├── java/  
│ └── node/  
├── packages/  
│ ├── hyperui-pydantic/  
│ ├── hyperui-fastapi/  
│ ├── hyperui-spring/  
│ └── hyperui-express/  
├── schemas/  
├── components/  
├── examples/  
├── conformance/  
├── docs/  
└── rfcs/

# 19. MVP Scope

The MVP should prove the authoring model in Python before expanding the binding surface.

## 19.1 Included

- Rust parser and compiler for core .hui syntax.

- Native HTML, text expressions, property access, if/else, loops, components, children, and slots.

- Pydantic-to-spec compiler.

- Rust string renderer with escaping and deterministic output.

- Python/PyO3 binding and FastAPI response adapter.

- Typed HTMX attributes and direct custom-element rendering.

- Development watcher, formatter, diagnostics, and release build command.

- A small first-party component set: Button, Link, Card, FormField, Alert, Table, Modal shell, and custom-element wrapper.

- One real reference application built without Node.js.

## 19.2 Explicitly Deferred

- Client-side virtual DOM or hydration.

- Arbitrary embedded Python or JavaScript expressions.

- Automatic JavaScript bundling.

- Java and Node bindings before the Python API stabilizes.

- Incremental DOM diffing.

- A large visual component library.

- Graphical component editor.

- Universal state-management framework.

# 20. Roadmap

| **Phase** | **Outcome** |
|----|----|
| **Phase 0 - RFC and prototypes** | Finalize syntax, component spec, expression subset, diagnostics, and safety model. Build parser spikes and three representative components. |
| **Phase 1 - Rust foundation** | Implement specification, markup parser, expression engine, compiler, renderer, CLI, and snapshot suite. |
| **Phase 2 - Python MVP** | Implement Pydantic compiler, PyO3 binding, FastAPI integration, development reload, and reference application. |
| **Phase 3 - Component ecosystem** | Add schema-driven code generation, documentation tooling, design-system profiles, and Web Component event schemas. |
| **Phase 4 - Java/Spring** | Generate idiomatic Java/Kotlin APIs, package native libraries, and validate cross-language conformance. |
| **Phase 5 - Node/TypeScript** | Add napi-rs binding, TypeScript API, Express/Fastify helpers, and optional JSX typing support. |
| **Phase 6 - Advanced tooling** | Language server, IDE extensions, component inspector, static-site generation, streaming, and performance optimization. |

# 21. Success Metrics

- A new developer can build and run the reference FastAPI application without Node.js.

- A developer familiar with JSX can understand a .hui template with minimal documentation.

- Template errors identify the exact source span and expected type.

- Equivalent Python, Java, and Node inputs eventually produce conformant HTML.

- Production rendering is competitive with established server-side template engines.

- First-party components meet documented accessibility requirements.

- HTMX and Web Components can be integrated without hidden framework-specific browser state.

- The canonical specification remains usable independently of Pydantic and any single binding.

# 22. Major Risks and Mitigations

| **Risk** | **Mitigation** |
|----|----|
| **Template-language scope creep** | Keep the expression language deliberately small. Require RFCs for new syntax and prefer pure helper functions over embedded host code. |
| **Cross-language API mismatch** | Treat the spec as semantic and let each generator create idiomatic syntax. Validate using conformance fixtures rather than identical source APIs. |
| **Native packaging burden** | Start with Python and a limited target matrix. Automate releases and postpone additional bindings until the core proves value. |
| **Competing with mature ecosystems** | Focus on restricted and server-driven environments rather than claiming universal React replacement status. |
| **Web Component complexity** | Use browser standards directly, provide thin wrappers, and avoid inventing a second client framework. |
| **Debugging generated systems** | Preserve source maps, readable generated files, deterministic output, and inspection commands. |
| **Specification instability** | Version the spec early, maintain migration fixtures, and separate public spec from internal render IR. |

# 23. Strategic Positioning

HyperUI should not initially market itself as a universal React replacement. Its strongest initial position is:

**The component framework for modern HTMX applications that need typed contracts, JSX-like markup, and no Node.js toolchain.**

Longer term, the cross-language component specification and shared design-system capability provide the larger strategic opportunity. The Rust renderer is important, but the durable product asset is the combination of portable component contracts and portable component templates.

# 24. Recommended First Prototype

The first prototype should implement one complete vertical slice rather than a broad collection of partial features.

17. Define UserCardProps with Pydantic.

18. Author user_card.hui using native HTML, Avatar, Button, a conditional, and HTMX attributes.

19. Compile the model and template into a canonical ComponentSpec and RenderProgram.

20. Render the component through PyO3 inside a FastAPI route.

21. Insert the fragment with HTMX.

22. Include one \<user-menu\> Web Component that emits a typed CustomEvent.

23. Generate a human-readable spec file and diagnostics.

24. Use the same compiled component fixture to generate a Java builder and TypeScript declaration, even before full runtimes exist.

## Prototype Acceptance Criteria

- No Node.js is required.

- Changing a prop type creates a useful template diagnostic.

- User-controlled text is escaped.

- An invalid Button property fails compilation.

- HTMX updates the component correctly.

- The Web Component reconnects correctly after an HTMX swap.

- The rendered HTML is deterministic and snapshot-tested.

- The canonical specification can be serialized to YAML or JSON.

# Conclusion

The JSX-like .hui interface is not an optional convenience; it completes the component model. Pydantic-only or builder-only APIs would provide typed data but miss the direct, compositional markup experience that made React components compelling. HyperUI should therefore be built around two equally important portable artifacts: the component specification and the component template.

With that foundation, Rust can supply a fast and auditable compiler/runtime, Python can offer an exceptional Pydantic and FastAPI experience, HTMX can handle server interactions, and Web Components can provide rich browser behavior. This creates a coherent architecture for modern component-based development in environments where a traditional JavaScript framework toolchain is undesirable or impossible.
