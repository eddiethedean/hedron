# Hedron Architecture Plan v16

This revision restructures Hedron around FastAPI's documented extension points instead of treating FastAPI as merely a dependency.

## Foundational Principle

Hedron extends FastAPI through custom APIRoute classes, APIRouter, response classes, middleware, lifespan, dependency injection, OpenAPI customization, StaticFiles, and documented extension points rather than replacing FastAPI.

## Architecture

- Python-first implementation.

- FastAPI-first experience via the 'hedron' package.

- Framework-neutral 'hedron-core' with Flask and Django adapters.

- Progressive disclosure from beginner to expert.

## FastAPI Extension Points

- Custom HedronRoute built on APIRoute.

- HedronRouter as the primary organizational unit.

- Component routers with automatic discovery.

- Custom HTML/component response classes.

- Lifespan-based startup and shutdown.

- Middleware for HTMX, themes, timing, security headers and Explorer.

- Dependency injection preserved everywhere.

- BackgroundTasks reused instead of inventing a task runner.

- StaticFiles used for compiled assets.

- Dependency overrides power Explorer examples and testing.

- Custom OpenAPI operation IDs.

- OpenAPI extensions via x-hedron-\* metadata.

- Hidden internal routes using include_in_schema=False.

## Component System

- Renderable Components.

- Addressable Components as HTTP resources.

- Direct component return values from Hedron endpoints.

- Explicit HTML(...) wrapper when using plain FastAPI.

- Component Explorer as the primary development tool.

## Developer Experience

- Automatic object rendering (Auto()).

- Data Intelligence Layer.

- Scoped Styles.

- HDN advanced templates.

- DataEditor.

- Chart adapters.

- Security-first defaults.

- Async-first architecture.

## Guiding Philosophy

JSON endpoints return models. HTML endpoints return components. Swagger documents HTTP. Hedron Explorer documents components. Hedron should always prefer documented FastAPI extension mechanisms over parallel abstractions.
