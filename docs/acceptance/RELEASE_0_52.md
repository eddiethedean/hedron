# Hedron `v0.52` conformance authority and Posit lifecycle acceptance

**Status:** Verified in-tree `v0.52.0` (cut-ready; **do not tag yet**).
**`v0.52.0` on PyPI** until upload (`registry_status = "deferred"`).<br>
**Planning baseline:** Published in-tree `v0.51.2`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.51.2`<br>
**Target:** Hedron `v0.52.0`<br>
**Decision/RFC:** D-089 / D-090 / [RFC-0079](../rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md)<br>
**Tracking:** [#522](https://github.com/eddiethedean/hedron/issues/522)<br>
**Related:** [#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513)

D-090 named shipped 0.51.2 seams (`hedron-portable-1`, `Capability`,
`load_bundled_fixtures`, `HedronPosit` / `href_for` /
`cookie_path_for_mount` / `ConnectCookieMode`). Stage 1 shipped conformance
authority extensions and Posit lifecycle companions (`PositContext`,
`CookieRegistry`, `hands_off`, matrix, diagnostics, query/fragment parity).
Do not create Git tag `v0.52.0` until a cut is intended.

## Release contract

- Extend `CONTRACT_VERSION` / `hedron-portable-1`; do not silently replace it.
- Node/Java evaluate the declared portable subset only — not FastAPI,
  browser, or complete Hedron.
- Supported Connect cookie bridge stays `drop_supported`.
- Posit companions #508–#513 are in-phase lifecycle gates, not a second RFC.
- PKG-052 upgrade source is **0.51**, not 0.50.
- Living tip is **0.52.0** in-tree; PyPI remains **0.51.0** until upload.

## Exact gate matrix

| Gate | Verified means |
|---|---|
| `PROTOCOL-052` | Negotiation, canonical encoding, forward-unknown behavior. |
| `PROFILE-052` | Profile registry, suite digests, and waivers. |
| `FIXTURE-052` | Fixture compiler validation. |
| `NEGATIVE-052` | Negative/boundary/metamorphic/adversarial vectors. |
| `RUNTIME-052` | Python/Node/Java stream, cancel, and resource behavior. |
| `DIFF-052` | Differential agreement across the declared subset. |
| `SECURITY-052` | Untrusted suites/results and secret boundaries. |
| `SANDBOX-052` | Files, archives, processes, temp, and network isolation. |
| `REPORT-052` | Signed envelopes and exact provenance. |
| `CI-052` | JUnit/SARIF, offline bundles, CI recipes. |
| `COMPAT-052` | Protocol current/previous matrix. |
| `PLATFORM-052` | OS/locale/runtime matrix. |
| `COOKIE-052` | Cookie registry lifecycle (#508). |
| `CONTEXT-052` | Request-bound `PositContext` (#509). |
| `HANDSOFF-052` | Hands-off URL adaptation (#510). |
| `MATRIX-052` | Deployment-matrix check/fixtures (#511). |
| `PDIAG-052` | Proactive Posit diagnostics (#512). |
| `ROUTEURL-052` | Named-route query/fragment/durable parity (#513). |
| `DOCS-052` | Protocol, author, Posit deployment, migration docs. |
| `AUTHOR-052` | External author kit without monorepo import. |
| `PKG-052` | Clean artifacts; 0.51 upgrade/rollback. |
| `SUPPLY-052` | Checksums, licenses, SBOM/provenance. |
| `REGRESS-052` | Whole-fleet regression; no hidden Deferred claims. |

## Stage 0 / Stage 1 checklist

- [x] D-089 and RFC-0079 define conformance authority + Posit lifecycle ownership.
- [x] D-090 rebases the living/planning baseline to Published in-tree `v0.51.2`.
- [x] Tracking [#522](https://github.com/eddiethedean/hedron/issues/522) bound.
- [x] Companions [#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513) bound.
- [x] Stage 0 / contract refine makes no runtime/version/living-tip claim.
- [x] Stage 1 runtime shipped (Verified gates; living tip `v0.54.0` in-tree).
- [x] In-tree cut metadata flipped (`docs/release.toml`, package versions, CI gate).
- [ ] Git tag `v0.52.0` / PyPI upload (deferred; do not tag yet).
