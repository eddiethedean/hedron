# RFC-0079: Conformance authority and HedronPosit deployment lifecycle

**Status:** Accepted<br>
**Target phase:** 0.52 (`v0.52.0`)<br>
**Decision:** D-089<br>
**Stage 0 contract refine:** D-090<br>
**Planning baseline:** Published in-tree `v0.51.2` (D-090)<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.51.2`<br>
**Tracking:** [#522](https://github.com/eddiethedean/hedron/issues/522)<br>
**Related:** [#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513)
— HedronPosit companion lifecycle; in-phase, not separate RFCs<br>
**Extends:** [RFC-0064](RFC-0064-PRODUCTION-GRADE-TOOLING.md),
[RFC-0066](RFC-0066-HEDRON-POSIT.md), RFC-0031 conformance seed,
RFC-0059 / 0.33 Posit topology

**Revision:** 2026-08-20 — D-089 ownership + D-090 Stage 0 refine against
Published in-tree `v0.51.2`. Living tip stays `v0.51.2`. No Stage 0
runtime, version bump, or PyPI claim.

## Summary

Phase 0.52 has **two locked workstreams** under one RFC and one cut:

1. **Conformance authority** — `hedron-conformance` becomes a versioned
   compatibility authority for a declared **portable subset**
   (`hedron-portable-1` and negotiated successors). Node/Java evaluators
   become independently installable reference consumers, not monorepo-only
   demonstrations.
2. **HedronPosit deployment lifecycle** — cookie registry, `PositContext`,
   hands-off URL adaptation, deployment-matrix check, proactive diagnostics,
   and named-route query/fragment parity so Workbench/Connect apps stop
   owning mount cookie paths and redirect adaptation
   ([#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513)).

This phase does **not** promise full non-Python Hedron ports, does **not**
reopen `polling_only`, and does **not** restore a Supported Connect cookie
bridge (`BRIDGE_DECISION=drop_supported` / `drop_supported` remains in force).

## Goals

### Workstream A — Conformance authority

- Publish a versioned conformance **manifest** with protocol negotiation,
  profile registry, suite digests, waivers, and forward-unknown behavior —
  extending `CONTRACT_VERSION` / `hedron-portable-1`, not replacing it
  without a negotiation story.
- Expand positive/negative/boundary/metamorphic/adversarial vectors; add a
  fixture compiler that rejects contradictory expectations before any
  runtime executes a suite (`load_bundled_fixtures` remains the seed corpus
  API).
- Package Node and Java evaluators as clean ecosystem artifacts with
  checksums, licenses, SBOM, and reproducible release instructions.
- Run Python/Node/Java differential tests across supported OS/runtime
  matrices; retain disagreements as regression vectors.
- Version the third-party author kit so external packages declare
  `Capability` values without importing the monorepo.

### Workstream B — HedronPosit deployment lifecycle

| Issue | Deliverable |
|---|---|
| [#508](https://github.com/eddiethedean/hedron/issues/508) | Cookie registry + `set`/`delete` lifecycle; no literal `Path=auto` |
| [#509](https://github.com/eddiethedean/hedron/issues/509) | Request-bound `PositContext` / `posit_for(request)` |
| [#510](https://github.com/eddiethedean/hedron/issues/510) | Opt-in hands-off local URL / redirect adaptation |
| [#511](https://github.com/eddiethedean/hedron/issues/511) | Deployment-matrix fixtures + `hedron-posit check --matrix` |
| [#512](https://github.com/eddiethedean/hedron/issues/512) | Proactive diagnostics; never log cookie values |
| [#513](https://github.com/eddiethedean/hedron/issues/513) | Query/fragment/durable parity across `href_for` / `redirect_for` families |

## Non-goals and exclusions

From ROADMAP §0.52:

- Full non-Python Hedron ports or browser runtimes for Node/Java.
- Restoring a Supported Connect authenticated-header cookie bridge.
- Reopening `polling_only`, `MORPH-048`, `SR-021`, Explorer 0.50 gate IDs,
  or 0.51 extras gates.
- Owning 0.53 Application DX (#514–#521) or 0.54 notebook/sim/sample-kit /
  external-author `hedron package doctor`.
- Treating subdirectory fixture trees as default authority before profiles
  admit them.
- Marketing Node/Java as FastAPI, Workbench, or complete Hedron substitutes.
- Inventing numeric limits, asset digests, or perf budgets in Stage 0.
- Stage 0 runtime symbols, package version bumps, or living-tip movement.

## Consume shipped, do not fork (D-090)

Stage 1 consumes these **0.51.2** seams:

**Conformance / runtimes:**

- `CONTRACT_VERSION = "hedron-portable-1"`, `FIXTURE_VERSION`,
  `Capability` enum, `load_bundled_fixtures()`, CLI `run` / `list` /
  `schema`, `compat` negotiation, `author_kit/` seed
- Default bundled corpus = top-level `fixtures/*.json` only
- `hedron-runtime-node` / `hedron-runtime-java` remain tooling-grade until
  `RUNTIME-052` / `PKG-052`

**HedronPosit:**

- `HedronPosit` helpers: `href` / `href_for`, `redirect` / `redirect_for`,
  `browser_url` / `browser_url_for`, `external_url` / `durable_url`
- `cookie_path_for_mount` and `workbenchify` owned-cookie Path repair
- `ConnectCookieMode.NATIVE` Supported; `authenticated_header_v1`
  Experimental extension-point only
- CLI: `hedron-posit check` / `run` / `doctor` (no `--matrix` yet)
- Asymmetry to close under #513: `browser_url_for` / `durable_url_for`
  accept `query`/`fragment`; `href_for` / `redirect_for` do not

## Locked portable subset

Node/Java **do** evaluate the declared portable subset under
`hedron-portable-1` profiles. They **do not** evaluate FastAPI apps,
browser runtimes, Workbench/Connect mounts, or a complete Hedron stack.

## Locked gate plan

| Gate | Workstream | Verified means |
|---|---|---|
| `PROTOCOL-052` | A | Negotiation, canonical encoding, forward-unknown behavior |
| `PROFILE-052` | A | Profile registry, suite digests, waivers |
| `FIXTURE-052` | A | Fixture compiler validation |
| `NEGATIVE-052` | A | Negative/boundary/metamorphic/adversarial vectors |
| `RUNTIME-052` | A | Python/Node/Java stream, cancel, resource behavior |
| `DIFF-052` | A | Differential agreement across the declared subset |
| `SECURITY-052` | A | Untrusted suites/results and secret boundaries |
| `SANDBOX-052` | A | Files, archives, processes, temp, network isolation |
| `REPORT-052` | A | Signed envelopes and exact provenance |
| `CI-052` | A | JUnit/SARIF, offline bundles, CI recipes |
| `COMPAT-052` | A | Protocol current/previous matrix |
| `PLATFORM-052` | A | OS/locale/runtime matrix |
| `COOKIE-052` | B | Cookie registry lifecycle (#508) |
| `CONTEXT-052` | B | Request-bound `PositContext` (#509) |
| `HANDSOFF-052` | B | Hands-off URL adaptation (#510) |
| `MATRIX-052` | B | Deployment-matrix check/fixtures (#511) |
| `PDIAG-052` | B | Proactive Posit diagnostics (#512) |
| `ROUTEURL-052` | B | Named-route query/fragment/durable parity (#513) |
| `DOCS-052` | A+B | Protocol, author, Posit deployment, migration docs |
| `AUTHOR-052` | A | External author kit without monorepo import |
| `PKG-052` | A+B | Clean npm/JAR/wheel artifacts; 0.51 upgrade/rollback |
| `SUPPLY-052` | A+B | Checksums, licenses, SBOM/provenance |
| `REGRESS-052` | A+B | Whole-fleet regression; no hidden Deferred claims |

## Alternatives considered

1. **Sibling RFCs for conformance vs Posit.** Rejected for Stage 0: one cut
   baseline and one exit gate; companions stay [#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513).
2. **Replace `hedron-portable-1` in place.** Rejected: extend with
   negotiation; keep `CONTRACT_VERSION` honest.
3. **Restore Supported Connect cookie bridge.** Rejected:
   `drop_supported` from 0.33 remains in force.
4. **Ship full Node/Java Hedron ports.** Rejected: portable subset only.

## Security implications

Untrusted conformance suites and results must not escape sandbox
boundaries. Posit diagnostics never log cookie values; Connect trust
boundaries hold; Supported bridge stays dropped. Stage 0 reserves names
only.

## Testing strategy

Gate scripts `scripts/check_*_052.py` bind evidence. Stage 0 rows are
**Planned**; Stage 1 fills Verified evidence. PKG upgrade source is
**0.51** (`v0.51.2`).

## Compatibility and migration

Public 0.51.2 conformance and Posit imports stay. Pin strings
`>=0.54.0,<0.55` stay until a 0.52 cut. Living tip remains `v0.51.2`
through Stage 0.

## Resolved questions (D-089)

1. **Who owns 0.52?** This RFC under D-089. Tracking
   [#522](https://github.com/eddiethedean/hedron/issues/522). Companions
   [#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513).
2. **Which gates?** The 23 IDs listed above
   (`PROTOCOL-052`…`REGRESS-052`).
3. **Two RFCs or one?** One RFC, two workstreams, one cut.
4. **Portable subset?** Locked: Node/Java evaluate declared profiles only;
   no FastAPI/browser/complete Hedron.
5. **Connect bridge?** Remains `drop_supported`.

## Resolved questions (D-090)

1. **Does Stage 0 refine change the living tip?** No. Living tip stays
   `v0.51.2`. Cut target stays `v0.52.0`.
2. **Which shipped seams does 0.52 consume?** Named above
   (`hedron-portable-1`, `Capability`, `load_bundled_fixtures`,
   `HedronPosit` / `href_for` / `cookie_path_for_mount` /
   `ConnectCookieMode`, planned `PositContext`).
3. **Upgrade source for PKG-052?** **0.51** (`v0.51.2`), not 0.50.
4. **Does this reopen later phases?** No. Do not reopen 0.51 extras,
   Explorer 0.50, `polling_only`, `MORPH-048`, `SR-021`, 0.53, 0.54, or
   schedule `1.0`.

Locks:
[conformance-capability-inventory-052.toml](../acceptance/conformance-capability-inventory-052.toml) ·
[conformance-profile-052.toml](../acceptance/conformance-profile-052.toml) ·
[posit-lifecycle-052.toml](../acceptance/posit-lifecycle-052.toml) ·
[upgrade-fixtures-052.md](../acceptance/upgrade-fixtures-052.md).

## Acceptance criteria

- RFC-0079 and D-089/D-090 are Accepted; tracking
  [#522](https://github.com/eddiethedean/hedron/issues/522) is bound.
- Stage 0 changes contracts only; no 0.52 runtime or version claim.
- Every 0.52-owned gate is Planned with an evidence command name;
  `scripts/verify_pkg_52.py --allow-planned` passes.
- Living tip remains `v0.51.2`.
