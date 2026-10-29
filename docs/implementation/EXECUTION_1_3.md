# Hedron 1.3.0 release readiness execution plan

**State:** Candidate implementation is verified by hosted CI; maintainer review, final artifacts, and release approval remain open<br>
**Prepared:** 2026-10-28<br>
**Target:** Repository ready for an authorized 1.3.0 release cut<br>
**Authority:** [RFC-0097](../rfcs/RFC-0097-FIRST-CLASS-UI-TESTING.md),
[implementation contract](UI_TESTING_1_3.md),
[acceptance](../acceptance/RELEASE_1_3.md), and
[17 required gates](../acceptance/release-gate-1.3.toml)

## Execution update — 2026-10-28 (historical baseline)

The repository work now includes the 1.3 gate dispatcher and version-aware evidence tooling,
trusted-user-action and generation-aware settle selection, explicit root pytest activation,
candidate example catalog entries, and an opt-in minimal FastAPI scaffold that generates a
real-browser test. The sample-kit contribution now declares core-only JSON-shaped metadata while
its Hedron-backed demo factory lives with the repository example, preserving satellite import
isolation. The scaffold is unchanged unless requested. PyPI 1.2.0 publication is verified and
bound in both the 1.3 predecessor record and planning contract. The 1.3 implementation baseline,
the 1.2 Python-baseline status, and the 1.4–1.7 planning baselines now reflect the published
1.2.0 train. Coordinated candidate package metadata and candidate CI selection target 1.3.0;
sample-kit 0.2.6 remains an independent candidate. The 1.2 release-validation path is retained
for its immutable source revision. Release-gate regression checks now distinguish the verified
predecessor from still-open 1.3 gates and validate the manual-only historical 1.2 rehearsal.

Local verification on the dirty CPython 3.12.13 worktree:

- Full repository suite: 4,467 passed, 530 skipped, 75 warnings.
- Full local browser-lane snapshots completed on macOS: Chromium 152 passed/85 skipped, Firefox
  150 passed/87 skipped, and WebKit 151 passed/87 skipped. Chromium and Firefox began before the
  persistent generated-scaffold browser regression was added; WebKit included it. These runs do
  not represent one frozen source revision, were not run on the required Linux runner, and the
  skipped tests have not all been classified for release acceptance.
- The 1.3 profile example passed all six tests on Chromium, Firefox, and WebKit. The generated
  scaffold browser smoke passed on each engine against the working-tree package.
- The `quality --skip-wheels` aggregate passed, including strict documentation, repository-wide
  Ruff check/format, BasedPyright (zero errors/warnings), package typing inventory, Python
  baseline, satellite import boundary, and release contract. The configured wheel smoke was
  skipped because it deletes existing files under `dist/`, which already contains the repository's
  1.2.0 artifacts. A safe all-workspace CPython 3.12 wheel build to `/private/tmp`, followed by a
  fresh-environment install/import smoke of the built workspace wheels, passed. The Workbench
  artifact/install check and base-Hedron/sample-kit import-isolation checks also passed. This is
  local macOS evidence only; the clean offline and Python/OS/dependency matrix remains release
  work. No files in the existing `dist/` were changed.
- The sample-kit contribution regression passed on Chromium, Firefox, and WebKit. The full repo
  suite and the aggregate quality run completed after the dependency-boundary fix.
- The strict 1.2.0 release gate passed on the published source revision. The 1.3.0 candidate gate
  now accepts the coordinated 1.3.0 metadata and recorded predecessor, while correctly rejecting
  the incomplete Required gates, freeze, review, artifact, and approval evidence.
- After reconciling the published predecessor in the planning contract and release tests, the
  focused release-gate/artifact-binding/reproducibility suite passed (38 tests), Ruff and format
  checks passed for the updated release tests, and the candidate gate, documentation train check,
  release contract, Python baseline, and `git diff --check` passed. Existing `dist/` artifacts
  remain unchanged.

These local results are not release evidence: the source tree is dirty, has no immutable tested
revision or bound distributable manifest, and ran outside the required Linux environment. All 17
gate rows remain Planned. The v1.2.0 predecessor is verified; freeze, maintainer review, and
release approval are not claimed.

Remaining release blockers as of 2026-10-28 were:

1. Required Linux/Python 3.11–3.14 package and host matrices, pinned browser provenance, and
   downstream clean-install/upgrade/rollback rehearsals are incomplete. Broad Firefox and WebKit
   suites have run on macOS, but the three engine results do not all bind to one frozen candidate
   revision and do not satisfy the required Linux/Python matrix.
