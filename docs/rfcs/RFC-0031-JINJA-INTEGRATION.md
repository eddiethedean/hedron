# RFC-0031: Jinja integration

**Status:** Implementing · **Target:** phase 0.9 (`v0.9.0`)

## Summary

Hedron will replace its experimental custom HDN language with an optional Jinja integration. Jinja
owns template inheritance, includes, macros, conditions, loops, and HTML-oriented composition.
Hedron continues to own typed Python components, prop and slot validation, rendering, identity,
assets, approved headers, diagnostics, HTMX policies, and framework adapters.

The integration ships as a separate `hedron-jinja` distribution importing as `hedron_jinja`.
`hedron-core` and the default `hedron` install do not depend on Jinja. Applications opt in with
`pip install "hedron[jinja]"` or `pip install hedron-jinja`.

The primary authoring model remains typed Python. Jinja is the familiar, optional presentation
layer for applications and collaborators who prefer templates. Hedron does not fork Jinja, create a
second expression language, or claim that application-supplied templates are safe to execute when
their authors are untrusted.

## Decision

RFC-0030 reopened declarative authoring from first principles. This RFC selects its established
template-engine candidate with the following constraints:

1. Python components are canonical and can be used without Jinja.
2. Jinja is an adapter, not the Hedron component runtime or security boundary.
3. Template source is trusted application or installed-package code.
4. Components available to templates come from an explicit, immutable allowlist.
5. The Hedron extension renders nested components through `hedron_core.render()` and preserves the
   complete `RenderResult` metadata.
6. Strict escaping and template checks are the default, but they do not turn Jinja into a safe
   language for hostile template authors.
7. D-041 removes HDN in phase 0.9 without a compatibility runtime or converter. Its grammar,
   evaluator, render program, and file format do not constrain this design.

## User model

Hedron has two cooperating authoring layers:

| Layer | Best for | Owns |
|---|---|---|
| Typed Python components | reusable behavior, business rules, authorization, derived values, typed props and slots | computation and component contracts |
| Jinja templates | page layout, inheritance, includes, macros, simple presentation branching and repetition | trusted presentation composition |

A typical application prepares a typed view model in Python, then renders a template. The template
may invoke allowlisted Hedron components:

```python
from jinja2 import Environment, FileSystemLoader

from hedron import Model
from hedron_jinja import HedronJinja, TemplateSpec


class AccountView(Model):
    display_name: str
    plan: str


environment = Environment(loader=FileSystemLoader("templates"), autoescape=True)
templates = HedronJinja(
    environment,
    components={"StatusBadge": StatusBadge, "AccountMenu": AccountMenu},
)

ACCOUNT = TemplateSpec[AccountView]("account/detail.html", view_type=AccountView)
result = templates.render(ACCOUNT, AccountView(display_name="Ari", plan="Pro"))
```

```jinja
{% extends "base.html" %}

{% block content %}
  <h1>{{ view.display_name }}</h1>
  {% hedron "StatusBadge" status=view.plan %}
{% endblock %}
```

Framework adapters consume the returned `RenderResult`; ordinary response code does not manually
concatenate assets, headers, or diagnostics.

## Goals

- Make HTML-oriented page composition familiar to existing Python web developers.
- Reuse Jinja inheritance, includes, macros, whitespace control, editor support, and ecosystem
  knowledge.
- Let templates invoke typed Hedron components without exposing arbitrary Python imports or a
  global component registry.
- Preserve Hedron render metadata across a mixed Jinja/component tree.
- Provide strict defaults, precise diagnostics, static checks where sound, and runtime validation
  everywhere else.
- Offer deterministic inventory, dependency, migration, and production-build behavior.
- Keep pure-Python Hedron applications first-class and dependency-light.

## Non-goals

- Accepting templates from untrusted users, tenants, prompts, databases, or network responses.
- Making Jinja expressions statically equivalent to Python's type system.
- Reimplementing or extending Jinja's general expression language.
- Treating arbitrary Jinja macros as registered Hedron components.
- Allowing template text to import Python modules or discover every registered component.
- Converting all legacy HDN programs automatically.
- Making `hedron-core` depend on Jinja, MarkupSafe, Flask, Django, or an application loader.
- Replacing native Python components or the `render(...) -> RenderResult` contract.
- Hiding I/O in filters, globals, tests, component rendering, or template attribute access.
- Advertising `SandboxedEnvironment` as safe execution for hostile template authors.

