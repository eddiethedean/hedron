# Edron 0.1 acceptance packet

**Status:** Draft and blocked; Edron implementation is not authorized and Edron is not published<br>
**Target:** Edron `0.1.0`; compatible Hedron train and release phase unassigned<br>
**Planning baseline:** Hedron workspace `0.66.2`; not an accepted compatibility floor<br>
**Roadmap:** [Edron `0.x` release roadmap](../EDRON_ROADMAP.md)<br>
**RFC:** [RFC-0094](../rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)<br>
**Public API:** [Edron 0.1 public API](../api/EDRON.md)<br>
**State and interaction:** [Edron 0.1 state and interaction](../api/EDRON_STATE_INTERACTION.md)<br>
**Packaging:** [Edron 0.1 packaging](../api/EDRON_PACKAGING.md)<br>
**Capability inventories:** [Edron 0.1 capability inventories](../implementation/EDRON_CAPABILITY_INVENTORIES.md)<br>
**Implementation:** [Edron 0.1 implementation specification](../implementation/EDRON_001.md)<br>
**Golden fixtures:** [Edron golden applications](../implementation/EDRON_GOLDEN_APPS.md)<br>
**Machine gate:** [edron-release-gate-001.toml](edron-release-gate-001.toml)<br>
**Upstream lock:** [edron-upstream-lock-001.toml](edron-upstream-lock-001.toml)

This packet defines the evidence required to accept the Edron design, authorize Edron runtime
implementation, and publish `0.1.0`. It is deliberately fail-closed. The existence of contracts,
code, tests, or a built wheel does not by itself satisfy a gate.

## Current decision

| Decision | Current state | Why |
|---|---|---|
| Accept RFC/design packet | **Blocked** | Native enablement dispositions, numeric budgets, exact package train, machine locks, review owners, and retained evidence are not frozen |
| Authorize separate reusable Hedron enablement | **Not yet authorized by this packet** | Design review must first approve each upstream question and its independent owner/contract |
| Authorize Edron runtime implementation | **Blocked** | All 11 upstream requirements must be Existing/Shipped and every implementation-entry gate Verified |
| Publish Edron `0.1.0` | **Blocked** | No Edron runtime/artifacts/evidence exist and all release gates remain open |

Nothing in this packet changes RFC-0094 from Draft, creates a roadmap phase, publishes a package,
or permits private Edron substitutes for missing native Hedron behavior.

## Three acceptance decisions

### Decision A — design acceptance

Approves the intended Edron 0.1 scope, public vocabulary, state/interaction rules, packaging model,
capability dispositions, implementation boundaries, and evidence plan. It may authorize work on
separately useful Hedron enablement items. It does **not** authorize dependent Edron runtime code.

Decision A requires every `EDR-DESIGN-*` gate Verified.

### Decision B — Edron implementation entry

Authorizes creation of `packages/edron` runtime code only after the design is accepted, every
required native contract is shipped in a frozen compatible train, machine-readable locks and
numeric budgets are complete, fixtures/checkers/CI are available, and no unresolved implementation
blocker remains.

Decision B requires every `EDR-ENTRY-*` gate Verified. Hedron enablement work retains its own RFC,
implementation, release, and evidence authority; this packet cannot mark native work complete.

### Decision C — `0.1.0` publication

Approves built artifacts from a tagged source revision after all public behavior, native
interoperability, HTTP/HTMX/no-JS parity, state, packaging/capabilities, styling, jobs, security,
accessibility, performance, typing, CLI, compatibility, documentation, and human review evidence is
retained and Verified.

Decision C requires every `EDR-RELEASE-*` gate Verified and both prior decisions satisfied.

## Evidence policy

This packet follows the repository [release evidence policy](EVIDENCE.md).

| State | Meaning in this packet | Satisfies a gate? |
|---|---|---|
| `Planned` | Requirement/evidence design exists; implementation evidence is not expected yet | No |
| `Implemented` | Code/artifact exists; required evidence or matrix is incomplete | No |
| `Verified` | Exact command and supported matrix passed with retained artifact and named owner | **Yes** |
| `Deferred` | Explicitly outside 0.1 with owning decision, rationale, destination, and compatibility impact | Only for non-Required scope; never for a Required gate |
| `Blocked` | A named dependency prevents verification | No |

