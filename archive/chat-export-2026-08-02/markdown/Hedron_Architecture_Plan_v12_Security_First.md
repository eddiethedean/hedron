**HEDRON**

**Architecture, Adoption, and Security Plan**

*Version 12 - Security-First Revision*

Python-first \| FastAPI-first \| HTMX-native \| Component-oriented

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr>
<th><strong>Core proposition<br />
</strong>JSON endpoints return models. HTML endpoints return components. Hedron turns typed server components into first-class HTTP resources while keeping every automatic behavior inspectable and secure by default.</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# Executive Summary

Hedron is a Python-first framework for building component-oriented HTML and HTMX applications. The default distribution, hedron, provides a batteries-included FastAPI experience. A framework-neutral hedron-core package supports dedicated hedron-flask and hedron-django adapters without installing FastAPI.

Security is not a separate middleware chapter. It is a cross-cutting design constraint applied to models, rendering, routes, actions, forms, OpenAPI, the Component Explorer, scoped styles, asset handling, caching, and adapter behavior.

- New users begin with built-in Python components and typed Hedron models; HDN is optional until fine-grained markup control is needed.

- Addressable components become explicit HTTP resources that naturally align with HTMX requests and fragment replacement.

- Hedron() automatically converts returned component objects into HTML responses; plain FastAPI applications use an explicit HTML(...) wrapper.

- OpenAPI remains authoritative for HTTP semantics, while x-hedron-\* extensions and the Component Explorer describe component semantics.

- Hedron Scoped Styles provide server-side CSS Modules-style isolation without Node.js or a browser styling runtime.

- Secure defaults include context-aware escaping, explicit trusted HTML, URL validation, CSRF protection, explicit endpoint exposure, secret redaction, private caching defaults, and development-only Explorer access.

# 1. Product Vision and Positioning

## 1.1 Focused initial market

Hedron should first win one audience: Python developers building FastAPI interfaces who want modern component composition without a Node.js toolchain. Flask and Django support remain intentional, first-class adapter paths, but FastAPI is the flagship onboarding story.

## 1.2 Distinctive idea

React makes components the unit of composition. HTMX makes endpoints the unit of interaction. Hedron unifies the two by making addressable components typed HTTP resources.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr>
<th><strong>Product identity<br />
</strong>Hedron is not "React in Python." It is a server-native component framework that embraces HTML, HTTP, FastAPI, and HTMX while borrowing only the component ideas that naturally fit.</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 1.3 Security-first product promise

- Automate security mechanics when the secure interpretation is unambiguous.

- Never infer authorization, trust, or business intent.

- Make route exposure and automatic HTMX behavior inspectable.

- Prefer explicit trusted types over unsafe flags.

- Fail early at model definition, component compilation, or startup.

- Provide build-time and Explorer security diagnostics.

# 2. Packaging and Dependency Architecture

| **Distribution** | **Purpose** | **Dependencies** |
|----|----|----|
| hedron | Batteries-included FastAPI integration | hedron-core, FastAPI, Starlette |
| hedron-core | Framework-neutral components, models, rendering, HDN, HTMX metadata, styles | Pydantic and minimal framework-neutral dependencies |
| hedron-flask | Complete Flask adapter and re-exported component API | hedron-core, Flask |
| hedron-django | Complete Django adapter and re-exported component API | hedron-core, Django |

## 2.1 Import experience

\# FastAPI-first  
from hedron import Hedron, Page, Card, Props  
  
\# Flask  
from hedron_flask import HedronFlask, Page, Card, Props  
  
\# Django  
from hedron_django import page, Page, Card, Props

## 2.2 Dependency boundary

hedron-core must not import FastAPI, Flask, Django, ASGI, or WSGI types. Adapters translate framework-native requests and responses into a small Hedron protocol. This keeps security semantics consistent across integrations while allowing each adapter to preserve its framework-native authentication, CSRF, session, and middleware systems.

# 3. Beginner-First Development Experience

## 3.1 Progressive disclosure

- Level 1: use built-in components and return them from endpoints.

- Level 2: configure props, variants, layouts, actions, and slots.

- Level 3: compose reusable Python components.

- Level 4: override or author HDN templates.

- Level 5: add Web Components, compiler extensions, and advanced asset behavior.

from hedron import Hedron, Page, Card, Button  
  
app = Hedron()  
  