## Packaging and dependencies

The integration is distributed independently:

| Distribution | Import | Required dependencies |
|---|---|---|
| `hedron-jinja` | `hedron_jinja` | matching `hedron-core`, `Jinja2>=3.1,<4` |
| `hedron[jinja]` | convenience extra | matching `hedron-jinja` |

`hedron-jinja` contains the Jinja extension, bindings, template contracts, checker, diagnostics,
and framework-neutral render session. Framework-specific response helpers stay in `hedron`,
`hedron-flask`, and `hedron-django` so dependency direction remains acyclic.

Jinja and MarkupSafe versions are recorded in build evidence and the compatibility matrix. Hedron
does not vendor either library. An incompatible Jinja major version requires an explicit
compatibility decision, not an unconstrained dependency upgrade.

## Public API

The initial public surface is:

```python
from hedron_jinja import (
    HedronJinja,
    HedronJinjaExtension,
    TemplateSpec,
    TemplateSource,
)
```

### `TemplateSpec[ViewT]`

`TemplateSpec` is an immutable typed reference to a template:

```python
ACCOUNT = TemplateSpec[AccountView](
    "account/detail.html",
    mode=RenderMode.PAGE,
    source=TemplateSource.APPLICATION,
)
```

Its fields are:

- `name: str`: loader-relative canonical name;
- `view_type: type[ViewT] | None`: captured from an explicit constructor argument when runtime
  validation is required; generic syntax alone is never used as runtime metadata;
- `mode: RenderMode`: `FRAGMENT` by default;
- `source: TemplateSource`: `APPLICATION` or `PACKAGE`;
- `logical_id: str | None`: stable diagnostic identity, derived from source and name by default.

Canonical names use `/`, contain no empty, `.` or `..` segments, contain no NUL, and are resolved by
the configured Jinja loader. Absolute filesystem paths and loader escape are rejected. Templates do
not receive their own filename as an authorization capability.

### `HedronJinja`

Construction binds one Jinja environment to one explicit component namespace:

```python
templates = HedronJinja(
    environment,
    components={"Card": Card, "StatusBadge": StatusBadge},
    strict=True,
)
```

Public operations are:

```python
templates.register_component(alias, factory)
templates.freeze()
templates.check(spec_or_name, *, view_type=None) -> tuple[Diagnostic, ...]
templates.render(spec_or_name, view, *, context=None, mode=None) -> RenderResult
await templates.render_async(spec_or_name, view, *, context=None, mode=None)
```

The component map accepts a `Component` subclass or a callable whose result is `NodeLike`. Callable
bindings must declare an explicit props contract; unconstrained `Callable[..., Any]` bindings are
rejected in strict mode. Aliases match `[A-Z][A-Za-z0-9_.-]*`, are case-sensitive, and are local to
the bound environment.

Registration is allowed only during application startup. The first check or render freezes the
binding automatically. Duplicate aliases, replacement after freeze, and factories without an
inspectable contract fail. `freeze()` is idempotent.

`render()` accepts either a `TemplateSpec` or a canonical string name. A `TemplateSpec` plus a
Hedron `Model` is the recommended typed path. A mapping is an escape hatch for gradual adoption;
strict checks can require a registered view type. The template receives exactly one application
value named `view` plus documented Hedron globals. Hedron does not flatten view fields into the
Jinja namespace.

`render_async()` permits Jinja async filters and includes when the environment was configured for
async execution. It does not make Hedron component rendering asynchronous and does not authorize
hidden I/O in component `render()` methods.

### Environment installation

`HedronJinja` installs `HedronJinjaExtension` once and fails if an incompatible extension instance
already owns the environment. It enforces `StrictUndefined` and HTML autoescape in strict mode.
Applications may configure loaders, bytecode caches, i18n, filters, and globals before binding.