Every Required gate is fail-closed. A checked prose box, local manual observation, workspace-only
test, issue closure, or unretained CI run is status commentary—not evidence.

### Minimum evidence record

Each `Verified` gate records:

- stable gate/requirement IDs and governing contract revision;
- exact local command and CI job/workflow;
- source commit/tag and clean/dirty state;
- Python, platform, server, browser, package-manager, dependency, and adapter dimensions exercised;
- retained immutable report/artifact URL or release-bundle path plus digest;
- owner/reviewer and verification time;
- limitations, excluded/deferred scope, and maturity claim; and
- any waiver with owner, expiry, remediation issue, and proof that it is eligible for waiver.

Critical/high security defects, release-blocking accessibility defects, unsupported compatibility
claims, missing no-JavaScript correctness, private native dependencies, and missing artifact
provenance are not waivable.

## Packet artifact register

| Artifact | Path/current source | State | Required before |
|---|---|---|---|
| RFC/design authority | `docs/rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md` | Planned review | Decision A |
| Golden applications | `docs/implementation/EDRON_GOLDEN_APPS.md` | Planned review | Decision A |
| Public API contract | `docs/api/EDRON.md` | Planned review | Decision A |
| State/interaction contract | `docs/api/EDRON_STATE_INTERACTION.md` | Planned review | Decision A |
| Packaging contract | `docs/api/EDRON_PACKAGING.md` | Planned review | Decision A |
| Capability inventories | `docs/implementation/EDRON_CAPABILITY_INVENTORIES.md` | Planned review | Decision A |
| Implementation specification | `docs/implementation/EDRON_001.md` | Planned review | Decision A |
| Human packet and gate index | this file + `edron-release-gate-001.toml` | Draft | Decision A |
| Upstream lock | `edron-upstream-lock-001.toml` | Blocked: all 11 unresolved | Decision B |
| Machine capability manifest | [edron-capability-manifest-001.toml](edron-capability-manifest-001.toml) | Draft/blocked: dispositions unaccepted; evidence incomplete | Decision A |
| Package/train lock | [edron-package-lock-001.toml](edron-package-lock-001.toml) | Draft/blocked: train and support matrix unfrozen | Decision B |
| Public API snapshot | [edron-public-api-lock-001.toml](edron-public-api-lock-001.toml) | Draft/blocked: signatures and digest unfrozen | Decision B |
| Native lowering matrix | [edron-lowering-matrix-001.toml](edron-lowering-matrix-001.toml) | Draft/blocked: native symbols, versions, and evidence unfrozen | Decision B |
| State/interaction matrix | [edron-state-interaction-matrix-001.toml](edron-state-interaction-matrix-001.toml) | Draft/blocked: upstream contracts, limits, and evidence unresolved | Decision B |
| Golden/focused fixture lock | [edron-fixture-lock-001.toml](edron-fixture-lock-001.toml) | Draft/blocked: sources, hashes, facts, and evidence unfrozen | Decision B |
| Performance/resource lock | [edron-performance-lock-001.toml](edron-performance-lock-001.toml) | Draft/blocked: measurement protocol and every numeric limit unfrozen | Decision A/B |
| Security corpus/ledger schema | planned Edron acceptance/security artifacts | Missing | Decision B/C |
| Human accessibility protocol/ledger | planned `human-at/edron-001/` | Missing | Decision B/C |
| Release evidence bundle | planned tag/CI artifact bundle | Not applicable yet | Decision C |

The seven machine-readable drafts set schemas and expose unresolved work without satisfying any
gate: each records `accepted = false`, `complete = false`, and `locked = false`. An artifact named
“planned” or containing `TBD`, placeholder zeroes, empty required arrays, missing owners, or unbound
commands cannot become Verified. Machine locks contain values and digests, not only links back to
prose.

