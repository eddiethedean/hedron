# Hedron `v1.0.0` release acceptance

Phase 0.8 freezes the public baseline and produces the evidence required here. Items marked
**0.8-ready** are satisfied by the freeze train and [release-gate-0.8.toml](release-gate-0.8.toml);
**RC-required** items must be proven from published `1.0.0rcN` artifacts.

## Specification and API

- [x] Foundations and all 1.0 RFCs are Accepted or explicitly Deferred. *(0.8-ready)*
- [x] Public APIs have reference documentation, typing, examples, stability level, and migration policy.
  *([STABILITY.md](../api/STABILITY.md), [upgrade.md](../guides/upgrade.md))*
- [x] Public APIs, rendered markup, registry/plugin metadata, HDN/build formats, diagnostics, and
  browser assets have explicit stability classifications. *(`FRZ-001`)*
- [x] Decision log and glossary match the implementation. *(0.8-ready)*
- [x] No implementation behavior depends on unavailable or noncanonical source material. *(0.8-ready)*

## Product proof

- [ ] A new user reaches a useful secure page in under five minutes using the published guide.
  *(RC-required from published artifacts)*
- [ ] The reference application demonstrates authenticated CRUD, forms/actions, addressable components, HTMX, HDN, scoped styles, DataEditor, a chart, `Auto()`, async sources, and Explorer.
  *(RC-required)*
- [x] Plain FastAPI incremental adoption is documented and tested. *(0.8-ready)*
- [x] Flask and Django are each labeled supported, experimental, or deferred; every supported
  adapter capability passes portable and native conformance from repository evidence.
  *(`ADP-FLK-08-*`, `ADP-DJG-08-*`; RC re-proves from published wheels)*

## Release quality

- [x] Security, accessibility, performance, packaging, deployment, compatibility, and supply-chain acceptance suites pass on the 0.8 train.
  *([release-gate-0.8.toml](release-gate-0.8.toml))*
- [x] No unresolved critical/high issue or undocumented breaking change remains on the freeze baseline.
- [x] Supported-version matrix, deprecation window, changelog, and upgrade guide exist.
  *([COMPATIBILITY.md](../COMPATIBILITY.md), [upgrade.md](../guides/upgrade.md))*
- [x] Supported framework/server/browser matrix published; maintenance/backport and security reporting
  targets documented in COMPATIBILITY / RELEASE. *(0.8-ready)*
- [ ] Offline/no-Node development and production paths pass from published RC artifacts. *(RC-required)*
- [ ] Recovery and rollback are rehearsed; SBOM, dependency/browser-asset vulnerability reports,
  license inventory, and artifact provenance/attestation are retained from the RC train.
  *(scripts exist on 0.8; RC-required retention)*
- [x] Every 0.8 release-gating requirement is `Verified` or owned `Deferred` under [EVIDENCE.md](EVIDENCE.md).

## Exit

At least one published `1.0.0rcN` train is exercised from clean installation and supported upgrade
through deployment and rollback using only published artifacts. The final stable artifacts differ
only by approved version/release metadata, and the named acceptance owners sign off on the retained
evidence bundle.

Procedure: [RELEASE.md](../RELEASE.md) (`## Rehearse 1.0.0rcN`) and
`scripts/rehearse_rc.py --help`.