For environments managed by Flask or Django, the owning adapter supplies a setup helper that binds
the existing environment rather than creating a competing loader or template configuration.

### Configuration

Project tooling reads this optional configuration when `hedron-jinja` is installed:

```toml
[tool.hedron.jinja]
application_roots = ["templates"]
strict = true
allow_dynamic_dependencies = false
max_template_depth = 32
max_macro_depth = 32
max_loop_iterations = 10000
max_total_loop_iterations = 50000
max_component_invocations = 10000
max_output_chars = 10000000
max_metadata_items = 10000
```

Paths are project-relative, canonicalized, nonsymlink-escaping directories. Package roots come from
verified plugin metadata, not this list. Unknown keys fail configuration validation. Runtime
constructor arguments may make limits stricter but may not silently weaken build policy; a weaker
production override requires a named configuration exception captured in evidence.

`strict=false` and `allow_dynamic_dependencies=true` are explicit experimental escape hatches.
Generated projects never set them. Jinja loader, bytecode cache, i18n, and application-specific
filters/globals remain normal Python environment configuration rather than duplicated TOML objects.

## Template syntax

### Inline component

```jinja
{% hedron "StatusBadge" status=view.plan compact=true %}
```

Rules:

- The component alias is a string literal. Dynamic aliases are prohibited.
- Props are named; positional props and `**mapping` expansion are prohibited.
- Values are ordinary Jinja expressions evaluated under the application's template trust boundary.
- `key=` is reserved for Hedron component identity and is not forwarded as a prop.
- `_`-prefixed names are reserved.
- The tag emits the component's rendered HTML at its source position.

### Component with default content

```jinja
{% hedron "Card" title=view.title with body %}
  <p>{{ view.summary }}</p>
{% endhedron %}
```

The body becomes the component's default `body` slot when that slot exists; otherwise it becomes
the component's children. A body containing only template whitespace counts as empty unless the
component explicitly opts into whitespace-preserving children.

### Named slots

```jinja
{% hedron "Card" title=view.title with body %}
  <p>{{ view.summary }}</p>

  {% slot "footer" %}
    {% hedron "AccountMenu" account_id=view.account_id %}
  {% endslot %}
{% endhedron %}
```

Slot names are string literals. A `slot` tag is valid only as a direct child of a block `hedron`
tag. Nested control flow may occur inside a slot, but a condition may not create or rename the slot
itself. Unknown slots, duplicate single-cardinality slots, missing required slots, named slots on
an inline tag, and `slot` outside `hedron` are errors. A `many` slot may be repeated and preserves
source order.

Rendered template bodies and slots are represented internally as provenance-carrying template
fragments. They are not passed through a public `TrustedHtml` constructor and are not exposed as a
general way to bless arbitrary strings. Nested Hedron tags preserve their render metadata instead
of becoming opaque markup.

### Jinja composition

Standard `{% extends %}`, `{% block %}`, `{% include %}`, `{% import %}`, `{% macro %}`, `{% if %}`,
and `{% for %}` behavior belongs to Jinja. Hedron adds no parallel equivalents. Include and extends
names must be static in strict mode so the build can inventory the dependency graph. Dynamic
template loading remains available only when `strict=False` and is classified experimental.

Macros return Jinja markup, not Hedron components. A macro may contain `hedron` tags, but it cannot
be registered as a component factory or bypass the allowlist.

### Deliberately omitted syntax

The first version has no template-level Python import, component import, dynamic component name,
spread props, arbitrary raw tag, `render_component()` global, or special HDN compatibility syntax.
These omissions keep dependency analysis, diagnostics, and the security boundary understandable.

## Component binding and validation

At bind time Hedron creates a `ComponentBinding` for each alias. The binding contains:

- the alias and stable component logical ID;
- the factory and declared `Props` model or explicit callable schema;
- allowed, required, defaulted, secret, identity, and deprecated prop metadata;
- named slot cardinalities;
- declared styles, assets, browser modules, and interaction capabilities; and
- source/package provenance for diagnostics.