## Decision A gates — design acceptance

| Gate | Requirement | Minimum evidence | Owner | State |
|---|---|---|---|---|
| `EDR-DESIGN-CONTRACT-001` | RFC scope/goals/non-goals/authority/alternatives/compatibility are approved | RFC review record and accepted revision digest | architecture | Planned |
| `EDR-DESIGN-GOLDEN-001` | Six golden apps have frozen source, native lowering, fallback/state/security/a11y analysis | Golden source/analysis lock and reviewers | product/API | Planned |
| `EDR-DESIGN-API-001` | Root exports, classes, signatures, returns, diagnostics, native identity, and deferrals are frozen | Complete declaration accounting, exact root snapshot, and typing review | API | Planned |
| `EDR-DESIGN-STATE-001` | Owner/lifetime/method/concurrency/idempotency/fallback/HTMX rules are frozen | `EDR-SI-*` trace matrix and state review | interactions | Planned |
| `EDR-DESIGN-PACKAGE-001` | Base batteries, optional/direct/extra semantics, artifacts, import and compatibility rules are frozen | `EDR-PKG-*` matrix and candidate resolver evidence | packaging | Planned |
| `EDR-DESIGN-INVENTORY-001` | Every base/optional/native/tooling/upstream/deferred capability has one disposition | `EDR-INV-*` audit; zero unowned rows | architecture | Planned |
| `EDR-DESIGN-IMPLEMENTATION-001` | Package/modules/compiler/runtime/native integration/stages/tests are implementable without duplicate authority | 87-ID implementation trace review | implementation | Planned |
| `EDR-DESIGN-AUTHORITY-001` | Edron introduces no renderer/router/DI/interaction/state/style/asset/browser/security authority | native authority and dependency-direction review | architecture/security | Planned |
| `EDR-DESIGN-UPSTREAM-001` | Five focused Hedron workstreams partition `UP-001`–`UP-011`, and every row has an Existing or proposed native owner/contract/evidence path | upstream lock with no duplicate, missing, ambiguous, or Edron-local disposition | Hedron maintainers | Blocked |
| `EDR-DESIGN-LIMITS-001` | Numeric output/binding/state/job/diagnostic/package limits are frozen | performance/resource lock with rationale and failure behavior | performance/security | Blocked |
| `EDR-DESIGN-SECURITY-001` | Threat model, trust boundaries, adversarial corpus, redaction and supply-chain plan are approved | security review/corpus index | security | Planned |
| `EDR-DESIGN-A11Y-001` | Semantic/focus/status/no-JS/chart/map/style/human evidence plan is approved | a11y matrix and scoped human protocol | accessibility | Planned |
| `EDR-DESIGN-PERF-001` | Native-comparison metrics/budgets and measurement method are frozen | performance lock and benchmark design | performance | Blocked |
| `EDR-DESIGN-EVIDENCE-001` | Every normative ID maps to owner, command class, CI lane, retained artifact type | machine release-gate completeness check | release | Planned |
| `EDR-DESIGN-DOCS-001` | Design packet links, terminology, status, examples, and strict build agree | strict docs/link/example/drift checks | docs | Planned |
| `EDR-DESIGN-DECISION-001` | Required reviewers sign the exact digests and explicitly authorize Decision A only | retained decision record | release/architecture | Blocked |

Decision A does not pass with a Required gate Deferred. A proposal to remove a Required 0.1
surface must update the RFC, every companion contract/inventory, goldens, machine locks, migration
impact, and review digest before the gate can be reconsidered.

## Decision B gates — Edron implementation entry

