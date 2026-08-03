# Hedron Architecture Plan v6

Updated vision incorporating component-returning endpoints and FastAPI-first integration.

## Core Vision

- Python-first, server-first framework.

- FastAPI is the flagship integration.

- Framework-neutral core with Flask and Django adapters.

- Progressive disclosure from beginner to expert.

## Packaging

- hedron → FastAPI distribution.

- hedron-core → shared engine.

- hedron-flask → Flask integration.

- hedron-django → Django integration.

## Model System

- Public APIs expose Props, Model, FormModel, and Field.

- Pydantic remains an implementation detail.

- Only Hedron-supported portable features are available.

## HDN

- Advanced authoring tool.

- JSX-inspired without React runtime semantics.

- Lowercase HTML, Uppercase Hedron components, hyphenated Web Components.

## Components as HTTP Resources

- Addressable components automatically expose HTTP resources.

- Developers reference components instead of writing HTMX URLs.

- Supports refresh, lazy loading, polling, bookmarking, and isolated testing.

## FastAPI Endpoint Integration

Hedron extends FastAPI so endpoint functions can directly return Hedron components. The return annotation represents the HTML contract in the same way that a Pydantic model represents a JSON contract in FastAPI.

@app.get("/users/{user_id}")  
def user_card(user_id: int) -\> UserCard:  
return UserCard(user=get_user(user_id))

Hedron automatically renders the component into HTML, creates the correct HTML response, validates the returned component against the annotated type, and preserves ordinary FastAPI behavior for JSON endpoints.

## Component Types

- Renderable Components: reusable composition primitives.

- Addressable Components: renderable components that can also be routed, refreshed, lazy-loaded and targeted by HTMX.

## Future

- React migration toolkit.

- Optional Rust acceleration after profiling.

- Cross-language support after Python API matures.

- Visual component studio.

## Guiding Principle

Hedron should feel like a natural extension of FastAPI. JSON endpoints return models; HTML endpoints return components.