The template checker validates static facts: alias existence, prop names, required props, reserved
names, slot names and cardinalities, literal value compatibility, static include dependencies,
and typed `view.field` paths. General Jinja expression types cannot always be proven statically.
Every invocation therefore validates the evaluated values through the binding's props contract at
runtime before construction. Static success never disables runtime validation.

Factories receive only validated props and structured child/slot values. They do not receive the
Jinja context, environment, loader, render session, raw request, or arbitrary registry unless their
normal Python construction contract explicitly contains an approved value.

## View models and template context

Typed view models should contain presentation-ready values. Database access, authorization,
network I/O, derived business rules, and unbounded iteration happen before rendering.

Strict mode exposes:

- `view`: the supplied model or mapping;
- `hedron_trusted`: a filter accepting only `TrustedHtml`;
- `hedron_url`: a filter accepting only a purpose-compatible `SafeUrl`;
- documented pure formatting filters; and
- application globals explicitly installed before `HedronJinja` freezes the environment.

It does not implicitly expose `request`, `session`, dependency containers, settings, environment
variables, Python builtins, the component registry, or framework globals. Framework integrations
may add documented, redacted proxy values, but raw request/session objects are not part of this RFC.

`Secret` values fail before string conversion. Undefined access fails with `StrictUndefined` in
strict mode. Application filters and tests are trusted Python code and remain subject to the rule
that rendering performs no hidden I/O.

## Render lifecycle and metadata

Each render creates an isolated `JinjaRenderSession`:

1. Resolve and canonicalize the template name through its configured source loader.
2. Validate the supplied view against the `TemplateSpec` contract.
3. Create a Hedron render context and empty metadata accumulator.
4. Execute Jinja with the internal session token and public `view` value.
5. For each `hedron` tag, resolve its immutable binding, validate props and slots, construct the
   component, and call `hedron_core.render(..., mode=FRAGMENT)` with the same context.
6. Insert only the returned HTML as internally marked template output, while merging assets,
   approved headers, identity entries, diagnostics, and redacted traces into the session.
7. Validate page or fragment output policy and return one immutable `RenderResult`.

Calling a Hedron tag outside a `HedronJinja.render()` session fails closed. Direct
`environment.get_template(...).render(...)` remains ordinary Jinja and cannot use Hedron tags,
because returning a bare string would silently lose metadata.

Nested assets are deduplicated by canonical asset identity while preserving first-use order.
Conflicting definitions for the same identity fail. Approved headers merge through Hedron's header
policy; a conflict fails rather than choosing the last value. Identity-map collisions fail.
Diagnostics retain both the Jinja source span and nested component path. Secret and raw context
values never enter traces.

For `RenderMode.PAGE`, the template owns the complete document and must emit one HTML document with
a doctype, one `html`, one `head`, and one `body`. Hedron does not wrap a page template in another
document. For `FRAGMENT`, document-level elements are rejected in strict mode.

## Escaping and markup policy

HTML autoescape is mandatory in strict mode. Literal template markup is trusted application source;
expression values are escaped by Jinja. Hedron component HTML is inserted only from a successful
Hedron `RenderResult` and is marked safe internally.

The built-in Jinja `safe` filter is rejected by the Hedron checker in strict mode. Trusted markup
must be a `TrustedHtml` value and use `|hedron_trusted`; the filter rejects strings and other types.
This makes trust visible in the Python type and at the template use site.

HTML escaping does not make URLs, CSS, JavaScript, `srcdoc`, or event attributes safe. Strict checks
therefore require:

- dynamic `href`, `src`, `action`, `formaction`, and equivalent URL attributes to use a compatible
  `SafeUrl` through `|hedron_url`;
- no dynamic `style`, `srcdoc`, `on*` event attribute, tag name, or attribute name;
- no JavaScript URL assembled from template strings; and
- CSP-compatible external scripts and styles registered through Hedron assets.

Applications may opt out of individual checks only through named configuration and retained build
evidence. `strict=False` is an application trust decision and is never the generated-project
default.

## Template trust boundary