| Gate | Requirement | Minimum evidence | Owner | State |
|---|---|---|---|---|
| `EDR-ENTRY-DESIGN-001` | Every Decision A gate is Verified | machine gate validation at accepted digests | release | Blocked |
| `EDR-ENTRY-UPSTREAM-001` | All 11 native requirements are Existing/Shipped in the required train | public symbols/contracts, release versions, conformance commands/artifacts | Hedron owners | Blocked |
| `EDR-ENTRY-TRAIN-001` | Exact mutually compatible Python/Hedron/data/charts/maps/server/parser/sanitizer train is locked | clean pip/uv resolution on supported candidate matrix | packaging | Blocked |
| `EDR-ENTRY-MANIFESTS-001` | Capability/package/API/lowering/state/fixture/performance locks are complete and mutually consistent | machine drift checker | release/tooling | Blocked |
| `EDR-ENTRY-FIXTURES-001` | Golden and focused positive/negative/native/no-JS source fixtures are frozen before implementation | fixture lock with source hashes and expected native facts | testing | Blocked |
| `EDR-ENTRY-CI-001` | Test lanes/checkers can collect empty/scaffold evidence and fail missing/duplicate/fake Verified rows | checker self-tests and CI workflow review | release/CI | Blocked |
| `EDR-ENTRY-SECURITY-001` | Threat corpus and artifact/import/package attack harness are ready | executable corpus inventory and owner sign-off | security | Blocked |
| `EDR-ENTRY-A11Y-001` | Automated and human protocol, tasks, privacy, ledger schema, environments are ready | protocol checker and accessibility sign-off | accessibility | Blocked |
| `EDR-ENTRY-ZERO-BLOCKERS-001` | No `Enable`, unknown owner, TBD budget/range, private native seam, or undocumented Required deferral remains | cross-packet fail-closed checker | architecture/release | Blocked |
| `EDR-ENTRY-AUTHORIZATION-001` | Maintainers explicitly authorize `packages/edron` implementation at exact locks/digests | retained implementation-entry decision | release/architecture | Blocked |

Decision B authorizes implementation, not publication. Each Edron slice still requires its native
prerequisite and tests. A scaffold may not export a planned feature merely because later stages are
expected to implement it.

## Decision C gates — `0.1.0` publication

| Gate | Requirement | Minimum evidence | Owner | State |
|---|---|---|---|---|
| `EDR-RELEASE-RUNTIME-001` | Definition compiler, request frames, buffers, descriptors and all public methods meet implementation requirements | unit/integration/concurrency reports | Edron implementation | Blocked |
| `EDR-RELEASE-API-001` | Exact root/signature/typing/return/diagnostic snapshot passes with no accidental exports | API/typing snapshot command/artifact | API | Blocked |
| `EDR-RELEASE-NATIVE-001` | Exact native objects/registries/routes/effects/styles/assets and mixed composition pass | differential/native identity matrix | architecture/Hedron | Blocked |
| `EDR-RELEASE-HTTP-001` | Full page/filter/fragment/action/form/job/download paths preserve HTTP/HTMX/no-JS meaning | raw ASGI/browser/no-JS matrix | interactions | Blocked |
| `EDR-RELEASE-STATE-001` | Request/session/cache/durable/job/browser ownership, restart and multi-worker claims pass | state/concurrency/backend reports | state | Blocked |
| `EDR-RELEASE-CAPABILITY-001` | Base batteries and every optional absent/direct/extra/incompatible/broken lane pass | clean environment capability matrix | packaging/adapters | Blocked |
| `EDR-RELEASE-STYLE-001` | themes/variants/recipes/scopes/CSS/native packages/adapters/CSP/modes pass | style reports, browser/visual/a11y artifacts | styling | Blocked |
| `EDR-RELEASE-JOB-001` | Job backend/scope/poll/cancel/result/download/production gate pass | native job integration and multi-worker evidence | jobs | Blocked |
| `EDR-RELEASE-SECURITY-001` | All security requirements/corpus pass with zero unwaivable finding | retained security report/advisory/SBOM/provenance | security | Blocked |
| `EDR-RELEASE-A11Y-001` | Automated and scoped human evidence pass with honest claim limits | browser/axe/semantic reports + redacted human ledger | accessibility | Blocked |
| `EDR-RELEASE-PERF-001` | Every frozen native-comparison and resource budget passes | retained benchmark/package/import reports | performance | Blocked |
| `EDR-RELEASE-TYPING-001` | Supported Python/type-checker matrix validates all positive/negative/golden/native cases | retained typing reports | typing | Blocked |
| `EDR-RELEASE-CLI-001` | run/check/register/explain/doctor/style commands, trust boundaries, formats and exit codes pass | CLI/static/import/report matrix | tooling | Blocked |
| `EDR-RELEASE-GOLDEN-001` | Six goldens plus focused map/editor/state/native/optional/CLI fixtures pass | fixture lock verification and artifacts | testing | Blocked |
| `EDR-RELEASE-PACKAGE-001` | Wheel/sdist metadata/assets/typing/licenses/clean install/offline import/build/provenance pass | external clean artifact matrix and digests | packaging | Blocked |
| `EDR-RELEASE-UPGRADE-001` | Compatible install/upgrade/invalid-train/uninstall/rollback and native-only use pass | upgrade/rollback fixture reports | release | Blocked |
| `EDR-RELEASE-DOCS-001` | Tutorials/API/state/package/native/styling/deployment/migration/troubleshooting match artifacts | strict docs, snippets, links and availability audit | docs | Blocked |
| `EDR-RELEASE-HUMAN-001` | Architecture, security, accessibility, package and release humans sign exact evidence bundle | retained signed decision/ledger references | release | Blocked |
| `EDR-RELEASE-REGRESS-001` | Full required Hedron/Edron regression suite passes on release source/artifacts | retained CI matrix | release | Blocked |
| `EDR-RELEASE-PUBLISH-001` | Tagged artifacts/hashes/provenance are verified and publication/rollback procedure is ready | release-candidate rehearsal and final explicit decision | release | Blocked |

