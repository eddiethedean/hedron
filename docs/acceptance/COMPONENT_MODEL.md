# Component model acceptance

## Functional

- [ ] Python components compose text, native elements, fragments, children, named slots, optional nodes, and sequences.
- [ ] Props validate at construction and remain immutable during rendering.
- [ ] Python and HDN components lower to equivalent node semantics.
- [ ] Renderable components expose no route by default.
- [ ] Addressable components retain a distinct factory input contract.
- [ ] Page and fragment rendering produce correct assets and metadata.
- [ ] Return-annotation mismatches produce component-aware diagnostics.

## Quality

- [ ] Text, attribute, URL, CSS, JSON, and trusted-HTML boundaries pass the security corpus.
- [ ] Component identity is deterministic and excludes secrets.
- [ ] Cycles and resource limits fail with a readable component path.
- [ ] Built-ins document props, slots, accessibility, examples, and escape hatches.
- [ ] Representative trees have stable snapshots and performance baselines.

## Exit

The reference CRUD page can be rendered without a live HTTP server and produces the same core HTML when invoked through FastAPI.