Jinja templates execute application presentation logic. Anyone who can modify trusted templates
is treated like someone who can modify application Python. Templates loaded from user input,
tenant storage, CMS fields, LLM output, uploaded archives, remote repositories, or database rows are
unsupported even when `SandboxedEnvironment` is used.

Hedron supports Jinja's `SandboxedEnvironment` as defense in depth for trusted templates with a
reduced context. It does not claim containment of hostile authors, because exposed objects,
callables, filters, resource use, loader behavior, and Jinja vulnerabilities remain relevant.

The component allowlist is an exposure boundary, not authorization. Components and actions enforce
normal application authorization before rendering or mutation. A template cannot make a private
component addressable or an action callable merely by naming it.

## Resource limits

The Jinja render session shares Hedron's configured limits and adds:

- maximum template include/extends depth;
- maximum macro recursion depth;
- maximum loop iterations per loop and per render;
- maximum component invocations;
- maximum emitted characters;
- maximum accumulated assets, headers, diagnostics, and trace entries; and
- optional wall-clock observation for diagnostics and operations budgets.

Jinja does not provide a complete instruction budget. Applications must pass bounded, materialized
collections in view models; arbitrary iterators and lazy query objects are rejected. The checker
flags loops over untyped or unbounded values. Limits fail with diagnostics and produce no partial
response. A wall-clock deadline is observability and cancellation support, not a substitute for
structural limits.

## Loaders, packages, and dependency inventory

Application and installed-package templates occupy separate loader namespaces. Package templates
must be declared in plugin metadata and are addressed by a stable package prefix. Application
overrides are explicit; loader precedence never silently shadows a package template.

Strict templates use static names for extends, include, import, and from-import. `hedron check`
walks this graph, detects cycles and missing dependencies, records source digests, and reports every
component alias used by each template. The production build manifest records:

- template logical ID, source kind, canonical name, and digest;
- static template dependencies;
- referenced component logical IDs and contract digests;
- view-model contract digest when declared;
- strict-policy version and relevant configuration; and
- Jinja, MarkupSafe, Hedron, and artifact format versions.

The manifest contains no source text, secrets, filesystem roots, or serialized live objects.
Production may use Jinja's bytecode cache or precompilation, but compiled Python bytecode is a local
cache, not Hedron's portable public artifact. Missing or stale dependencies fail the production
build/startup policy already used by Hedron manifests.

## Framework integration

The framework-neutral integration returns `RenderResult`. Framework adapters remain responsible
for status codes, encoding, cookies, approved headers, streaming policy, and response construction.

- FastAPI: `hedron` provides a response helper/decorator path that accepts a `RenderResult` from
  `HedronJinja`; request dependencies prepare the typed view model.
- Flask: `hedron-flask` binds `app.jinja_env` during `init_app` and provides a response adapter. It
  does not replace Flask's loader or global template configuration.
- Django: `hedron-django` binds a named Jinja2 backend. Django Template Language is unaffected and
  receives no Hedron tag from this RFC.

All three adapters use the same template fixtures and metadata merge conformance suite. Framework
convenience APIs may be ergonomic wrappers but may not change template semantics.

## Diagnostics

The initial diagnostic family is reserved as follows:

| Code | Meaning |
|---|---|
| `HED-JINJA-0001` | invalid or escaping template name |
| `HED-JINJA-0002` | missing template or static dependency |
| `HED-JINJA-0003` | invalid/duplicate component binding |
| `HED-JINJA-0004` | unknown or dynamic component alias |
| `HED-JINJA-0005` | invalid, missing, or reserved prop |
| `HED-JINJA-0006` | Hedron tag used outside a render session |
| `HED-JINJA-0007` | invalid, duplicate, misplaced, or missing slot |
| `HED-JINJA-0008` | view-model contract failure or undefined field |
| `HED-JINJA-0009` | forbidden raw markup or `safe` filter |
| `HED-JINJA-0010` | unsafe dynamic URL/CSS/script/attribute context |
| `HED-JINJA-0011` | template dependency cycle or dynamic dependency |
| `HED-JINJA-0012` | render resource limit exceeded |
| `HED-JINJA-0013` | metadata conflict or identity collision |
| `HED-JINJA-0014` | incompatible environment or async mode |
| `HED-JINJA-0015` | forbidden iterator, secret, or context value |
| `HED-JINJA-0016` | stale or incompatible build manifest |
| `HED-JINJA-0017` | page/fragment document-shape violation |
| `HED-JINJA-0018` | legacy HDN migration cannot be represented safely |

