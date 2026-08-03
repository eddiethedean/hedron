# Component model acceptance

## Phase 0.1 (`v0.1.0`) subset

- [x] Python components compose text, native elements, fragments, children, named slots, optional nodes, and sequences.
- [x] Props validate at construction and remain immutable during rendering.
- [x] Python and HDN components lower to equivalent node semantics. *(phase 0.3)*
- [x] Renderable components expose no route by default.
- [x] Addressable components retain a distinct factory input contract (`@addressable` → `AddressableDescriptor`; HTTP only via `include_component`). *(phase 0.2)*
- [x] Page and fragment rendering produce correct assets and metadata.
- [ ] Return-annotation mismatches produce component-aware diagnostics. *(deferred; construction diagnostics covered)*

## Quality (0.1)

- [x] Text, attribute, URL, CSS, and trusted-HTML boundaries pass the security corpus. *(Markdown/SVG charts deferred)*
- [x] Component identity is deterministic and excludes secrets.
- [x] Cycles (same instance re-entering `render`) and resource limits fail with a readable component path; nested same-type components are allowed.
- [x] Built-ins document props, slots, accessibility, examples, and escape hatches.
- [x] Representative trees have stable snapshots and performance baselines.

## Exit

- [x] The reference CRUD page can be rendered without a live HTTP server.
- [x] Produces the same core HTML when invoked through FastAPI (body parity; PAGE responses may additionally inject the bundled HTMX script). *(phase 0.2)*
