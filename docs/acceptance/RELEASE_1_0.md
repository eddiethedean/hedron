# Hedron `v1.0.0` release acceptance

## Specification and API

- [ ] Foundations and all 1.0 RFCs are Accepted or explicitly Deferred.
- [ ] Public APIs have reference documentation, typing, examples, stability level, and migration policy.
- [ ] Public APIs, rendered markup, registry/plugin metadata, HDN/build formats, diagnostics, and
  browser assets have explicit stability classifications.
- [ ] Decision log and glossary match the implementation.
- [ ] No implementation behavior depends on unavailable or noncanonical source material.

## Product proof

- [ ] A new user reaches a useful secure page in under five minutes using the published guide.
- [ ] The reference application demonstrates authenticated CRUD, forms/actions, addressable components, HTMX, HDN, scoped styles, DataEditor, a chart, `Auto()`, async sources, and Explorer.
- [ ] Plain FastAPI incremental adoption is documented and tested.
- [ ] Flask and Django are each labeled supported, experimental, or deferred; every supported
  adapter capability passes portable and native conformance from published artifacts.

## Release quality

- [ ] Security, accessibility, performance, packaging, deployment, compatibility, and supply-chain acceptance suites pass.
- [ ] No unresolved critical/high issue or undocumented breaking change remains.
- [ ] Supported-version matrix, deprecation window, changelog, and upgrade guide exist.
- [ ] Supported framework/server/browser matrix, maintenance/backport policy, and security reporting
  and response targets are published.
- [ ] Offline/no-Node development and production paths pass.
- [ ] Recovery and rollback are rehearsed; SBOM, dependency/browser-asset vulnerability reports,
  license inventory, and artifact provenance/attestation are retained.
- [ ] Every release-gating requirement is `Verified` under [EVIDENCE.md](EVIDENCE.md), with no
  expired waiver or unowned deferment.

## Exit

At least one published `1.0.0rcN` train is exercised from clean installation and supported upgrade
through deployment and rollback using only published artifacts. The final stable artifacts differ
only by approved version/release metadata, and the named acceptance owners sign off on the retained
evidence bundle.