Diagnostics include template logical ID, canonical source name, line and column span, include/macro
stack, component alias/logical ID when applicable, explanation, remediation, and safe structured
metadata. Text, JSON, SARIF, CLI, and Explorer views use the same diagnostic object.

## Tooling and developer experience

`hedron check` gains Jinja discovery and validation. `hedron dev` watches static template
dependencies and atomically invalidates affected templates. `hedron build` records the production
inventory. Explorer shows template source, dependency graph, component calls, view contract,
policy findings, and render trace subject to its normal source allowlist.

Hedron does not ship a Jinja formatter or language server. It interoperates with established Jinja
editor tooling and publishes the extension tag grammar and diagnostic schema. A future typing
plugin may consume `TemplateSpec` and component metadata, but it is not required for 0.11.

Generated examples use typed `view` models, strict mode, static includes, and explicit component
allowlists. There is always an equivalent pure-Python component path.

## Accessibility implications

Jinja does not change Hedron component accessibility contracts. Static template checks cover the
sound subset: duplicate IDs in static structure, obvious missing labels/landmarks/language/title,
invalid nesting detectable without execution, forbidden positive `tabindex`, and component schema
requirements. They do not claim to prove accessibility.

Representative page and fragment fixtures must pass keyboard, focus, screen-reader semantics,
status/error announcement, reduced-motion, contrast, zoom/reflow, and non-JavaScript evidence. A
component rendered through Jinja must have the same observable accessibility behavior as direct
Python rendering.

## Performance implications

The package adds no cost when it is not installed. Benchmarks separate template load/compile,
warm render, Jinja expression work, Hedron component rendering, and metadata merging.

For the accepted representative fixtures:

- installing the extension must add no more than the greater of 10% or 100 microseconds to a warm
  template with no Hedron tags compared with the same bound Jinja environment;
- each Hedron tag path is compared with direct `hedron_core.render()` plus equivalent HTML
  placement, with a release threshold recorded before implementation and no hidden I/O;
- dependency checks and incremental invalidation scale with the affected static graph, not every
  template in the project; and
- resource-limit failures are measured for maximum nesting, loops, component count, and output.

Cold-start, memory, artifact, and installed-size budgets are recorded in the phase 0.9 evidence
ledger. Regressions require a documented budget decision rather than relaxed tests.

## Security implications

Security depends on four explicit boundaries:

1. Template authors are trusted application-code authors.
2. View values are typed, bounded, presentation-ready data without raw request/session objects.
3. Component availability is an immutable local allowlist; authorization remains in Python.
4. HTML/URL/trusted-content output follows strict contextual policies and the existing Hedron
   security types.

Adversarial tests cover loader traversal, malicious names, undefined values, secret conversion,
attribute/call access, unsafe Markup producers, `safe`, URL schemes, event/style/srcdoc contexts,
include cycles, recursive macros, huge loops/output, malicious component factories, metadata
conflicts, stale manifests, exception redaction, and concurrent session isolation.

No security claim relies solely on Jinja sandboxing or autoescape.

## Testing strategy

- Parser tests for all extension forms, whitespace control, nesting, and source spans.
- Golden templates for inheritance, includes, macros, loops, inline components, bodies, and slots.
- Component binding tests against required/defaulted/invalid/secret props and slot cardinality.
- Typed-view static checks and runtime validation tests.
- Observable-output and metadata parity against direct Python component rendering.
- FastAPI, Flask, and Django adapter conformance using the same fixtures.
- Strict escaping, trusted HTML, safe URL, CSP, and adversarial suites.
- Concurrency tests proving render sessions and metadata do not leak across requests.
- Resource-limit, performance, bytecode-cache, production-manifest, wheel-install, and offline tests.
- Manual rewrite fixtures covering representative 0.8 semantics without executing HDN source.
- Python 3.11–3.14 and the documented Jinja/MarkupSafe compatibility matrix.

