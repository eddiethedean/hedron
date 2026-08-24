# Vision

Hedron enables Python developers to build maintainable, modern web interfaces with the same language and architectural model they use for their FastAPI applications.

## Product promise

> Build component-based FastAPI interfaces with HTML and HTMX, without requiring Node.js.
> Start with familiar Python objects and built-in components; adopt browser components or a future
> evidence-backed declarative format only when additional control is needed.

Hedron combines:

- React-like component composition;
- Streamlit-like low-friction handling of common Python objects;
- FastAPI-native routing, dependency injection, security, OpenAPI, and async I/O;
- standards-based HTML, CSS, HTTP, HTMX, and Web Components;
- an Explorer that makes framework inference visible and testable.

## Initial audience

The beachhead is Python teams building FastAPI CRUD applications, internal tools, data applications, dashboards, forms, and administrative systems in environments where Node.js is unavailable or unwanted.

Flask and Django are intentional adapter targets. They are not part of the flagship onboarding path and must not distort the FastAPI experience.

## Success

Hedron succeeds when a new user can render a useful secure page in five minutes, build a CRUD
application with Python components, inspect every inferred behavior, and progressively replace
defaults without abandoning the framework. A separate template language is not a success criterion.

The output remains ordinary web technology. A Hedron application can be debugged with browser tools, HTTP clients, FastAPI tooling, and standard accessibility and security scanners.
