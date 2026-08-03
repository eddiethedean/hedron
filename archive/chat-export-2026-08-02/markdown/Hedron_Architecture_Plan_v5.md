# Hedron Architecture Plan v5

Python-first, FastAPI-first, HTMX-native component framework.

## Guiding Principles

- Beginner-first with progressive disclosure.

- FastAPI is the flagship integration.

- Framework-neutral core with Flask and Django adapters.

- HTML-first, server-first.

- Components are the primary abstraction.

## Packaging

- hedron -\> FastAPI distribution

- hedron-core -\> shared engine

- hedron-flask -\> Flask integration

- hedron-django -\> Django integration

## Model System

- Users import Props, Model, FormModel and Field from Hedron.

- Pydantic remains an internal implementation detail.

- Restricted portable model system.

## Learning Path

- Use built-in components.

- Configure props and slots.

- Compose components.

- Use HDN when needed.

- Build browser components.

## HDN

- JSX-inspired but server-native.

- Lowercase tags are HTML.

- Uppercase tags are Hedron components.

- Hyphenated tags are Web Components.

## Components as HTTP Resources

- Addressable components expose endpoints automatically.

- Developers reference components instead of URLs.

- HTMX attributes are generated automatically.

- Supports refresh, polling, lazy loading and independent testing.

## Component Types

- Renderable Components

- Addressable Components

## FastAPI

- @app.page returns components.

- Typed actions.

- Automatic HTMX fragment rendering.

## Flask and Django

- Separate packages.

- Shared component model.

- No FastAPI dependency.

## Future

- React migration tooling.

- Optional Rust acceleration after profiling.

- Cross-language support later.

- Visual component studio.
