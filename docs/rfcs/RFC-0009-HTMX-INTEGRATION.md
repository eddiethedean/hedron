# RFC-0009: HTMX integration

**Status:** Accepted

## Model

HTMX owns server requests and DOM swaps. Hedron supplies typed conveniences, page-versus-fragment response selection, component references, safe targets, response headers, testing helpers, and diagnostics while keeping generated `hx-*` attributes visible.

## Behavior

- Ordinary navigation receives a full document; `HX-Request` normally receives a fragment.
- Typed actions infer safe mechanical attributes from registered routes.
- `RefreshButton`, lazy loading, polling, pagination, and retry helpers operate on addressable components.
- Cross-component refresh uses explicit `HX-Trigger` events.
- Advanced users can use validated native HTMX attributes.

Unsafe methods use CSRF protection under cookie authentication. GET never represents mutation. User input cannot control arbitrary attribute names, target selectors, redirect locations, or dependency values. Sensitive pages may disable HTMX history snapshots.

## Acceptance criteria

- Full and fragment modes are covered by request-header tests.
- Generated attributes have an Explorer trace and an explicit override.
- Redirects, validation fragments, out-of-band swaps, and triggers obey documented FastAPI response behavior.
- Official HTMX assets can be locally served without Node.js.