## Upstream Hedron acceptance lock

The machine source is [edron-upstream-lock-001.toml](edron-upstream-lock-001.toml). The eleven
requirements are grouped into five independently reviewable Hedron workstreams; every workstream
and requirement remains Blocked/Unresolved.

| Workstream | Requirements | Native outcome | Primary owners |
|---|---|---|---|
| `HEDRON-WS-CLASS` | `UP-001`, `UP-003` | reusable fresh-instance class compilation and dependency binding | application compiler and DI |
| `HEDRON-WS-INTERACTIONS` | `UP-002`, `UP-004`–`UP-006` | one HTTP/HTMX/no-JS filter, fallback, confirmation, and success model | routing/forms/actions/responses/security/a11y |
| `HEDRON-WS-PROVENANCE` | `UP-007`, `UP-011` | exact native handle lookup plus bounded external-facade provenance in native reports | registry/diagnostics/style tooling |
| `HEDRON-WS-JOBS` | `UP-008` | reusable application-oriented `TaskFlow` lifecycle | tasks/jobs |
| `HEDRON-WS-STYLING` | `UP-009`, `UP-010` | registry-derived variants and cross-package theme parity | core/data/charts/maps/styling |

Workstream grouping is scheduling and ownership structure, not a resolution shortcut. Each
constituent `UP-*` row still needs its own public contract/symbol, evidence, resolution, and shipped
version. A workstream may ship independently, but Decision B still requires all eleven rows.

| ID | Required native authority | Blocks | Verification needed before Decision B |
|---|---|---|---|
| `UP-001` | fresh-instance class compiler for page members/signatures/async/handles | page/fragment/action compilation | public contract/symbol, atomic plan, lifecycle/conformance, shipped version |
| `UP-002` | coherent typed GET filter plan | named controls/filter scopes/history | public plan schema/builder, HTTP/HTMX/no-JS/race evidence, shipped version |
| `UP-003` | class dependency descriptor | `ed.dependency` | DI/override/cleanup/static/shadow tests, shipped version |
| `UP-004` | owning-screen action fallback | default action/PRG | unsafe method/CSRF/validation/redirect tests, shipped version |
| `UP-005` | accessible unsafe confirmation | `confirm=` | keyboard/focus/cancel/no-JS/security evidence, shipped version |
| `UP-006` | success outcome parity | `ed.success` | HTMX/ordinary status/presentation/error evidence, shipped version |
| `UP-007` | facade source/binding to exact native handle lookup | `app.native`, explain | registry schema/identity/collision/source-redaction evidence, shipped version |
| `UP-008` | extended native `TaskFlow` | `JobFlow` | backend/scope/result/poll/production/no-JS evidence, shipped version |
| `UP-009` | native recipe-family variant metadata | `variant=` | registry mapping/version/explanation/collision evidence, shipped version |
| `UP-010` | shared brand/theme contract across core/data/charts/maps | Edron theme guarantee | cross-package token/mode/a11y/asset evidence, shipped versions |
| `UP-011` | external facade provenance in native style/registry reports | explain/style tooling | shared report schema/source/redaction/diff evidence, shipped version |

