# Hedron `v1.3.0` first-class UI testing acceptance plan

**Status:** Candidate source verified on `dec75e9ab60a5632ce9d63d8662f01589e2ccb4d`; all 16 non-release gates have current retained evidence, and release approval/cut/tag/publication remain pending
**Planning revision:** 2026-10-28
**Planning baseline:** Published `v1.2.0`
**Required release predecessor:** `v1.2.0` — PyPI publication verified
**Compatibility baseline:** Stable `v1.0.0` testing inventory plus additive 1.x behavior
**Authority:** [RFC-0097](../rfcs/RFC-0097-FIRST-CLASS-UI-TESTING.md)
**Implementation:** [UI_TESTING_1_3](../implementation/UI_TESTING_1_3.md)
**Machine packet:** [release-gate-1.3.toml](release-gate-1.3.toml)
**Planning contract:** [ui-testing-contract-130.toml](ui-testing-contract-130.toml)
**Package dispositions:** [ui-testing-package-dispositions-130.toml](ui-testing-package-dispositions-130.toml)
**Behavior/accessibility inventory:** [ui-testing-inventory-130.toml](ui-testing-inventory-130.toml)
**Skip policy:** [ui-testing-skip-policy-130.toml](ui-testing-skip-policy-130.toml)

The candidate implementation includes the direct-Page testing surface, spawned ASGI host, explicit
pytest plugin, structured failure manifests, packaged sample app, and browser tests. The
[local vertical-slice record](evidence-130/LOCAL_VERTICAL_SLICE_2026-10-28.md) reports 31 passing
tests on each local browser engine. The accepted scope/API contract and package dispositions are
bound to the maintainer acceptance record. The current release ledger records 16 non-release gates
as Verified; `RELEASE-130` remains Planned until release approval and the release cut are recorded.

Strict release validation binds every Verified gate to retained evidence, its SHA-256, and the tested
source revision. The evidence-only record may follow that source revision under
`docs/acceptance/evidence-130/`, with the gate and this plan; strict validation requires a clean
tree. The ledger retains the v1.2.0 publication record, accepted frozen contract, measured budgets,
complete package dispositions, reproducible artifact manifest, and upgrade/rollback rehearsal.
Release approval remains empty, `release_cut_satisfied` is false, and no tag or publication is
authorized by this candidate packet.

## Entry and release dependencies

The maintained sequence requires the published 1.2 Python baseline and its release evidence.
`predecessor_satisfied` is bound to the publication verification at
[evidence-120/PUBLICATION.md](evidence-120/PUBLICATION.md). Implementation and freeze evidence are
complete on the candidate source. A release still requires the explicit release decision and
release-cut evidence.

FREEZE-130 requires actual results for process startup/root-path/cleanup, pytest-playwright context
and capture ownership, checkpoint/event capability coverage, capture-resource limits, dependency/
browser revisions, fresh-user/typing exercises, named maintainers, and measured budgets. The
accepted contract marks the freeze satisfied and all seven required numeric budgets Measured and
frozen. The version-aware [release gate checker](../../scripts/check_release_gate.py) selects the
1.3 ledger, accepts Planned rows only in candidate mode, and rejects incomplete evidence in strict
release mode.

## Candidate evidence history — 2026-10-29

