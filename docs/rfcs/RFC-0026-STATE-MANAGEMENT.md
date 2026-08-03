# RFC-0026: State management

**Status:** Accepted

## Principle

Hedron does not create a universal state container. State remains in the layer that owns it:

- URL and request parameters for navigation and shareable filters;
- forms and typed actions for submitted interaction;
- application databases and services for durable domain state;
- framework-native sessions or cookies for session state;
- caches for derived data under explicit security scope;
- Web Components for transient browser-local interaction;
- addressable components and HTMX events for server-driven refresh.

Component instances are render values, not durable stateful actors. `SessionState`, if provided, is a typed adapter over framework session mechanisms and does not introduce process-global mutable state.

Optimistic UI is permitted only with explicit rollback and error behavior. DataEditor pending cells and local undo are browser state; accepted changes become server state only after typed validation and application persistence.

## Acceptance criteria

- Multi-worker deployments do not depend on in-process component state.
- Session, cache, and browser-state scopes are visible in documentation and Explorer.
- HTMX history and caches can be disabled for sensitive state.
- Restarting a process does not silently lose state represented as durable.

