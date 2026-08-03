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