2. The native synthetic-capture path has no Hedron-owned mechanism yet for the required
   recording-time disk monitor, measured overshoot bound, and deterministic threshold
   termination. The installed pytest-playwright recorder buffers trace data until context close;
   Hedron currently relies on that upstream recorder and does not own its storage lifecycle. The
   ownership/monitoring design and full confidential-canary and storage-failure corpus remain open.
3. Required behavior and accessibility inventory adoption is incomplete. The browser-lane skips
   (85 Chromium, 87 Firefox, 87 WebKit) need explicit classification before any required browser
   row can be accepted.
4. Required resource budgets remain Unmeasured; dependency/browser/platform limits and package
   dispositions are not frozen; named maintainer owners and reviews are absent.
5. Reproducible candidate artifacts bound to a clean source revision, compatibility evidence,
   all gate reviews, and explicit release approval remain outstanding. The 1.3 artifact rehearsal
   workflow is now defined but has not produced a retained candidate manifest.

The separately versioned `hedron-native==0.1.4` package lookup on PyPI remains unconfirmed. The
1.2 predecessor record covers the 22 coordinated Python distributions; native artifacts remain
tracked separately and are not represented as a PyPI upload.

## Execution update — 2026-10-29

Hosted candidate CI run [40918890605](https://github.com/eddiethedean/hedron/actions/runs/40918890605)
passed on source revision `825f31c8af6e1c446995dbff8be30738b634b22c`. It completed on Linux
`x86_64` with all Python 3.11–3.14 host rows, all three pinned browser lanes on Python 3.12,
quality/docs/typing/package jobs, both existing minimum/latest dependency-bound jobs, integration
smokes, the supply-chain bundle, and the required aggregate check. The retained results are
summarized in the [Linux resource and matrix evidence](../acceptance/evidence-130/ui-testing-resource-budgets-2026-10-29.json);
GitHub retains the per-job artifacts for 90 days.

The Linux host acceptance passed all 13 required cases on each of Python 3.11.15, 3.12.13, 3.13.14,
and 3.14.6. The Chromium, Firefox, and WebKit lanes each passed all 27 required inventory cases.
Skip totals were 79, 81, and 81; each skip matched the explicit policy. The five accessibility cases
and 15 behavior cases passed on all three engines.

The three Linux budget reports passed. The synthetic capture probe used a private 128 MiB tmpfs,
25 ms monitoring, a 64 MiB file limit, a valid retained failure trace, a confirmed ENOSPC hard-limit
probe, and a visible over-limit file error. Its largest 25 ms growth sample was 44,515,636 bytes;
the historical maximum used for the frozen 64 MiB overshoot bound is 45,564,212 bytes. The separate
structured privacy probe passed on each engine for form, query, header, cookie, storage, console,
exception, target, and path values. It retained one structured manifest per engine, found no canary
values in those manifests, wrote no native browser output, and the downloaded 49-file CI artifact
set contained zero canary-token matches.

The candidate CI workflow now also installs `hedron[testing]` in its minimum/latest dependency
environments and runs the host, artifact, policy, and contribution suites with explicit plugin
activation. That closes the earlier gap where the minimum/latest jobs covered stable adapters but
not the optional UI-testing stack; its result must be green on the source revision containing the
workflow change before upstream-bounds evidence is closed.

The release remains in progress. The contract freeze flag is still false, no named maintainer
assignments or package-disposition review are recorded, and the phase gate file keeps all 17 rows
Planned. Reproducible distributables, the Python 3.10 fallback check, and the Python 3.11 scaffold
upgrade/rollback rehearsal are bundled in the 1.3 release-artifact workflow, which is not yet on the
default branch and has not produced an artifact manifest. PR #984 is still draft with no reviewer
or assignee. The maintainer review and release approval records are empty. No tag or publication
has been created.

## Initial planning snapshot

The following subsection records the state when this execution plan was first drafted. The
execution update above supersedes its implementation and verification status; predecessor,
freeze, ownership, and release blockers below remain open.

The UI testing candidate implements the direct Playwright API, managed ASGI host,
explicit pytest plugin, structured manifests, synthetic capture option guards, and
sample-kit contribution. A historical macOS/Python 3.12 slice passed on all three
engines. Subsequent review fixes have received static checks and partial focused
probes, not a complete rerun against a frozen candidate. That historical slice is
not evidence for the final source revision.

All 17 `*-130` gates are still `Planned`. The 1.3 contract has unfrozen dependency,
browser, resource, and platform limits. Current package metadata and CI select
1.2.0, and `scripts/check_release_gate.py` has no 1.3 dispatcher entry. The 1.2
gate is Verified in-tree, while `docs/release.toml` still records 1.1.3 as the
published version and 1.2.0 as development. Reconcile those facts using retained
release evidence before satisfying 1.3's predecessor condition.

At initial planning time, the latest focused run had 30 passes and one managed-host failure
caused by this sandbox denying a loopback bind. Later local runs completed with loopback access,
but release host/browser evidence still belongs on the required Linux runners. An environment
failure is an unverified row, not a pass or a product regression by itself.

## Release scope

Keep the accepted first cut: sync pytest, native Page/Locator/expect, managed
flagship ASGI and caller-owned literal-loopback URLs, isolated contexts,
checkpoint observation, narrow HTTP expectations, structured diagnostics,
explicit synthetic capture, one specialist contribution, and the declared
behavior/accessibility corpus. New surfaces ship as Beta; existing Stable
helpers retain their compatibility.

Keep 1.4–1.7 runtime features with their owning phases. Native capture is currently
required by the 1.3 acceptance contract: implement its resource/failure guarantees.
If it cannot meet them, stop and obtain an explicit accepted scope amendment;
do not silently drop it or mark the gate Verified.

## Ordered work packages

### E0 — Reconcile the predecessor and make 1.3 gates executable

**Status:** Completed for local predecessor, candidate metadata, gate selection, and rehearsal
workflow setup. Artifact rehearsal output and strict release evidence remain future work.

**Suggested owner roles:** release, tooling, architecture. Assign actual named
maintainers before closing this work package.

1. Review `evidence-120`, immutable artifact/tag/publication records, and current
   release facts. The coordinated 1.2.0 PyPI files are verified in
   `evidence-120/PUBLICATION.md`, and the 1.3 predecessor record is hash-bound.
2. Add explicit 1.3 support to `scripts/check_release_gate.py`: expected 17 ids,
   required rows, predecessor, contract freeze, approval, evidence binding, and
   release-cut conditions. Verify missing, stale, incomplete, or unrelated
   evidence fails. In-progress checks may allow Planned; the release path may not.
3. Audit release tooling for 1.2 assumptions, including
   `scripts/build_reproducible_release_artifacts.py`, its verifiers and upgrade
   rehearsals, `scripts/ci_checks.sh`, CI, and the release workflow. Preserve the
   historical 1.2 verification path while adding a 1.3 path. A separate 1.3
   reproducible-artifact workflow now runs the version-aware candidate tooling.
4. Produce a changed-distribution inventory. Update coordinated candidate
   versions, `__version__`, internal requirements, lockfile, changelogs, and
   development metadata together for 1.3.0. Independently versioned satellites
   follow their own version policy; changed contents cannot reuse a published
   version. Public published facts remain tied to actual uploads.
5. Select 1.3 in candidate CI after its validator and metadata agree.

**Exit:** The 1.3 candidate checker accepts current metadata and Planned rows;
strict mode rejects the incomplete release. Predecessor status is documented
accurately. The artifact rehearsal workflow is ready to bind a clean revision.
No unsupported version falls back to a historical gate.

### E1 — Freeze observable behavior and protect the review fixes

**Suggested owner roles:** testing, browser-platform, tooling.

Write durable regression coverage around the real failure boundaries from review:

- HTTP redirect denial; response-body disposal on fulfill, abort, and exceptions;
  HTTP and WebSocket guards installed before pages and retained through capture;
  explicit SSE/streaming/WebSocket capability limits.
- Canonical IPv4/IPv6 origins and default ports; fixture and marker option
  precedence; explicit Service Worker blocking; HAR/video and CLI capture
  rejection before context creation, including dynamic fixture requests.
- Sibling/old-document checkpoints; fast completion, delayed 422 swap and settle,
  no-swap HTTP error, send error, timeout, abort, and 204. Cover a later same-target
  poll, a poll racing before the action, overlapping actions, supersession, and
  generation changes. Define correlation precisely; selecting the first or last
  start alone does not establish action identity in every race.
- Dynamic contribution loading plus valid, missing, duplicate, conflicting,
  incompatible, and nested import-reference cases; fixture resource validation.
- Final shutdown-confirmation races, failed lifespan, forced termination,
  capture failure with native context closure, and manifest-write failure during
  setup, call, and teardown while preserving the original failure.

Use unit/subprocess tests for validation and failure reporting, and real browsers
for DOM/lifecycle/network claims. Replace stand-in-only proofs with real boundary
tests where browser or ASGI ordering determines correctness. Fix failures before
expanding adoption. Freeze signatures, event/schema versions, supported behavior,
explicit unavailable cases, and ownership after these probes pass.

**Exit:** Repeatable regression suite passes; no unresolved correctness or
ownership issue remains. Gate candidates: `CONTRACT`, `LOCATOR`, `SETTLE`, `ERROR`,
and `PYTEST` (all ids carry the `-130` suffix).

### E2 — Prove host, context, and pytest lifecycle behavior

**Suggested owner roles:** testing, tooling.

- Exercise retained port-zero listeners, actual lifespan readiness, root paths,
  static assets, synthetic auth/DB overrides, startup errors, startup deadlines,
  shutdown failure/hang, interruption, and bounded terminate/kill/join.
- Verify external URLs never stop the caller's server and report unavailable
  server facts honestly. Check for leaked processes, listeners, file descriptors,
  pages, and contexts after both passing and failing cases.
- Run setup/call/teardown failures, forgotten sessions, multiple scenarios,
  xdist workers, and rerun attempts. Preserve isolated artifacts and failed
  attempts; retain upstream driver/browser ownership.
- Exercise engine, headed/device, locale, viewport, JavaScript, fixture overrides,
  and markers through the actual pinned pytest-playwright integration. Collection
  must work without browser binaries; a selected required engine missing at run
  time must fail with an actionable diagnostic.

**Exit:** Lifecycle matrix and leak checks pass on the declared Linux runtime.
Gate candidates: `HOST`, `PYTEST`, and `ERROR`.

### E3 — Complete artifact, privacy, and capture guarantees

**Suggested owner roles:** testing, security, performance.

- Run a confidential canary corpus through form/query/header/cookie/storage,
  exception, console, target ids, and paths; scan every structured output and
  temporary artifact for those values.
- Cover exact/over-limit event and manifest sizes, omission/truncation/failure
  markers, permissions, symlinks, denied writes, partial writes, path isolation,
  and atomic replacement. Overflow must not silently lose a failure.
- Verify synthetic consent, unredacted labels, trace/screenshot ownership,
  required-member presence, capture errors, and successful-run temporary cleanup.
  Upstream best-effort screenshot behavior alone cannot prove required capture.
- Implement recording-time disk monitoring, a measured sampling interval and
  overshoot bound, and deterministic capture termination. Measure disk usage
  while recording rather than relying on final archive size.
- Validate app auth/CSRF remains effective and state clearly that browser-origin
  controls do not restrict server egress.

**Exit:** Canary and injected capture/storage failures pass with explicit results.
Gate candidates: `ARTIFACT` and `SECURITY`; resource evidence feeds E6.

### E4 — Run the declared behavior and accessibility corpus

**Suggested owner roles:** reference-app, accessibility, browser-platform.

Create a bounded inventory mapping each required behavior to an existing or new
test. Adopt the shared harness for those tests where it supplies real evidence:
PAGE/fragment/OOB/history, secured forms and validation, local/request/combined
state, elements, uploads/downloads, polling/action concurrency, JavaScript-off
fallback, and missing assets. Do not treat mocked responses as host evidence.

Run the inventory on Chromium, Firefox, and WebKit on Linux/Python 3.12. Include
semantic and keyboard interaction, focus and announcements, supported presentation
modes/viewports, zoom/reflow, and no-JS behavior. Record axe version, scope,
incomplete/error outcomes, and an intentional violation to prove detection.

**Exit:** Every declared required case passes on each required engine. A skipped
required case fails the gate; unrelated optional legacy skips remain explicitly
classified. Gate candidates: `BEHAVIOR`, `A11Y`, `LOCATOR`, `SETTLE`, and `ERROR`.

### E5 — Verify compatibility, distributions, and downstream use

**Suggested owner roles:** compatibility, packaging, packages, docs.

- Run core/host/import/package checks on CPython 3.11–3.14. Test actual minimum
  and maximum supported upstream dependency combinations, then narrow declared
  ranges if evidence requires it. Pin browser revisions for release evidence.
- Build wheels and sdists and install them in clean environments without source
  checkout imports or editable-install help. Check base/core without optional UI
  dependencies, `hedron[browser]`, and `hedron[testing]`, including offline install
  from a prepared wheelhouse and actionable missing-extra/browser diagnostics.
- Preserve Stable testing exports, typing, aliases, and existing behavior. Ensure
  installing packages causes no pytest plugin autoregistration or optional import
  leak. Verify packaged example/resources, dependency metadata, and notices.
- Review all 23 package dispositions with actual maintainers. Exercise the
  sample-kit contribution in installed packages and cover absence, disabled,
  version/conflict, and fleet import cases.
- Deliver the packaged/scaffold test example required by acceptance; the current
  repository example alone does not prove generated-project adoption. Rehearse
  installation, first test, intentional failure, debugging, upgrade, and opt-out.
  Complete docs and changelogs, then run strict documentation checks.

**Exit:** Clean installed-package matrix and downstream rehearsals pass.
Gate candidates: `COMPAT`, `PKG`, `SATELLITE`, and `DOCS`.

### E6 — Freeze measured budgets and bind evidence to the candidate

**Suggested owner roles:** performance, architecture, release.

Measure cold/warm host startup and shutdown, context creation/closure, settle
overhead and deadlines, event storage, structured artifact bytes, synthetic
recording disk/overshoot, worker count, memory/process counts, and total CI time.
Record hardware, runtime, sample count, observations, chosen numerical limits,
and rationale. Exercise exact-limit and over-limit behavior. Account for slower
required runners; do not invent thresholds from the single historical smoke run.

Freeze the matrix, limits, schemas, package dispositions, and named owners in
`ui-testing-contract-130.toml`. Each gate record must name its command, runner/job,
source revision, dependency/browser provenance, result counts, and retained
evidence path/checksum. Validate source/artifact binding automatically.

**Exit:** No required budget is Unmeasured, no authority question is unresolved,
and evidence describes the actual candidate. Gate candidates: `FREEZE` and `PERF`.

### E7 — Build and rehearse the release candidate

**Suggested owner roles:** release, packaging, maintainers.

1. Commit the complete candidate and run the full inherited repository CI plus
   the new 1.3 matrix on that source revision. Classify and resolve failures;
   local sandbox restrictions require a capable runner, not a waiver.
2. Build reproducible release artifacts using the version-aware tooling from E0.
   Verify inventory, hashes, metadata, import/typing/scaffold smoke, native artifact
   compatibility, upgrade from the verified predecessor, and opt-out/rollback.
3. Finalize the evidence manifest and retain the exact distributables and logs.
   Mark the 16 non-release gates Verified only after their requirements pass and
   named maintainers review them. Evidence must bind to the tested source and
   artifact hashes; do not reuse the dirty-worktree vertical-slice attestation.
4. Complete `RELEASE-130` with explicit release approval, the predecessor record,
   final gate validation, release notes, support/maturity/known limits, publish
   order, and rollback instructions. A new source change after verification needs
   appropriate reruns and a refreshed artifact/evidence binding.

**Exit:** All 17 gates Verified, strict release checks pass, the exact candidate
artifacts are retained and approved, and required CI has no unresolved failure or
skip. Publication then follows [the release runbook](../RELEASE.md), including
merge CI and Read the Docs checks before an authorized unique release tag/upload.

## Scheduling and command handoff

Critical path: E0 → E1 → E2/E3 → E4/E5 → E6 → E7. Measurement collection starts
during E2–E5; final threshold and evidence freeze happens in E6. Artifact/privacy
and packaging work can proceed alongside behavior adoption after ownership and
API behavior are settled. Assign named owners and size the work after E0/E1;
the current evidence does not support a reliable calendar estimate.

Useful existing suite entry points are below. These are the execution handoff,
not commands run while preparing this plan:

```bash
uv sync --locked --all-groups --python 3.12
uv run pytest -q tests/unit/test_ui_testing_policy.py tests/unit/test_ui_testing_host.py \
  tests/unit/test_ui_testing_artifacts.py tests/unit/test_ui_testing_contributions.py -n 0
HEDRON_BROWSER=1 HEDRON_BROWSER_ENGINE=chromium bash scripts/ci_checks.sh browser --python 3.12
HEDRON_BROWSER=1 HEDRON_BROWSER_ENGINE=firefox bash scripts/ci_checks.sh browser --python 3.12
HEDRON_BROWSER=1 HEDRON_BROWSER_ENGINE=webkit bash scripts/ci_checks.sh browser --python 3.12
```

After E0 adds 1.3 support and aligns candidate metadata, the final repository
handoff uses `scripts/ci_checks.sh all --all-pythons --all-browsers --release-gate
--gate-version 1.3.0` and `scripts/check_release_gate.py 1.3.0` through the locked
environment. Do not use `--allow-planned`, skip flags, or unretained evidence for
the release decision. Existing required licensed/native/backend checks retain
their requirements and must run on appropriately provisioned infrastructure.
