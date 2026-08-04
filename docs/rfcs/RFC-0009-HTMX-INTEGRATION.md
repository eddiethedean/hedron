# RFC-0009: HTMX integration

**Status:** Accepted

## Model

HTMX owns server requests and DOM swaps. Hedron supplies typed conveniences, page-versus-fragment response selection, component references, safe targets, response headers, testing helpers, and diagnostics while keeping generated `hx-*` attributes visible.

The current compatibility line targets HTMX `>=2.0,<3.0` with an exact reviewed core asset per Hedron release.
Removed HTMX 1 attributes are not accepted. HTMX 2 extensions are independently pinned, locally
served optional assets with their own compatibility, CSP, lifecycle, and audit evidence.

## Behavior

- Ordinary navigation receives a full document; `HX-Request` normally receives a fragment.
- Typed actions infer safe mechanical attributes from registered routes.
- `RefreshButton`, lazy loading, polling, pagination, and retry helpers operate on addressable components.
- Cross-component refresh uses explicit `HX-Trigger` events.
- History cache misses receive full pages and do not masquerade as ordinary fragment requests.
- Secure runtime defaults disable eval and response-script execution, preserve same-origin
  requests, and enable native form-validity reporting; an explicit application config may replace
  the profile.
- Advanced users can use validated native HTMX attributes.

Unsafe methods use CSRF protection under cookie authentication. GET never represents mutation. User input cannot control arbitrary attribute names, target selectors, redirect locations, or dependency values. Sensitive pages may disable HTMX history snapshots.

## Acceptance criteria

- Full and fragment modes are covered by request-header tests.
- Generated attributes have an Explorer trace and an explicit override.
- Redirects, validation fragments, out-of-band swaps, and triggers obey documented FastAPI response behavior.
- Official HTMX assets can be locally served without Node.js.

The phase 0.6+ adoption and extension gates are tracked in the
[HTMX 2 integration audit](../HTMX_2_AUDIT.md).