@app.page('/')  
def home() -\> Page:  
return Page(  
title='Welcome',  
children=\[  
Card(  
title='Users',  
children=\[Button('Load users', target=UserTable())\],  
)  
\],  
)

## 3.2 Automatic but explainable behavior

- Full document for ordinary navigation; component fragment for HX-Request.

- Return annotations define HTML response contracts.

- Addressable component references replace manually written endpoint strings.

- Stable component identity supports self-targeting, testing, and diagnostics.

- Typed actions infer method, route, and mechanics but never permission decisions.

- All inferred behavior is visible in the Component Explorer.

# 4. Hedron Model System

Users import Hedron-owned model types. Pydantic is the initial implementation mechanism, not the public contract.

from hedron import Model, Props, FormModel, Field, Secret  
  
class User(Model):  
id: int  
name: str  
  
class UserCardProps(Props):  
user: User  
compact: bool = False  
  
class LoginForm(FormModel):  
username: str  
password: Secret = Field(autocomplete='current-password')

## 4.1 Supported subset

- Portable primitive, collection, enum, literal, optional, and nested Hedron model types.

- Hedron-owned constraints and Field options only.

- Unsupported arbitrary types, callbacks, mutable framework objects, or custom serialization fail at class creation.

- Props and endpoint inputs are intentionally distinct; internal props are never automatically exposed as client-controlled parameters.

## 4.2 Security semantics

- Secret fields are redacted from repr, logs, Explorer panels, examples, identity hashes, and error echoes.

- Raw HTML uses TrustedHtml, never str.

- URL-bearing fields use validated SafeUrl or equivalent context-specific conversion.

- Custom validators are initially restricted because arbitrary Python validation is not portable or statically inspectable.

- Extra fields are forbidden by default to reduce mass-assignment risk.

# 5. Component Model

## 5.1 Renderable components

Renderable components are ordinary reusable composition primitives. They have no endpoint unless explicitly promoted to an addressable resource.

## 5.2 Addressable components

Addressable components are renderable components with explicit HTTP resource definitions. They can be independently requested, refreshed, lazy-loaded, polled, cached, previewed, and tested.

from hedron import addressable, Depends  
  
@addressable(  
dependencies=\[Depends(require_user)\],  
cache='private-no-store',  
)  
def user_table(  
team_id: int,  
service: UserService = Depends(get_user_service),  
) -\> UserTable:  
return UserTable(rows=service.list(team_id))

## 5.3 Security rules for addressability

- Addressability is always explicit; discovery never exposes every component by default.

- Endpoint inputs come from the factory signature, not from every component prop.

- Authorization dependencies must be explicit or unambiguously inherited.

- Hedron warns when a component is rendered from routes with conflicting security contexts.

- Authenticated component responses default to Cache-Control: private, no-store.

- Generated component URLs use registry identifiers, never request-controlled filesystem paths.

# 6. FastAPI Integration

## 6.1 Hedron application mode

app = Hedron()  
  
@app.get('/users/{user_id}')  
def user_card(user_id: int) -\> UserCard:  
return UserCard(user=get_user(user_id))

Hedron recognizes the component annotation and returned value, validates the declared HTML contract, renders the component, sets text/html, and preserves FastAPI dependency injection and error behavior.

## 6.2 Plain FastAPI mode

app = FastAPI()  
  
@app.get('/users/{user_id}', \*\*hedron_response(UserCard))  
def user_card(user_id: int):  
return HTML(UserCard(user=get_user(user_id)))

Explicit wrapping avoids monkey-patching FastAPI and enables incremental adoption. Plain FastAPI users can opt into accurate OpenAPI documentation through hedron_response(...).

## 6.3 Security integration

- FastAPI Depends and Security remain authoritative for authentication and authorization.

- Unsafe methods receive CSRF enforcement when cookie-authenticated Hedron actions are used.

- Hedron never turns GET into a mutation mechanism.

- Explicit Response objects and redirects pass through unchanged, subject to safe redirect helpers where user-controlled destinations are involved.

- Return-type mismatches produce component-aware diagnostics without exposing sensitive values.

# 7. HTMX-Native Interaction Model

## 7.1 Component references instead of URL strings

Button(  
'Refresh',  
target=UserTable(team_id=team.id),  
)

Hedron resolves the addressable component, validates parameters, generates the route, target, and swap semantics, and records the inference for the Explorer.