“Existing” requires the exact public symbol and evidence; an internal/private/similar implementation
does not satisfy the row. “Shipped” requires the accepted release/artifact train, not only code on a
branch. Edron cannot own the native evidence command for these gates.

## Fixture and coverage lock

### Required golden fixtures

| Fixture | Required proof beyond “renders” |
|---|---|
| Hello | clean base install, import, page/title/text/theme, server, semantic full page, no network/Node |
| Sales dashboard | layout, metric, dataframe, first-party chart, coherent GET filters, fragment/cache/history/races/fallback |
| Customer CRUD | DI, Pydantic form, auth/CSRF/binding/confirmation/idempotency/revision/effects/PRG/a11y |
| Report job | backend/scope/submit/status/poll/cancel/result/download/no-JS/terminal/multi-worker production gate |
| Plotly | absent/direct/extra/incompatible/broken, exact remediation, explicit no-fallback, native maturity/assets |
| Styling | theme/variants/recipes/scopes/CSS/native packages/third-party limitations/CSP/modes/inspect/diff |

### Required focused fixtures

- simple map geometry, local UI assets, explicit tile/data network policy, CSP, description/fallback;
- native `hedron-data` editor access and a negative test proving no Edron editor claim;
- pandas, Polars, PyArrow, Altair, Matplotlib, and SQLAlchemy capability matrices;
- native component, fragment, action, feature, route, theme/style, session/cache/job composition;
- dependency cleanup/overrides/shadowing and concurrent fresh-instance/context teardown;
- cache scopes/invalidation/restart, typed sessions, multi-worker job scope, downloads/ranges;
- CLI static versus trusted import, JSON/SARIF, redaction, optional probe, source/observed facts;
- wheel/sdist external installs, invalid trains, upgrades, uninstall/rollback, offline import/assets;
- every Deferred/rejected API name as a negative source/import/typing/runtime test; and
- security, accessibility, browser, no-JS, and native performance differential corpora.

Fixture locks record source hashes, governing capability IDs, expected native routes/handles/
methods/targets/effects/assets/state, supported matrix, maturity/limitations, and evidence command.
Snapshots alone do not substitute for semantic/raw HTTP assertions.

## Compatibility matrix

The matrix is **candidate scope**, not accepted support, until `EDR-ENTRY-TRAIN-001` is Verified.

| Dimension | Candidate/required disposition | Current state |
|---|---|---|
| Python | 3.11, 3.12, 3.13, 3.14 consistently with accepted Hedron train | Unverified |
| Platforms | Linux required; supported macOS/Windows architectures must be explicitly frozen | Unfrozen |
| ASGI/server | native FastAPI/Starlette + selected bundled development server range | Unfrozen |
| Package managers | clean `pip` and `uv` installation/resolution; neither is runtime authority | Unverified |
| Hedron packages | exact bounded `hedron`, `hedron-data`, `hedron-charts`, `hedron-maps` train | Unfrozen |
| Browsers | Chromium, Firefox, WebKit for supported enhanced journeys; raw HTTP/no-JS authoritative | Unverified |
| HTMX | native supported HTMX with Hedron extension present/absent; no Edron dialect | Unverified |
| Type checkers | supported checker/version matrix must be frozen before entry | Unfrozen |
| Optional adapters | seven curated capabilities in absent/direct/extra/incompatible/broken lanes | Unverified |
| Deployment | single/multi-worker claims, root path/proxy, production security, restart/rollback | Unverified |

