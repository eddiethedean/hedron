# Glossary

**Action** — A typed server operation with an HTTP method, input contract, dependencies, and response behavior.

**Addressable component** — A component factory explicitly registered as an HTTP resource. It may be loaded, refreshed, polled, cached, previewed, and tested independently.

**Auto** — The intelligent rendering entry point that selects a component for a supported Python value through the renderer registry.

**Component** — A typed, reusable unit that produces a Hedron node tree or render result.

**Component Explorer** — Development interface for components, routes, examples, HTMX inference, styles, assets, security, accessibility, and performance traces.

**Component identity** — A deterministic non-secret identifier used for targets, diagnostics, tests, and registry references. It is not an authorization token.

**Component registry** — The single metadata source shared by routing, rendering, Explorer, OpenAPI, assets, examples, tests, and diagnostics.

**Data Intelligence Layer** — Inspection logic that describes Python data and recommends or chooses suitable components under explicit policy.

**Fragment** — HTML intended to replace or augment part of a document, normally in response to HTMX.

**HDN** — Hedron’s optional JSX-inspired, HTML-first server template language.

**HedronRoute** — The `APIRoute` subclass that recognizes component contracts and produces Hedron responses and metadata.

**HedronRouter** — The `APIRouter`-based organizational unit for pages, actions, and addressable component resources.

**Page** — A component rendered as a complete HTML document for ordinary navigation and commonly as an appropriate fragment for HTMX navigation.

**Prepared component** — Optional resolved state produced before deterministic tree rendering.

**Renderable component** — A component with no HTTP resource unless separately declared addressable.

**Scoped styles** — Component-local CSS whose local symbols and keyframes are structurally rewritten to deterministic collision-free identifiers.

**TrustedHtml** — An explicit trusted type accepted by raw HTML rendering. Ordinary strings never imply trust.

**Web Component** — A standards-based custom element used for persistent browser-local behavior such as a data grid or chart runtime.