## 7.2 Self-refreshing components

- RefreshButton() inside an addressable component targets the owning component automatically.

- lazy=True compiles to a safe load-triggered component request.

- poll="5s" compiles to periodic retrieval without exposing arbitrary URLs.

- Infinite-scroll and pagination helpers bind to typed component inputs.

## 7.3 HTMX security

- Unsafe methods include CSRF tokens and validate Origin/Referer according to policy.

- Untrusted values cannot control arbitrary hx-\* names or raw attribute dictionaries.

- History caching can be disabled on sensitive pages and components.

- Automatic targets are constrained to stable component identities, reducing selector injection risk.

- Action bindings serialize only public route parameters, never dependency objects or authorization decisions.

# 8. HDN Template Language

HDN is an advanced, JSX-inspired template language that remains HTML-first and server-native. Hedron borrows only conventions that naturally fit its architecture.

\<article class={styles.root}\>  
\<h2\>{props.user.name}\</h2\>  
  
{props.user.isAdmin && (  
\<Badge variant='warning'\>Admin\</Badge\>  
)}  
  
\<Button action={deleteUser(userId=props.user.id)}\>  
Delete  
\</Button\>  
\</article\>

## 8.1 Security by construction

- Expressions are escaped according to HTML text, attribute, URL, CSS, or JSON context.

- Arbitrary JavaScript execution is not supported.

- Raw HTML requires TrustedHtml and an explicit rendering operation.

- Dynamic attribute names are rejected by default.

- Includes and component references resolve only through the prebuilt registry.

- Compiler diagnostics identify unsafe raw HTML, URL schemes, dynamic HTMX attributes, and secret-value rendering.

# 9. Forms and Typed Actions

## 9.1 Automatic forms

class CreateUser(FormModel):  
name: str  
email: Email  
role: Literal\['admin', 'member'\] = 'member'  
  
Form(CreateUser, submit=create_user)

- Generate labels, controls, required state, help text, and accessible error associations.

- Preserve submitted non-secret values on validation failure.

- Never place secrets in query strings or diagnostics.

- Use POST for mutation forms and include CSRF tokens automatically.

- Constrain file size, accepted content types, and upload handling through explicit field metadata.

## 9.2 Typed actions

- Action functions declare method, route, input contract, dependencies, and return component.

- Component bindings generate route-safe URLs and validated parameters.

- Destructive labels never determine HTTP methods or confirmation behavior.

- Signed parameters, if added later, supplement but never replace authorization.

- LocalRedirect rejects untrusted external destinations; ExternalRedirect is explicit.

# 10. OpenAPI and Documentation

FastAPI OpenAPI remains the source of truth for HTTP semantics. Hedron adds component semantics without misrepresenting HTML as JSON.

- Component responses are documented as text/html with string schemas.

- Component annotations disable ordinary JSON response-model handling for that route.

- x-hedron-\* extensions describe component identity, addressability, props schema, render modes, HTMX defaults, and preview URLs.

- Auto-generated internal component resources are hidden from Swagger by default.

- Public pages and explicitly public component endpoints may appear under Pages, Components, or Actions tags.

- Secret fields and internal source paths never appear in production documentation.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr>
<th><strong>Documentation split<br />
</strong>Swagger/ReDoc documents HTTP. Hedron Explorer documents components, rendering, HTMX, styles, and diagnostics.</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 11. Hedron Component Explorer

The Explorer is the development control center and the primary mechanism for making Hedron automation transparent.

## 11.1 Primary areas

- Components, Pages, Actions, Routes, Diagnostics, Security, and Settings.

- Live preview with editable props and named examples.

- Addressable endpoint request simulator with headers, status, timing, and rendered HTML.

- HTMX inspector showing generated attributes and the reason each was inferred.

- Component graph, inverse usage graph, source locations, templates, styles, and render traces.

- Accessibility and security diagnostics with actionable remediation.

## 11.2 Explorer security

- Disabled and unregistered outside development by default.

- Production enablement requires explicit configuration and authentication dependencies.

- Redact Authorization, cookies, secrets, local paths, and sensitive model fields.

- Disable mutation simulation by default in production; enforce CSRF and audit all enabled mutations.

- Prevent arbitrary modules, paths, headers, and URLs from being supplied through Explorer controls.

- Rate-limit request simulation and separate Explorer authorization from ordinary application roles.