Unsupported dimensions remain explicit and cannot inherit a compatibility claim from Hedron or an
optional dependency.

## Security acceptance matrix

At minimum the retained adversarial corpus covers:

| Boundary | Required attacks/failures |
|---|---|
| registration/compiler | class/descriptor spoofing, collisions, late seal, dynamic attributes, annotation/source abuse, partial commit |
| request frame/output | cross-app/page/request/container use, detached tasks, cancellation, partial output, budget exhaustion |
| binding/forms/actions | duplicate/extra/missing values, dependency shadowing, hidden-field tamper, CSRF, authz/tenant, body/upload limits |
| interactions | target/selector/redirect/OOB forgery, stale/replay/double submit, idempotency payload mismatch/store outage, conflicts |
| state/cache/session | public/private/tenant leakage, poisoning, secret keys, restart/multi-worker mismatch, invalid migration/expiry |
| jobs/downloads | enumeration, cross-scope IDs, cancellation races, result/path traversal, header/range/filename abuse, retention |
| content/styles/assets | XSS/trust escalation, Markdown sanitization, CSS/path/root injection, CSP/integrity, duplicate/remote assets |
| capabilities/packages | dependency confusion, version skew, malicious metadata/import/entrypoint, broad ImportError, command injection, runtime install |
| tooling/diagnostics | untrusted import confusion, source/path/secret leakage, SARIF/JSON injection, callback execution in static/explain paths |

Release requires zero unwaived critical/high findings and no medium finding that invalidates a
Supported security claim. Security evidence names the tested artifact, not only workspace code.

## Accessibility and human acceptance

Automated evidence covers semantics/names/states, labels/errors, keyboard/focus/busy/announcements,
no-JS, reflow/zoom, contrast/modes, forced colors, reduced motion, RTL/print, charts/maps data
alternatives, HTMX swaps, confirmation, conflict/delete recovery, and polling rate.

Before Decision B, a scoped human protocol freezes:

- representative tasks from all six goldens plus map/native composition;
- desktop/mobile viewport, keyboard-only, screen-reader/browser, zoom/high-contrast/motion modes;
- privacy/consent, private versus repository evidence, redaction, retention, and withdrawal policy;
- pass/fail/severity/retest rules and claim limitations;
- ledger schema with environment, artifact digest, task result, findings, remediation, reviewer; and
- a packet checker that distinguishes placeholder/example rows from completed sessions.

Decision C requires the accepted sessions/retests for the Supported claim. Automated axe success
or an unexecuted protocol is not human evidence.

## Performance and resource lock

Exact numbers remain a blocking Stage 0 task. The lock must freeze measurement method, warm/cold
mode, hardware/runner class, input fixture, repetitions/statistic, native comparator, threshold,
failure behavior, and retained report for:

- Edron wheel/base environment compressed/uncompressed size;
- cold/warm root import time, memory, and imported modules;
- class registration time per page/fragment/action and peak allocation;
- full-page/fragment/action latency and allocations versus equivalent native Hedron;
- request lowering cost per node/control/binding/target and maximum counts/bytes/depth/fan-out;
- generated HTML/metadata/trace/source-map/assets raw/gzip size and duplication;
- optional capability negative/success import time and retained cache bounds;
- state/cache/session/job/download/idempotency limits and retention;
- CLI check/register/explain/doctor/style time/memory/output size; and
- resolver/install/build time and artifact reproducibility.

Zero, infinity, “reasonable,” inherited limits without proof, or thresholds added after benchmarks
run cannot satisfy the gate. A regression may be accepted only by revising the contract/lock before
release with user impact and native comparison.

## Documentation and availability audit

Decision C documentation must include:

