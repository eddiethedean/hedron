# Design principles

1. **Progressive disclosure.** Users encounter a concept only when it solves a problem they have reached.
2. **Server first.** Prefer server rendering unless browser execution provides clear user value.
3. **Standards first.** Prefer HTML, CSS, HTTP, HTMX, and Web Components over proprietary protocols.
4. **FastAPI native.** Extend documented FastAPI mechanisms instead of bypassing them.
5. **Typed boundaries.** Props, inputs, actions, data changes, events, and integration results have explicit contracts.
6. **Components compose.** Components own structure and may own styles, examples, tests, documentation, and browser behavior.
7. **Addressability is explicit.** Rendering a component never silently exposes an endpoint.
8. **Infer mechanics, not business intent.** Authorization, trust, persistence, and destructive meaning remain explicit.
9. **Secure by default.** Dangerous behavior requires a visible, typed opt-in.
10. **Explain the magic.** Every automatic decision is inspectable and overrideable.
11. **Deterministic rendering.** The same prepared component produces equivalent HTML and metadata.
12. **Async at I/O boundaries.** Data loading may be asynchronous; tree construction and serialization remain deterministic.
13. **Browser state stays local.** Rich widgets may own transient interaction state without inventing an application-wide client store.
14. **No mandatory Node.js.** The official development and production paths work without npm or a JavaScript bundler.
15. **Keep the core small.** Heavy or domain-specific integrations are lazy optional packages or extras.
16. **Accessibility is contractual.** Components express accessible names, states, keyboard expectations, and fallbacks.
17. **Operational behavior is visible.** Timing, caching, assets, security context, routes, and payload sizes are inspectable.
18. **Escape hatches earn stability.** Native HTML, attributes, CSS, Web Components, and explicit
    responses remain available. A custom declarative language is optional only if evidence justifies
    owning it; the current HDN prototype is experimental and scheduled for removal under D-040.
19. **Framework adapters preserve authority.** FastAPI, Flask, and Django retain their routing, security, sessions, and lifecycle semantics.
20. **Optimize after measurement.** Complexity must be justified by representative evidence.
