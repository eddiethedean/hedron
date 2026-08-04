# Hedron `v0.9.0` HDJ replacement acceptance

Phase 0.9 is the intentional authoring break defined by D-041/D-043/RFC-0031. It introduces HDJ
through the optional `hedron-jinja` distribution and removes HDN completely. Native Flask/Django
depth and bounded QuerySet work move to phase 0.11. Evidence is indexed by
[`release-gate-0.9.toml`](release-gate-0.9.toml).

## Clean removal

- [x] HDN parser, evaluator, formatter, render program, source discovery, registry fields, manifest
  entries, build output, exports, CLI/Explorer paths, examples, and tests are removed.
  *(`BREAK-09-001`)*
- [x] Build-manifest format 2 rejects old artifacts, coordinated packages report `0.9.0`, and 0.8
  is documented as the final HDN-capable line. *(`BREAK-09-001`)*
- [x] No compatibility flag, legacy runtime package, dual discovery period, or converter ships.
  *(`BREAK-09-001`)*

## Optional HDJ package

- [x] `hedron-jinja` installs independently, imports as `hedron_jinja`, and is exposed through the
  optional `hedron[jinja]` extra without making Jinja a core dependency. *(`JINJA-09-001`)*
- [x] Typed template specs, explicit immutable component bindings, inline components, explicit
  `with body` blocks, named slots, sync/async entry points, and page/fragment shape checks have
  focused tests. *(`JINJA-09-001`)*
- [x] Strict undefined/escaping, explicit trusted HTML and URL filters, direct-render fail-closed
  behavior, component/output budgets, and `RenderResult` metadata merging have focused tests.
  *(`JINJA-09-001`)*
- [ ] `.hdj` format-v1 parsing, mandatory static prologue, profile expansion, feature/capability
  checking, source line preservation, and `.hdj`-only loader behavior have focused evidence.
  *(`JINJA-09-002`)*
- [ ] Trusted literal HTML/CSS/JS/Web Component/Jinja/HTMX source remains standards-complete;
  dynamic-value trust and SecurityPolicy/CSP capability checks stay separate. *(`JINJA-09-002`)*
- [ ] Hedron component, route, form/CSRF, interaction, asset/style/theme, browser module,
  data/chart, diagnostic, trace, and adapter features have HDJ parity fixtures. *(`JINJA-09-002`)*
- [ ] The pinned HTMX attribute/header/event/extension surface has progressive enhancement,
  history, OOB, forms, concurrency, lifecycle, accessibility, and policy evidence.
  *(`JINJA-09-002`)*
- [ ] Static include/extends inventory, contextual URL-attribute validation, macro/loop/depth
  budgets, application/package loader namespaces, and full build-manifest integration satisfy the
  detailed [HDJ ledger](JINJA.md). *(`JINJA-09-002`)*

## Release proof

- [x] The repository regression suite and lint pass after the hard removal. *(`REGRESS-09-001`)*
- [ ] Built wheel/sdist clean-install, supported Python/Jinja matrix, docs examples, 0.8→0.9
  manual-upgrade fixture, rollback, SBOM/license/provenance, and public-index verification pass.
  *(`PKG-09-001`)*
- [ ] Every remaining detailed HDJ requirement is either Verified or explicitly Deferred with an
  owner, destination phase, and stability impact.

## Exit

The phase can publish only when no first-party runtime path understands HDN, the optional HDJ
package satisfies its advertised beta contract, every release-gate row is `Verified` or owned
`Deferred`, and the upgrade guide states the deliberate incompatibility plainly.