CI run [40918890605](https://github.com/eddiethedean/hedron/actions/runs/40918890605) passed on
Linux x86_64 at source revision `825f31c8af6e1c446995dbff8be30738b634b22c`. It exercised all 13
required host cases on CPython 3.11.15–3.14.6, and all 27 required inventory cases on pinned
Chromium, Firefox, and WebKit rows running Python 3.12.13. The browser rows passed behavior,
accessibility, skip-classification, and resource-budget checks. The same run passed the structured
privacy and synthetic capture probes; a local scan of its downloaded 49-file artifact set found
zero randomized canary-token matches. Details, metrics, and artifact identities are in the
[retained resource and matrix evidence](evidence-130/ui-testing-resource-budgets-2026-10-29.json).

That run’s minimum/latest dependency jobs installed stable dependencies and passed their adapter
suite; they did not include the optional UI-testing extra. Follow-up CI run
[40922256179](https://github.com/eddiethedean/hedron/actions/runs/40922256179) passed on source
revision `ee72dd904b4aefef74a62c7a1521484d78646837`, including the extended minimum/latest jobs.
Both rows installed `hedron[testing]`, explicitly loaded Hedron’s pytest plugin, and passed the
selected adapter plus UI-testing suites (333 passed, 11 skipped each). The minimum row resolved
pytest 8.3.0, pytest-playwright 0.10.0, Playwright 1.62.0, and Uvicorn 0.46.0; the latest row
resolved 9.2.0, 0.10.0, 1.64.1, and 0.54.0. Browser end-to-end tests remain on the separately
pinned Playwright 1.62.0 matrix. All checks in the follow-up run passed. The
[retained evidence](evidence-130/ui-testing-resource-budgets-2026-10-29.json) records its artifact
identities and a zero-hit scan across 49 downloaded files. The source revision and CI results are
candidate evidence; release approval was still open after that run.

An earlier full CI run [40924535172](https://github.com/eddiethedean/hedron/actions/runs/40924535172)
passed on source revision `008959155f6426b5239069bd8bd4cd93323d8e28`, including quality/docs checks
of the evidence-backed contract state. Its host, browser, bounds, packaging, integration,
supply-chain, and required aggregate results are retained in
[ci-run-40924535172.json](evidence-130/ci-run-40924535172.json). The 49 downloaded artifact files
were scanned for randomized privacy-canary values with zero matches. That run is historical evidence
superseded by the final candidate run below.

## Previous candidate verification — 2026-10-29 (`e76f595d`)

The first candidate evidence run, [40937671727](https://github.com/eddiethedean/hedron/actions/runs/40937671727), passed on source revision `4dbab1ea7c511b56058eca5d2da8297c43b1d059`. An intervening run, [40941629675](https://github.com/eddiethedean/hedron/actions/runs/40941629675), exposed a stale release-gate test assertion after maintainer acceptance changed `FREEZE-130` to Verified. The assertion was corrected in the tested source below; this is recorded as CI history, not candidate evidence.

CI run [40942185662](https://github.com/eddiethedean/hedron/actions/runs/40942185662) completed successfully on the exact candidate source revision `e76f595db5cf1643b05bf6124dbf970a8741b806`. All 18 workflow jobs passed, including `CI required`. This covers Linux CPython 3.11.15–3.14.6, pinned Linux Chromium 151.0.7922.34, Firefox 153.0, and WebKit 26.5, minimum/latest testing-extra bounds, quality and strict typing, package rehearsals, Workbench and Connect integration smokes, and the supply-chain bundle.

Each Python host row passed all 55 cases, including all 13 required host cases, with no skips. Maximum measured startup was 0.95–1.15 seconds, shutdown was 0.33–0.39 seconds, and each host used one child process. Each browser row passed all 27 required behavior/accessibility cases. Overall browser suites had 216 collected cases per engine; 79–81 skips were classified as unselected-engine cases, retired historical APIs, separate privacy/capture lanes, or the Chromium-only style check. No required case was skipped. Browser runs completed in 279–528 seconds; peak private temporary trees were 44.5–84.4 MB within the 128 MiB private tmpfs cap and 1,800-second timeout.

The isolated synthetic capture probes retained valid failure traces (195–220 kB), surfaced the over-limit error, and terminated an over-budget profile within the frozen overshoot bound. Structured privacy probes passed on all three engines with no leaked canary categories or unexpected native output. A scan of all 142 extracted files from the retained run artifacts found zero randomized canary-token matches.

The minimum and latest dependency-bound jobs explicitly loaded `-p hedron.testing.pytest_plugin`; each passed 335 tests with 11 classified skips. The minimum row resolved pytest 8.3.0, pytest-playwright 0.10.0, Playwright 1.62.0, pytest-xdist 3.6.1, and Uvicorn 0.46.0. The latest row resolved pytest 9.2.0, pytest-playwright 0.10.0, Playwright 1.64.1, pytest-xdist 3.8.0, and Uvicorn 0.54.0. The browser matrix remains pinned to Playwright 1.62.0.

The 22 coordinated packages produced 44 distributions in two byte-identical builds. Independent verification from a clean checkout of candidate source matched all 44 approved hashes in each retained build. The CPython 3.11 upgrade rehearsal passed from v1.2.0 to v1.3.0 and rolled back to v1.2.0 with the original lock restored. The versioned [artifact hash ledger](evidence-130/python-artifacts-40942185662.json) and [upgrade/rollback record](evidence-130/upgrade-rollback-40942185662.json) are retained with the [CI summary, job identities, and artifact digests](evidence-130/ci-run-40942185662.json). GitHub retains these run artifacts through 2027-01-27.

The owner accepted the exact scope/API contract and package dispositions. That acceptance does not approve release. `RELEASE-130` stays Planned; `release_approval.approved` and `release_cut_satisfied` remain false, and no 1.3.0 tag or publication has been made.

## Current candidate verification — 2026-10-29

The final release-CI repair is at source revision `dec75e9ab60a5632ce9d63d8662f01589e2ccb4d`. PR CI run [40973136018](https://github.com/eddiethedean/hedron/actions/runs/40973136018) passed every required job: coverage, strict typing/docs, packaging, both dependency bounds, bounded host acceptance on CPython 3.11–3.14, and the complete Chromium/Firefox/WebKit browser acceptance matrix. The supply-chain evidence job and candidate artifact rehearsal also passed. The separate full CI dispatch [40973327693](https://github.com/eddiethedean/hedron/actions/runs/40973327693) passed the general test suite on CPython 3.11–3.14 and the full CI matrix. Native wheel matrix [40973135817](https://github.com/eddiethedean/hedron/actions/runs/40973135817) passed on Linux x86_64, Linux ARM64, macOS ARM64, and Windows.

The current [CI summary and retained acceptance reports](evidence-130/ci-run-40973136018.json) bind the 16 verified non-release gates to `dec75e9`. It retains the host/browser case reports, resource budgets, privacy and capture probes, supply-chain bundle, and run artifact identities. The current [Python artifact ledger](evidence-130/python-artifacts-40973136018.json) records 22 coordinated packages and 44 distributions, byte-identical repeated builds, and the [CPython 3.11 upgrade/rollback rehearsal](evidence-130/upgrade-rollback-40973136018.json), which passed baseline, upgrade, and rollback with the original lock restored. GitHub retains the run artifacts through 2027-01-27.

`RELEASE-130` remains Planned until the release decision. `release_approval.approved` and `release_cut_satisfied` remain false; no tag or publication has been made. The candidate is technically prepared for the release decision, with the approval and cut record intentionally pending.

## Required gates

| Gate | Owner role | Required evidence |
|---|---|---|
| `FREEZE-130` | architecture | Source/export/task inventory, direct-Page prototype/user exercise, owned-host/context/capture/settle probes, exact candidate API/typing, named maintainers, complete dispositions, dependency/browser/host matrix, schemas, measured numeric budgets, exact commands/artifacts; no unresolved authority issue or Unmeasured Required budget. |
| `CONTRACT-130` | testing | Three testing layers; native Page/Locator/expect; explicit central plugin activation; sync fixture/session scope; child/app and upstream context ownership; no wrapper DSL, second runner, shared live app, runtime instrumentation, or premature Stable promotion. |
| `HOST-130` | testing | Spawned importable ASGI factory; child-owned retained port-zero loopback listener; readiness after lifespan; real root-path/static/override parity; bounded graceful/forced cleanup; startup/fixture failure, interruption, xdist; caller-owned loopback external mode with unavailable server facts. |
| `LOCATOR-130` | testing | Native Playwright semantic lookup and assertions, strict mark/region Locators, dynamic re-query after swap, ambiguity diagnostics, shadow/specialist boundaries, and direct Page/context interoperability; no get_by/expect clone. |
| `SETTLE-130` | browser-platform | Pre-action checkpoint with session/navigation epoch; require actual matching start; scoped response/abort/204/swap/settle/generation facts; fast request, supersession, OOB/removal, unknown capability and hung start/end; no global idle, future poll tick wait, fabricated readiness, or sleeps in new/adopted examples. |
| `ERROR-130` | testing | Automatic session/fixture clean check; managed server/page/crash/console/HTTP/asset/network policy; canceled-request distinctions; narrow exact-count expected-HTTP scope; missing expectation failure; external facts unavailable; preserve primary test error plus capture/teardown secondary errors. |
| `ARTIFACT-130` | testing | Versioned structured-only default manifest; separate explicit synthetic unredacted native capture; pre-creation upstream flag validation and one capture owner; recording-versus-retention distinction; bounded safe private temporaries/overshoot, atomic writes, disabled/unavailable/truncated/capture-failed markers, and no upload. |
| `PYTEST-130` | tooling | Additive testing extra and explicit root-conftest/-p registration; supported pytest-playwright fixtures/options; one context lease/finalizer contract; no monkey patch; collection/no-binary behavior versus fail-on-missing selected browser; setup/call/teardown, xdist/rerun artifacts, no unrequested host/browser startup. |
| `SATELLITE-130` | packages | Every coordinated/optional package has an explicit disposition; one minimal useful specialist contribution proves v1 identity/schema/capability/fixture metadata, explicit loading, absence/disabled/version/conflict/fleet behavior; stable re-exports/import isolation; no mandatory public modules/managed WSGI or duplicate harness/plugin authority. |
| `BEHAVIOR-130` | reference-app | Early Chromium secured-form/intentional-failure slice before satellite breadth, then bounded current PAGE/fragment/OOB/history/form/CSRF/auth/local/request/combined/element/upload/download/poll/action/no-JS/asset-failure corpus; no implementation of 1.4–1.7 features. |
| `A11Y-130` | accessibility | Native semantic/keyboard/focus/announcement, mode/viewport, zoom/reflow and no-JS fixtures; axe engine/version/scope/incomplete/error evidence and deliberate violation; no WCAG/human-AT completion claim. |
| `SECURITY-130` | security | Literal-loopback app/browser origins, fail-closed redirect responses, and service-worker/capability dispositions; test correlation cannot bypass app auth/CSRF; structured-only confidential canary proof; no raw trace redaction promise or remote capture; artifact paths/isolation and honest browser-versus-server-egress limits. |
| `PERF-130` | performance | Retained cold/warm startup/context/settle/cleanup and xdist baselines; frozen numeric event/artifact/private-disk/overshoot/time/worker/CI budgets and exact/over-limit behavior; capture overhead measured by profile; forced termination remains failed cleanup. |
| `COMPAT-130` | compatibility | Stable 1.0 and additive 1.x testing exports/behavior preserved; 1.2 Python baseline; base/core import without browser/pytest; sync Linux target matrix and explicit OS/host pilots; supported upstream min/max bounds and pinned browser revisions; no full Cartesian/managed-adapter parity claim. |
| `DOCS-130` | docs | One packaged synthetic test-app factory and scaffold example; testing pyramid, explicit activation/install, direct Page, checkpoint/expected failure, capture/resource/privacy/cleanup limits, debug/CI and opt-out; optional browser testgen/doctor do not block cut; current-availability labels honest. |
| `PKG-130` | packaging | Clean base/browser/testing-extra wheels/sdists/offline install/import/typing matrix on CPython 3.11–3.14; upstream fixture/capture options, missing-extra/browser diagnostics, bounded packaged resources, compatible versions and notices; no optional dependency leak or base pytest11 side effect. |
| `RELEASE-130` | release | All other Required rows Verified; v1.2.0 predecessor evidence, accepted exact contract and immutable artifacts, upgrade/opt-out/rollback and maturity/limits, explicit release approval; no skipped Required browser row or future feature claim. |

## Required versus optional scope

| Required in the first cut | Optional / Deferred from Required scope |
|---|---|
| Sync pytest and direct Playwright, explicit plugin/testing extra | Asyncpytest or standalone non-pytest lifecycle, wrapper locator/assertion API |
| Spawned flagship ASGI factory and literal-loopback external URL | Live app/closure serialization, managed WSGI/Posit launchers, remote server/browser capture |
| Structured-only default and separate explicit synthetic capture corpus | Claimed generic trace/DOM/screenshot redaction, visual baseline comparison framework |
| Complete all-package disposition inventory and one explicit sample-kit contribution | Public testing modules and executable host providers for every satellite |
| One packaged/scaffold example and bounded existing reference adoption | Browser testgen, testing doctor, all-historical-test sleep removal |
| Existing runtime behavior and test-only observation | Runtime APIs, instrumentation, or feature semantics belonging to 1.4–1.7 |

No existing accepted stable obligation is removed. The accepted scope records the included surfaces;
new 1.3 testing APIs remain Beta candidates for release.

## Required vertical slice and failure matrix

The first synthetic profile slice passes locally in Chromium, Firefox, and WebKit. Hosted Linux CI
passed the declared 27-case behavior/accessibility inventory on each pinned browser engine and the
13-case host acceptance on each CPython 3.11–3.14 row. Follow-up CI also passed the minimum/latest
testing-extra suites. The accepted freeze assigns API and package ownership, records the Linux
platform/runtime intersections, and keeps macOS and Windows as pilots. No full Cartesian or
managed-adapter support is implied.

| Deliberate case | Required interpretation |
|---|---|
| Request finishes before settle starts | Pre-action checkpoint still observes it |
| No matching request starts / navigation invalidates cursor | Timeout or invalid-cursor diagnostic; never early success |
| 204, replace-policy abort, removed target, stale generation | Follow existing terminal/swap contract without hanging or allowing stale mutation |
| Long polling/stream or unrelated target remains open | Does not block this scoped wait |
| First-party readiness fact is not exposed | Capability unavailable plus explicit semantic predicate; no invented settled fact |
| Expected 422 plus unrelated pageerror | Response expectation does not suppress pageerror |
| Server raises, fixture setup fails, capture fails, teardown fails | Preserve primary exception and append bounded secondary failures |
| Child refuses graceful stop | Terminate/kill/join under deadline, fail cleanup; never report successful lifespan shutdown |
| External loopback test | Server exception/lifespan details unavailable; no caller server shutdown |
| Restricted profile and upstream raw-capture flags | Configuration rejection before context creation |
| Secret canary in form/header/query/exception/console | Structured-only output omits values; scan all written and private temporary artifacts |
| Synthetic trace failure / successful run | Explicit unredacted label and required failed capture / cleanup of success temporaries |
| Required engine missing/skipped | Failed release evidence, never Verified |
| xdist, rerun, nested/OOB replacement | Independent hosts/contexts/paths; failed attempts retained; exactly-once cleanup |

## Artifact and limit acceptance

Structured metadata is the default and contains no raw body, arbitrary message, credential,
cookie/header/storage value, URL/form value, screenshot, DOM, HAR, video, or native trace.
A confidential canary corpus proves that boundary. Rich captures run in a separate explicitly
synthetic corpus and are labeled unredacted. Trace retention on failure requires recording during
the run; screenshots and raw trace cannot be reconstructed or generically sanitized afterward.

A missing required member, denied write, queue overflow, or private-disk threshold breach is an
artifact failure with explicit markers, not successful truncation. Freeze structured hard limits
and native monitoring/overshoot/termination behavior separately; final archive size alone is not
proof of an in-recording cap. Inability to prove native capture limits blocks that capture profile
or requires an explicit accepted scope amendment, not a hidden relaxation.

## Candidate maturity and release checkpoints

All new scenario/host/fixture and schema/contribution surfaces are additive Beta candidates.
Existing Stable test helpers retain their compatibility. Promotion needs narrower demonstrated
support, rather than the presence of an import or generated example.

| Checkpoint | Exit evidence |
|---|---|
| `1.3a0` | Accepted empirical freeze; selected API and typing; observed prototypes, user exercise, matrix and numeric budgets |
| `1.3a1` | Managed-host/profile/intentional-failure Chromium slice, checkpoint core and bounded structured evidence; no satellite prerequisite |
| `1.3b1` | Capture/pytest hardening, bounded three-browser behavior/security/a11y/compatibility corpus, minimal contribution and full disposition inventory |
| `1.3rc1` | Clean package/scaffold/docs/upgrade/opt-out evidence, predecessor release, and every non-release gate Verified |

## Stop and rollback

Stop on an unresolved ownership or observed-work boundary, unmeasured Required budget, secret
capture, leaked process/context/listener, hidden incomplete fact, swallowed primary failure,
unexpected skip, optional import leak, or need for production instrumentation. Fix or amend scope
before implementation/promotion; do not mark a synthetic smoke as browser evidence.

Removing explicit plugin activation/scenario use leaves render/AppScenario/raw Playwright paths
available. Rehearse upgrade and opt-out on clean packages; never remove application data or disable
clean checks to make a rollback pass. Record artifact retention and deletion limits honestly.

## Downstream handoff

Supply 1.4–1.7 only the versioned checkpoint/event/error facts, explicit capability availability,
context isolation, and controlled test-factory seams. Future polling/loading/timing/save behavior
and real visibility/suspension evidence stay with their owning phases. This preserves 1.3's
tooling-only scope and the [new sequence](../rfcs/RFC-0100-INTERACTION-EFFICIENCY-AND-FORM-CONTINUITY.md).