## HDN removal boundary

D-041 rejects a dual-runtime migration period. Phase 0.9 deletes HDN source discovery, parser,
expression evaluator, formatter, `RenderProgram`, compiled artifacts, manifest fields, public APIs,
CLI and Explorer integration, reference examples, and tests. There is no `migrate hdn` command,
compatibility setting, legacy package, or automatic syntax translation.

Applications with HDN remain on the 0.8 line until their templates are manually rewritten as typed
Python components or Jinja templates. Upgrade documentation provides a semantic rewrite table but
does not execute old HDN source inside a 0.9 process. The build-manifest format is bumped so old
artifacts fail closed.

## Alternatives considered

### Python only

Python remains the baseline and is sufficient for many applications. It was not chosen as the only
surface because Jinja provides familiar HTML-first composition, inheritance, includes, macros, and
collaboration workflows without Hedron owning another language. Applications incur no Jinja cost
unless they opt in.

### A smaller custom layout language

A custom language could provide stronger static typing and a closed value model, but Hedron would
again own parsing, semantics, editor tooling, security review, migrations, and user education. The
current evidence does not justify that permanent cost.

### Continue HDN

The current Python-AST evaluator, custom HTML-like parser, flat render program, and incomplete
component schema integration do not provide a sound foundation. Preserving them would optimize for
experimental implementation compatibility rather than user value.

### Use framework-native template integrations only

Flask and Django already expose Jinja integrations, but a thin framework-only helper would not
preserve Hedron component metadata or provide one component tag, strict policy, checker, migration,
and cross-framework conformance contract.

### Sandboxed user-authored templates

This would be a different product with a hostile-code execution threat model, stronger isolation,
capability-safe values, and hard CPU/memory containment. It is explicitly out of scope.

## Resolved design questions

- **Is Jinja required?** No; it is an optional package and extra.
- **Are templates trusted?** Yes, at the same level as application presentation code.
- **Can templates name components dynamically?** No.
- **Can all props be statically typed?** No; sound static facts are checked and runtime props
  validation is mandatory.
- **How is nested metadata preserved?** One explicit render session merges complete nested
  `RenderResult` metadata.
- **Can direct Jinja rendering use Hedron tags?** No; it fails because metadata would be lost.
- **Does Jinja replace Python components?** No.
- **Does the extension expose request/session objects?** No implicit exposure.
- **Does SandboxedEnvironment permit untrusted authors?** No.
- **Does Jinja output become a reusable `Component.render()` string?** No; adapters consume the
  integration's `RenderResult`.
- **Does HDN syntax survive?** No. Version 0.9 contains no HDN parser or compatibility syntax.

## Acceptance criteria

The phase 0.9 implementation is complete only when:

- `hedron-jinja` installs independently and the default/core distributions have no Jinja import or
  dependency;
- the public API, tag grammar, strict policy, diagnostics, manifest, and migration behavior match
  this RFC and their API specifications;
- all nested `RenderResult` fields merge deterministically with conflict tests;
- typed view, component prop, slot, loader, context, escaping, URL, trusted HTML, CSP, resource,
  concurrency, and redaction gates pass;
- FastAPI, Flask, and Django Jinja paths pass shared conformance fixtures;
- three representative applications are published in Python-only and Jinja forms, including a
  semantic card, an accessible form/error flow, and a repeated data/status view;
- a Python-first author and an HTML-oriented author complete the representative tasks, with findings
  recorded as evidence rather than used to weaken safety gates;
- build/check/dev/Explorer integration, production manifest validation, published-wheel install,
  offline startup, compatibility matrix, and performance budgets pass;
- repository inventory proves no first-party HDN runtime, artifact, discovery, public API, example,
  or test remains; and
- documentation teaches the trust boundary and pure-Python alternative before advanced escape
  hatches.

Promotion from experimental to beta occurs no earlier than phase 0.12 and requires real-application
evidence plus closure of all critical and high-severity security findings.
