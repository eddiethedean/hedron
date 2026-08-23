# Glossary

**Region** — A named, replaceable part of a page (`app.region("service-status")`). Its
HTML `id` stays stable so HTMX can swap it.

**Swap** — Replacing that region's HTML with a fragment the server returned.

**Pin** — An install constraint with an upper bound, for example `hedron>=0.59.0,<0.60`.
Use the pin the package index can resolve.

**Train** — A minor version line (`0.46.x`). Compatible patches stay inside the pin;
the next train is an intentional upgrade.

**Published** — A cut available on the current train (`v0.59.0` on PyPI). Pin the matching
upper-bounded install constraint.

**Action** — A typed server operation with an HTTP method, input contract, dependencies, and response behavior.

**Addressable component** — A component factory explicitly registered as an HTTP resource. It may be loaded, refreshed, polled, cached, previewed, and tested independently.

**Addressable declaration** — Reusable component metadata created with `@addressable`; it becomes reachable only when a router or application explicitly includes it at a path.

**Auto** — The intelligent rendering entry point that selects a component for a supported Python value through the renderer registry.

**Component** — A typed, reusable unit that produces a Hedron node tree or render result.

**Component Explorer** — Development interface for components, routes, examples, HTMX inference, styles, assets, security, accessibility, and performance traces.

**Component identity** — A deterministic non-secret identifier used for targets, diagnostics, tests, and registry references. It is not an authorization token.

**Component registry** — The single metadata source shared by routing, rendering, Explorer, OpenAPI, assets, examples, tests, and diagnostics.

**Data Intelligence Layer** — Inspection logic that describes Python data and recommends or chooses suitable components under explicit policy.

**Fragment** — HTML intended to replace or augment part of a document, normally in response to HTMX.

**HDN** — Hedron's removed experimental template-language prototype. Version 0.8 is the last line
that can execute it; 0.9 has no parser, compatibility flag, converter, or legacy package.

**HDJ (Hedron Jinja)** — Optional phase 0.9 standards-first `.hdj` format for trusted application
templates. A static TOML prologue declares the version, kind, features, and required capabilities;
the body combines native HTML, CSS, JavaScript, Web Components, Jinja, HTMX, and explicit Hedron
bridges while returning a complete `RenderResult`. It is not a Jinja fork, a core dependency, or a
sandbox for hostile authors.

**HedronRoute** — The `APIRoute` subclass that recognizes component contracts and produces Hedron responses and metadata.

**HedronRouter** — The `APIRouter`-based organizational unit for pages, actions, and addressable component resources.

**Page** — A component rendered as a complete HTML document for ordinary navigation and commonly as an appropriate fragment for HTMX navigation.

**NodeLike** — The public recursive value shape accepted by the renderer: component nodes, text, fragments, supported primitives, or sequences of those values.

**Prepared component** — Optional resolved state produced before deterministic tree rendering.

**Renderable component** — A component with no HTTP resource unless separately declared addressable.

**RenderContext** — An immutable framework-neutral rendering context; request adapters derive it without embedding raw request, session, or dependency objects.

**RenderResult** — The immutable framework-neutral result containing a Unicode HTML string plus registered asset, approved header, identity, diagnostic, and optional redacted trace metadata.

**SafeUrl** — An immutable URL validated for a declared purpose and still subject to the final rendering or redirect context policy. URL-bearing HTML attributes (including `srcset`, `ping`, and HTMX URL attrs) require SafeUrl checks.

**Secret** — A typed sensitive value that redacts in public representations; model fields typed as `Secret[T]` validate the inner value against `T`. Application access is explicit via `reveal()`.

**SessionState** — A typed request-scoped facade over the active framework's session, obtained via `session_state(key, annotation)`; it is not a global Hedron state store.

**Scoped styles** — Component-local CSS whose local symbols and keyframes are structurally rewritten to deterministic collision-free identifiers.

**TrustedHtml** — An explicit trusted type accepted by raw HTML rendering. Ordinary strings never imply trust.

**Web Component** — A standards-based custom element used for persistent browser-local behavior such as a data grid or chart runtime.

## Maturity vocabulary

**Train** — A coordinated package version line (for example `0.25.x` / tag `v0.25.0`) that
adopters pin together. “Living train” means the current published line (`0.59.x`).

**Package maturity (Beta / Alpha)** — PyPI packaging readiness. **Beta** flagship packages
are pin-for-production; **Alpha** packages expect more churn. Not the same as capability
readiness or API `stable`.

**Supported** — Capability readiness: works on the current train when pinned. **Not** a
commercial SLA and **not** the same as API compatibility level `stable`.

**Experimental** — Public API shipped; may change; prefer documented fallbacks (for example
polling instead of SSE).

**Deferred** — Documented but not ready; do not market as Supported.

**API compatibility (`stable` / `beta` / …)** — Catalogued in [STABILITY.md](api/STABILITY.md).
Most public symbols remain `beta` on `0.x`.

Canonical snapshot: [What’s ready today](guides/whats-ready.md) · cheat-sheet:
[How to read](getting-started/how-to-read.md).

## Maintainer jargon (rare on adopter pages)

**Disposition** — Locked choice for a release packet (for example live-transport
`polling_only`). Adopters can ignore the word; read [What’s ready](guides/whats-ready.md).

**Gate ID** — Maintainer evidence label such as `DECIDE-024` or `ARCHETYPE-025` in
STATUS / acceptance corpora (GitHub). Not required to use Hedron.

**Packet refine** — Maintainer step that freezes Verified criteria before a cut.

**Waive ledger** — Recorded exception for a browser/perf gate with rationale (acceptance
TOMLs on GitHub).