## 11.3 Security panel

- Raw HTML and trusted-value usage.

- Mutations without CSRF.

- Addressable resources without explicit authorization.

- Unsafe URL schemes and redirects.

- Public caching of authenticated fragments.

- Sensitive content with HTMX history enabled.

- Inline scripts/styles under strict CSP.

- Explorer exposure and security-header configuration.

- Dynamic attributes and raw HTMX configuration.

# 12. Hedron Scoped Styles

Hedron Scoped Styles provide CSS Modules-style isolation without Node.js or a browser-side CSS-in-JS runtime.

UserCard/  
├── component.py  
├── template.hdn  
├── styles.css  
└── examples.py  
  
\# template.hdn  
\<article class={styles.root}\>  
\<h2 class={styles.title}\>{props.user.name}\</h2\>  
\</article\>

- Local class and keyframe names are rewritten to deterministic collision-free names.

- HDN and Python components use typed styles.name references.

- Global selectors require explicit :global(...).

- CSS variables provide themes and dynamic tokens; semantic variants are preferred over arbitrary prop-to-CSS generation.

- An application bundle is the MVP delivery strategy; route splitting and dynamic HTMX asset negotiation come later.

- Relative assets are fingerprinted and constrained to registered roots.

## 12.1 Style security

- Reject path traversal outside component or package asset roots.

- Do not fetch remote assets during compilation by default.

- Disallow user-controlled raw CSS and unsafe style attribute generation in strict mode.

- Treat third-party CSS and browser JavaScript as executable browser content.

- Prefer external fingerprinted stylesheets for CSP compatibility.

- Allow strict policy to reject inline styles, remote fonts, and unapproved external resources.

# 13. Browser Components and Assets

- Web Components own rich local browser behavior; Hedron and HTMX own server structure and interaction.

- Light DOM is preferred when HTMX needs to target descendants; Shadow DOM is used for isolated widgets.

- Browser modules are registered explicitly, fingerprinted, and served as external assets.

- No arbitrary inline event handlers are generated.

- Component packages declaring browser JavaScript are surfaced clearly in audit and Explorer metadata.

- Content Security Policy compatibility is a release requirement.

# 14. Security Headers and Browser Policy

- Content-Security-Policy with strict external-asset defaults.

- frame-ancestors for clickjacking defense.

- X-Content-Type-Options: nosniff.

- Referrer-Policy and Permissions-Policy.

- Optional COOP and COEP profiles for applications that need them.

- No automatic weakening of framework or proxy security headers.

app = Hedron(  
security=SecurityConfig.strict(),  
)

# 15. Caching, Identity, and Sensitive Content

- Authenticated fragments default to private, no-store.

- Public caching must be explicit and include all declared vary dimensions.

- Hedron warns when authentication dependencies coexist with public caching.

- Secret values never participate in component IDs or cache keys.

- Sensitive pages can disable HTMX history snapshots automatically.

- Component identity is deterministic but must not expose secrets or raw serialized props.

# 16. Adapter Security

## 16.1 FastAPI

- Preserve Depends, Security, OAuth2 scopes, sessions, and middleware behavior.

- Hedron CSRF applies only where FastAPI lacks an authoritative application mechanism and cookie authentication makes it necessary.

## 16.2 Flask

- Integrate Flask request context, sessions, blueprints, url_for, and selected CSRF solution.

- Do not silently introduce FastAPI or Starlette behavior.

## 16.3 Django

- Django middleware, CSRF, authentication, permissions, forms, and URL reversing remain authoritative.

- Hedron adapts component rendering and metadata around those systems rather than replacing them.

# 17. Component Packages and Supply Chain

Third-party Hedron packages can contain Python, HDN, CSS, browser JavaScript, assets, and Explorer plugins. Installing one is equivalent to installing executable application code.

hedron audit-components

- Report package capabilities and browser assets.

- Identify raw HTML usage, dynamic attributes, remote assets, and Explorer plugins.

- Integrate with standard Python dependency and vulnerability scanners rather than replacing them.

- Do not promise sandboxing of installed Python packages.

# 18. Diagnostics, CI, and Security Modes

## 18.1 Build-time checks

hedron check --security --fail-on warning --format sarif

- Analyze route metadata, HDN ASTs, model schemas, scoped CSS, assets, OpenAPI extensions, and Explorer configuration.

- Support text, JSON, and SARIF output.

