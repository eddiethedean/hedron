# Hedron Architecture Plan v10

This revision incorporates Hedron's OpenAPI and documentation strategy alongside the existing FastAPI-first architecture.

## Architecture

- Python-first implementation.

- FastAPI is the flagship integration.

- Framework-neutral core with Flask and Django adapters.

- Progressive disclosure from beginner to expert.

## Packaging

- hedron (FastAPI distribution)

- hedron-core (shared engine)

- hedron-flask

- hedron-django

## Core Concepts

- Hedron-owned Props, Model, FormModel and Field.

- Pydantic is an implementation detail.

- Addressable Components become HTTP resources.

- HDN is an advanced customization layer.

## Automatic Framework Behaviors

- Automatic page vs HTMX fragment rendering.

- Automatic component endpoint registration.

- Component references instead of manual HTMX URLs.

- Typed actions.

- Automatic forms and validation rendering.

- Layout inference.

- Component explorer.

- Component-aware testing.

## OpenAPI & Documentation Strategy

Hedron extends FastAPI's documentation instead of replacing it. Standard OpenAPI remains the source of truth for HTTP semantics, while Hedron augments operations with component metadata.

## OpenAPI Principles

- Component responses are always documented as text/html, never JSON.

- FastAPI request parameters, dependencies and request models remain unchanged.

- Component return annotations become HTML response contracts.

- Component metadata is attached through x-hedron-\* OpenAPI extensions.

- Generated component resource endpoints are hidden from Swagger by default but visible in the Hedron Component Explorer.

- All generated documentation remains overridable.

## Hedron Component Explorer

- Separate from Swagger/ReDoc.

- Displays registered components, props, endpoint, preview, generated HTML, HTMX behavior and relationships.

- Consumes the same metadata used to generate OpenAPI extensions.

## FastAPI Integration Modes

Hedron() automatically renders returned components into HTML responses. Existing FastAPI applications explicitly wrap returned components with HTML(...).

## Guiding Philosophy

JSON endpoints return models. HTML endpoints return components. Swagger documents HTTP. Hedron Explorer documents components. Hedron should feel like a natural extension of FastAPI while remaining portable to Flask and Django.

# Hedron Component Explorer

The Hedron Component Explorer is the development control center for Hedron applications. FastAPI Swagger and ReDoc remain focused on HTTP contracts; the Explorer focuses on components as renderable, addressable UI resources. It is generated from the same registry and metadata used by rendering, routing, OpenAPI extensions, diagnostics, and testing.

## Explorer Goals

- Make every registered page, component, action, and addressable resource discoverable.

- Provide isolated component previews without requiring hand-authored stories for basic use cases.

- Make Hedron's inferred behavior visible, explainable, and overridable.

- Combine component inspection with real HTTP and HTMX request testing.

- Reduce onboarding time by teaching the framework through live application metadata.

## Primary Navigation

- Components: renderable and addressable components grouped by application area and origin.

- Pages: page components, public routes, layouts, dependencies, and metadata.

- Actions: typed server actions, HTTP methods, input contracts, return components, and usages.

- Routes: a Hedron-oriented route table covering pages, components, actions, and internal resources.

- Diagnostics: template, routing, accessibility, identity, HTMX, and performance issues.

- Settings: development-only Explorer preferences, discovery paths, themes, and debugging controls.

## Component Detail Workspace

- Preview: isolated live render with viewport, theme, request mode, and state controls.

- Props: generated controls derived from Hedron Props models.

- Examples: named realistic scenarios such as populated, empty, loading, error, and large-data states.

- Request: simulator for invoking the component's actual HTTP resource.

- HTMX: inferred attributes, defaults, target selection, triggers, swaps, and explanation of their sources.

- Source: Python component source, HDN template, source locations, generated HTML, and component metadata.

- Accessibility: static markup checks and future browser-assisted audits.

- Usage: parent components, pages, actions, and routes that reference or return the component.

- Performance: development render timing, output size, child counts, and cache information.

## Prop Controls and Examples

- Strings use text inputs; booleans use checkboxes; numbers use numeric controls.

- Literal and enum values use selects; nested models use structured editors; lists use repeatable inputs.

- Changing props rerenders the preview without requiring a code change.

- Named examples are the source of truth for realistic data and dependency scenarios.

- The Explorer must not invent business data automatically.

## Addressable Component Request Simulator

- Exercise the real endpoint rather than only calling the renderer directly.

- Edit path, query, form, body, header, and HTMX request values.

- Display status, media type, response headers, render time, response size, HTML, and preview.

- Show component traces and server logs when development tracing is enabled.

- Support opening the endpoint directly in a new browser view.

## HTMX Inspector

- Show the component resource URL, default target, default swap, trigger, polling, lazy-load, and history behavior.

- Display generated HTMX markup beside the Hedron source declaration.

- Explain each inferred attribute, such as action method, owning component target, or framework default.

