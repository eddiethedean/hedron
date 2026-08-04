# HDN acceptance (legacy prototype)

> **Legacy migration gate:** D-040/RFC-0031 select an optional Jinja integration and schedule HDN
> deprecation in 0.11, default-discovery removal in 0.12, and runtime removal in 0.13. Checked items
> below describe narrow prototype evidence, not an active language promotion gate.

## Migration gate

- [x] Current language/runtime and public APIs are labeled experimental.
- [x] New HDN feature and tooling work is stopped; only critical fixes and migration support remain.
- [x] RFC-0031 specifies the selected Jinja trust, component, metadata, limit, diagnostics,
  packaging, and migration contracts.
- [ ] The Jinja replacement passes `JINJA.md` without relying on current HDN internals. *(0.11)*
- [ ] HDN is deprecated in 0.11, disabled from default discovery in 0.12, and removed from
  first-party runtime packages in 0.13 with retained migration documentation.

## Language

- [x] Grammar covers native tags, explicitly imported components, custom elements,
  fragments, props, children, slots (MVP default-content fragments; named fill contracts
  deferred), conditions, loops, and pure helpers. Templates without imports retain the
  compatibility tag-name lookup.
- [ ] Operator precedence and error recovery are specified by fixtures. *(Deferred — expand fixture corpus in a later hardening pass; current expressions cover helpers, comparisons, indexing, and nullish coalesce.)*
- [x] Explicit Python/JavaScript call and module-import syntax is rejected. This is not a complete
  sandbox claim: current attribute/index/helper operations still run Python data-model behavior,
  which is one reason for the design hold.
- [x] Contextual escaping and `TrustedHtml` rules match Python rendering.
- [ ] HTML, component, accessibility, style-symbol, and security errors include source spans. *(Deferred — diagnostics carry expression/context today; full span coverage lands with richer tooling in phase 0.4+.)*

## Tooling

- [x] Formatter is idempotent.
- [x] Source maps identify original templates.
- [x] `inspect` and `eject` preserve semantic contracts.
- [x] The only source extension is `.hdn` (`template.hdn`); discovery, `hedron eject`, and
  `hedron dev` do not maintain a second extension or precedence rule.
- [x] Production consumes versioned compiled artifacts without Node.js.
- [x] Explicit imports survive compiled-program serialization, appear in dependency
  manifests, and resolve exclusively through the host component mapping.
- [x] Parser/compiler fuzz tests have bounded time (memory bound deferred).

## Legacy prototype evidence

The reference application contains one narrow Python/HDN observable-output comparison. Promotion
requires the RFC-0031 Jinja and migration gates, not additional promotion checks against the legacy
implementation.
