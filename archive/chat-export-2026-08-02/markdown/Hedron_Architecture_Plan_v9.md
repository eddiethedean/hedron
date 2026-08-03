# Hedron Architecture Plan v9

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