- installation/quickstart and explicit “not Streamlit reruns” mental model;
- class/page/output/layout/display/input/filter/fragment/action/form/dependency/state/job APIs;
- native Hedron interoperability and ejection/mixed composition;
- styling ladder from built-in theme through native recipes/scopes/CSS;
- base versus optional packages, direct install, extras shortcuts, missing/incompatible/broken help;
- HTTP/HTMX/no-JS, concurrency/idempotency/conflict, security and accessibility behavior;
- development versus production server/deployment/worker/session/cache/job guidance;
- migration from Streamlit and from native Hedron in both directions;
- CLI/static trusted-import boundaries and troubleshooting/error codes;
- exact maturity/limitations/unsupported platforms/adapters/features; and
- a current release/support page that does not describe Draft/Deferred surfaces as available.

All code snippets parse/type-check/run in their declared environment. Strict docs/link checks may
report intentionally excluded RFC/implementation files as informational, but no broken public link
or stale availability claim is allowed.

## Planned evidence commands

The commands below are required interfaces for future checkers; they do not exist yet and are not
evidence today:

```console
python scripts/check_edron_001.py --stage design --verify
python scripts/check_edron_001.py --stage implementation-entry --verify
python scripts/check_edron_001.py --stage release --verify
python scripts/check_edron_001.py --gate EDR-RELEASE-NATIVE-001 --verify
python scripts/check_edron_001.py --audit-drift
```

The checker must validate schema/version, unique IDs, valid states, artifact existence/digests,
owner/command/CI/matrix/retention for Verified rows, rationale/destination for Deferred rows, named
dependencies for Blocked rows, zero placeholders in accepted locks, contract requirement coverage,
and consistency with built package metadata. `--allow-planned` may validate packet scaffolding but
cannot return implementation-entry or release-ready.

## Sign-off roles

| Role | Decision A | Decision B | Decision C |
|---|---|---|---|
| RFC/architecture owner | required | required | required for authority/interop |
| Hedron native owners | upstream dispositions | all required native releases | native regression/compatibility |
| Edron API/implementation owner | contract/spec | entry locks/fixtures | runtime/API/goldens |
| Security | threat/evidence plan | corpus readiness | artifact report/sign-off |
| Accessibility | matrix/human plan | protocol readiness | automated + human sign-off |
| Packaging/release | package/evidence plan | train/manifests/CI | artifacts/provenance/publish |
| Performance | metric/budget design | frozen locks/harness | retained passing reports |
| Documentation | packet consistency | implementation-facing docs plan | release docs/availability audit |

One person may hold multiple roles, but the evidence record names the role explicitly. Automated
checks do not replace human design/security/accessibility/release decisions.

## Change control

After Decision A, a material change to public vocabulary, state owner, HTTP method/fallback,
security/accessibility meaning, base/optional packaging, native authority, capability maturity,
required platform, or performance budget requires:

1. RFC/decision update under the repository lifecycle;
2. synchronized API/state/package/inventory/implementation/acceptance edits;
3. regenerated machine locks/digests and affected fixtures;
4. compatibility/migration analysis; and
5. renewed sign-off for the invalidated decision(s).

Implementation discoveries cannot silently weaken a gate. If native support is infeasible, defer
or remove the Edron feature through review rather than introducing a hidden fallback.

## Final release rule

Edron `0.1.0` is release-ready only when the machine gate reports:

```text
design_accepted = true
implementation_authorized = true
release_ready = true
all Required gates = Verified
all Deferred rows = explicitly outside 0.1 with owner/rationale/destination
zero Blocked/Planned/Implemented Required gates
zero undocumented public capabilities or private native dependencies
```

The current packet reports all three decisions false. That is the correct status for a pre-coding
design packet.

## See also

- [Release evidence policy](EVIDENCE.md)
- [Acceptance specifications index](README.md)
- [RFC-0094](../rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)
- [Edron implementation specification](../implementation/EDRON_001.md)
- [Edron capability inventories](../implementation/EDRON_CAPABILITY_INVENTORIES.md)
- [Edron packaging](../api/EDRON_PACKAGING.md)
- [Edron state and interaction](../api/EDRON_STATE_INTERACTION.md)
- [Edron public API](../api/EDRON.md)