- Highlight invalid or unresolved targets and conflicting HTMX behavior.

- Allow developers to compare normal and HX-Request rendering modes.

## Component Graph and Render Trace

- Show component composition from pages down to leaf components.

- Show inverse usage: which pages, components, routes, and actions depend on a component.

- Connect addressable components to their resource routes and returning actions.

- Provide a development render tree with timing, output bytes, template source, and cache status.

- Defer advanced interactive graph visualization and flame graphs until after the MVP.

## Diagnostics and Accessibility

- Missing or invalid props.

- Duplicate generated IDs or component keys.

- Invalid or unresolved HTMX targets.

- Route conflicts and duplicate component resource names.

- Template compilation and component resolution failures.

- Inputs without labels, duplicate IDs, missing alternative text, invalid ARIA, heading jumps, and malformed tables.

- Slow component renders and unusually large HTML responses.

- Diagnostics link to exact Python or HDN source locations when available.

## Registry as the Single Source of Truth

- The Explorer must consume the same ComponentDefinition registry used by rendering and routing.

- The registry records component type, Props type, component kind, source, endpoint, template, examples, dependencies, and metadata.

- OpenAPI extensions, previews, diagnostics, CLI commands, and testing helpers must not maintain separate copies of component metadata.

## Development and Production Safety

- The Explorer is enabled by default only in development mode.

- Production access must be explicitly enabled and protected by a dependency or authentication policy.

- Source paths, diagnostics, internal routes, and component data must never be exposed accidentally.

- Explorer and preview routes are excluded from the application's public OpenAPI schema by default.

## Explorer Extensibility

- Future plugins may contribute component panels for SQLAlchemy, Redis, authentication, OpenTelemetry, design tokens, or organization-specific accessibility rules.

- The Explorer itself should be built with Hedron components as a reference application and framework dogfooding target.

- Plugin panels must use a documented capability interface and cannot mutate component registration implicitly.

## CLI Integration

- hedron components: list registered components.

- hedron inspect \<Component\>: show metadata, props, source, endpoint, usages, examples, and warnings.

- hedron preview \<Component\>: open or serve an isolated preview.

- hedron routes: list pages, actions, component resources, and API routes.

- hedron graph \<Component\>: show component relationships.

- hedron check: run component, HTMX, template, and accessibility diagnostics.

## Explorer MVP

- Component and page registry with search and filtering.

- Component detail pages and Props schemas.

- Named examples and isolated previews.

- Addressable endpoint request simulator.

- Rendered HTML viewer and HTMX metadata.

- Source locations and actionable diagnostics.

- Development-only safeguards and public OpenAPI exclusion.

## Deferred Explorer Capabilities

- Interactive graph visualization.

- Performance flame graphs.

- Browser-based accessibility automation.

- Visual component editing.

- Plugin marketplace.

- Production monitoring and analytics.

## Suggested Internal Routes

- /\_hedron

- /\_hedron/components

- /\_hedron/components/{component_id}

- /\_hedron/components/{component_id}/preview

- /\_hedron/components/{component_id}/request

- /\_hedron/pages

- /\_hedron/actions

- /\_hedron/routes

- /\_hedron/diagnostics

- /\_hedron/openapi

**Product Principle:** Every automatic behavior Hedron introduces should be visible and explainable in the Component Explorer. The Explorer is the primary mechanism for keeping powerful framework inference transparent rather than magical.

# Hedron Scoped Styles

Hedron Scoped Styles provide CSS Modules-style isolation without Node.js or a browser-side styling runtime. Components own ordinary CSS files; Hedron compiles local classes, animation names, and component assets into stable collision-free output and makes the resulting behavior inspectable in the Component Explorer.

## Design Goals

- Keep ordinary standards-based CSS as the authoring language.

- Scope component classes and keyframes without Shadow DOM.

- Require no Node.js, npm, bundler, or browser-side CSS runtime.

- Work identically with Python-rendered components and HDN templates.

- Preserve readable, deterministic output and strong development diagnostics.

- Support themes and design systems through CSS custom properties and semantic variants.

- Make style ownership, compilation, and delivery visible in the Hedron Component Explorer.

## Component-Local Organization

- A component folder may contain component.py, template.hdn, styles.css, examples.py, browser.js, and tests.py.

- A styles.css file in a component folder is discovered automatically by convention.

- Components may also attach a stylesheet explicitly through scoped_styles(path).

- Global reset, token, typography, and application styles remain separate from component-local styles.

## Authoring Model

HDN templates receive a typed styles binding automatically:

> \<article class={styles.root}\>  
> \<h2 class={styles.title}\>{props.name}\</h2\>  
> \</article\>

Python-rendered components use the same style symbols:

> return Article(  
> H2(props.name, class\_=styles.title),  
> class\_=styles.root,  
> )

## Style Symbol Behavior