- Use stable diagnostic codes and remediation guidance.

- Permit explicit suppressions with justification and source location.

## 18.2 Security profiles

| **Profile** | **Defaults** | **Use case** |
|----|----|----|
| development | Local Explorer, detailed diagnostics, safe debug metadata, relaxed development asset rules | Local development only |
| standard | Escaping, CSRF, secure headers, explicit exposure, private authenticated caching, Explorer disabled | General production applications |
| strict | No unsafe raw HTML, no inline script/style, no remote assets, warnings fail builds, explicit routes and schemes | Government and high-assurance environments |

# 19. Automatic Behaviors and Their Security Constraints

| **Automatic behavior** | **Secure inference** | **Never infer** |
|----|----|----|
| Component response rendering | Escape by context and emit text/html | Trust or authorization |
| Addressable routes | Register explicitly declared resources | Public exposure from mere usage |
| Typed actions | Method, route, CSRF mechanics, target | Permission or destructive confirmation |
| Forms | Control type, labels, constraints, error association | Business validation or authorization |
| Caching | Private no-store for authenticated resources | Public cache safety |
| Styles | Local class rewriting and asset fingerprinting | Design intent or safe remote content |
| Explorer | Display registry and inference reasons | Production exposure or secret visibility |

# 20. Implementation Roadmap

## Phase 1 - Secure beginner experience

- Hedron() FastAPI subclass and explicit plain-FastAPI HTML wrapper.

- Core component tree and context-aware escaping.

- Props, Model, FormModel, Field, Secret, TrustedHtml, SafeUrl.

- Explicit addressable components with dependency preservation.

- CSRF, secure headers, private caching defaults, and filesystem-safe assets.

- Basic Explorer registry, preview, and security diagnostics.

## Phase 2 - Typed interactions

- Typed actions and component references.

- AutoForm and validation fragments.

- OpenAPI component metadata.

- HTMX inspector and request simulator.

- Component-aware testing helpers.

## Phase 3 - HDN and Scoped Styles

- HDN parser, AST, compiler, source diagnostics, and trusted-value checks.

- Scoped class/keyframe compiler, application bundle, asset manifests, and Explorer Styles panel.

- Strict CSP support and build-time checks.

## Phase 4 - Ecosystem and adapters

- Flask and Django adapters with framework-native security conformance tests.

- Component package audits and design-system support.

- React migration analysis and guided conversion.

## Phase 5 - Measured optimization

- Profile parser, renderer, escaping, and style compilation.

- Introduce optional Rust acceleration only for proven bottlenecks while preserving pure-Python behavior and security semantics.

# 21. MVP Non-Goals

- No custom authentication framework.

- No Hedron-maintained cryptographic primitives or HTML sanitizer.

- No automatic authorization inference.

- No universal React application transpilation.

- No browser-side virtual DOM or hydration model.

- No automatic public exposure of every component.

- No Rust core before profiling demonstrates a need.

- No arbitrary CSS-in-Python or runtime CSS injection as the default.

# 22. Acceptance Criteria

- A new developer can install hedron, return a component from a typed FastAPI endpoint, and receive a secure HTML response without learning HDN.

- Ordinary user strings cannot become executable HTML, unsafe URLs, HTMX attributes, CSS, or JavaScript by accident.

- An addressable component cannot become public without explicit exposure and a defined security context.

- Cookie-authenticated unsafe HTMX actions are CSRF-protected by default.

- Explorer routes are absent in production unless explicitly and securely enabled.

- OpenAPI accurately documents text/html while preserving FastAPI input and security documentation.

- Scoped styles cannot escape asset roots or require a Node.js build tool.

- All automatic behavior is visible in the Explorer or CLI and can be overridden explicitly.

- Security checks can run in CI and emit stable machine-readable diagnostics.

# 23. Final Design Principles

**1. Secure by default, explicit when dangerous.**

**2. Infer mechanics, never trust or authorization.**

**3. Components are typed rendering contracts and, when explicit, HTTP resources.**

**4. FastAPI is the flagship experience; hedron-core remains framework-neutral.**

**5. Progressive disclosure is a product requirement, not a documentation preference.**

**6. HTML, HTTP, CSS, and browser standards remain visible rather than hidden.**

**7. Every piece of framework magic must be inspectable.**

**8. Native acceleration is optional and evidence-driven.**
