# Phase 0.63 React island boundary

React remains an optional, Experimental interoperability path. Hedron core
does not import or bundle React. `react_island_recipe()` exposes the pinned
adapter metadata, and `react_island_host()` renders a server-owned fallback
inside a CSP-auditable host with cleanup and SSR markers.

An application may attach the pinned adapter at the host boundary, but the
fallback must remain complete and usable when JavaScript is absent or the
adapter is blocked by policy. The recipe is intentionally isolated: it does
not change the component registry, execute callbacks, or make React a runtime
dependency of the core package.