- Local class names are exposed as styles.root, styles.header, and similar typed symbols.

- Unknown style names fail early with source-aware diagnostics and spelling suggestions.

- Class lists accept conditional values and omit false or null entries automatically.

- Readable generated names are preferred by default for inspectability.

- Stable hashes must not depend on absolute machine paths, timestamps, import order, or randomness.

## Scoping Semantics

- Classes in component stylesheets are local by default.

- Keyframe names and animation references are scoped with the component.

- Explicit :global(...) and :local(...) escapes handle third-party or application-wide selectors.

- Generated class names provide isolation without increasing selector specificity through deep component prefixes.

- Native CSS nesting is preserved by default; optional flattening may be added for configured browser targets.

## Variants, Tokens, and Themes

- Finite semantic variants are preferred over arbitrary CSS generated from props.

- Variant values may map to local scoped classes and can be validated exhaustively against Literal or enum props.

- CSS custom properties are the primary mechanism for design tokens, theme switching, and controlled local overrides.

- Scoped classes provide isolation, variants represent component states, and tokens supply shared visual values.

- Component-level token overrides remain an explicit escape hatch rather than the default styling model.

## Cascade and Overrides

- Hedron should establish a predictable cascade-layer order: reset, tokens, base, components, utilities, overrides.

- Compiled component styles live in the components layer.

- Application overrides should use the overrides layer rather than specificity escalation.

- Users may customize packaged components through semantic props, extra classes, CSS variables, override layers, or style ejection.

## Asset Collection and Delivery

- The component registry records stylesheet and static-asset dependencies.

- The renderer deduplicates styles required by the known component graph.

- The MVP ships one fingerprinted application component stylesheet for reliability with HTMX-loaded fragments.

- Route-aware bundles may be added later after dependency analysis proves reliable.

- Dynamic component asset negotiation for HTMX fragments is a future optimization, not an MVP requirement.

- Relative CSS URLs are resolved from the component folder, fingerprinted, and rewritten to managed asset URLs.

## Compilation Pipeline

- Parse CSS structurally into an AST; regular-expression rewriting is not sufficient.

- Discover local class and keyframe symbols.

- Generate deterministic scoped identifiers.

- Rewrite selectors, animation references, and component-relative asset URLs.

- Emit compiled CSS plus a style-symbol manifest consumed by HDN and Python components.

- Cache compilation in development and emit immutable fingerprinted assets for production.

## HTMX Integration

- The initial page stylesheet must include styles for components that may arrive through ordinary HTMX fragment swaps.

- The MVP favors reliability by loading the deduplicated application component bundle up front.

- A later optional browser bridge may negotiate missing component assets through headers or out-of-band links.

- Style loading behavior must avoid flashes of unstyled content and remain compatible with Content Security Policy.

## Component Explorer Integration

- Each component detail view includes a Styles panel.

- The panel shows authored CSS, compiled CSS, class maps, keyframes, tokens, assets, consumers, and diagnostics.

- The preview uses the exact compiled stylesheet delivered by the application.

- The Explorer explains which scoped symbol produced each generated class.

- Variant completeness, missing classes, unsafe global selectors, duplicate symbols, and unused local symbols can be reported.

- All automatic style behavior must be visible and explainable rather than opaque framework magic.

## Development and Production Modes

- Development mode watches component styles, recompiles affected manifests, retains readable names, and refreshes previews.

- Production builds produce deterministic fingerprinted CSS and asset manifests with immutable caching.

- Runtime CSS compilation should not be required in production.

- External stylesheet delivery is preferred over injected style tags for strong CSP compatibility.

- Applications may configure a strict mode that rejects inline style attributes.

## Web Components and Shadow DOM

- Hedron components normally render into light DOM and use scoped generated classes.

- Independent Web Components may use Shadow DOM and own their internal styles.

- Shared themes should flow into Web Components through CSS custom properties when supported.

- Hedron does not rewrite third-party Shadow DOM styles unless the component explicitly opts into the Hedron compiler.

## MVP Scope

- One styles.css file per component.

- Local class names by default.

- styles.name references in HDN and Python.

- Stable generated class names.

- Keyframe scoping.

- Explicit :global(...) support.

- Global application stylesheet and CSS custom-property themes.

- One deduplicated application CSS bundle.

- Development recompilation and Explorer diagnostics.

## Deferred Features

- Cross-file CSS composition.

- Route-level CSS splitting.

- Dynamic HTMX asset negotiation.

- Sass or Less preprocessing.

- Arbitrary CSS-in-Python systems.

- Aggressive unused-selector elimination.

- Advanced minification and browser-side hot style replacement.

- A full design-token compiler.

## Scoped Styles Product Principle

Props define component inputs. HDN or Python defines component structure. Scoped Styles define component presentation. FastAPI defines transport. HTMX defines interaction. The Component Explorer makes every inferred behavior visible.
