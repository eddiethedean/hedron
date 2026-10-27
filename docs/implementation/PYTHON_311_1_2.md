# Phase 1.2: Python 3.11+ support and typing baseline

**Status:** Implementation in the v1.2.0 candidate workspace; release evidence pending
**Baseline:** Published `v1.1.3`
**Authority:** [RFC-0099](../rfcs/RFC-0099-PYTHON-311-BASELINE.md)
**Acceptance:** [RELEASE_1_2](../acceptance/RELEASE_1_2.md) ·
[release-gate-1.2.toml](../acceptance/release-gate-1.2.toml)

Decision D-120 accepts retiring Python 3.10 for the candidate because it no longer receives
CPython security fixes. The repository implementation now raises the maintained package and
generated-project floor to 3.11, moves static/runtime CI targets and native selectors to 3.11–3.14,
uses the equivalent standard-library typing and TOML/enum APIs, removes obsolete TOML backports,
and explicitly selects the 1.2 release packet. This does not extend support for published 1.1.3.

## Repository seams

This is the inspected starting inventory, not a substitute for the W0 freeze.

| Area | Sources to reconcile | Required result |
|---|---|---|
| Python package inventory | Root `pyproject.toml`, every workspace member's metadata, `release/publish-order.toml` | Every maintained distribution has an owner, release line, dependency order, Python requirement, and artifact disposition |
| Static checks | Root `pyproject.toml`, `scripts/check_package_typing_inventory.py`, `scripts/check_typing_044.py`, `typings/` | BasedPyright targets 3.11 in `all` mode; Ruff targets `py311`; existing strictness and package coverage preserved |
| Compatibility | `packages/hedron-core/src/hedron_core/compat.py`, `typing_aliases.py`, `component.py`; `packages/hedron-data/src/hedron_data/workspace.py` | Standard-library enum/TOML implementations and equivalent 3.11 typing imports; public imports preserved |
| Dependency cleanup | Root dev group, core/docs package metadata, fallback consumers in packages/scripts/tests, `uv.lock` | Remove obsolete direct TOML/backport requirements only after consumer audit |
| Runtime/release CI | `.github/workflows/ci.yml`, `release.yml`, `edron-release.yml`, `scripts/ci_checks.sh` | Declared runtime lanes cover 3.11–3.14; minimum-runtime checks execute under 3.11 |
| Native | `.github/workflows/native-wheels.yml`, `packages/hedron-native/pyproject.toml`, native sources | Both wheel selectors omit cp310; each advertised remaining platform/runtime combination passes conformance |
| Release enforcement | `release/support-matrix.toml`, `scripts/check_release_gate.py`, `scripts/check_release_contract.py`, `scripts/check_changed_package_versions.py`, `scripts/check_stable_dependency_bounds.py` | Live manifests and release checks agree with actual artifact metadata and support policy |
| Consumer and authoring guidance | Scaffolds in package source, examples, README, compatibility/install/contributor/security/release guides | Generated and documented applications install on 3.11; accurate upgrade and rollback steps |
| Historical material | Frozen acceptance packets, stable inventory/signatures, archived examples | Preserve historical facts and review any intentionally retained compatibility reference |

## W0 — Freeze scope and policy

Reconcile the machine packet's 23 starting package names against current workspace membership,
release order, build tooling, and package discovery. Record every additional or retired tree.
Inventory active 3.10 branches, `tomli` consumers/stubs, typing backports, Python requirements,
classifiers, matrices, wheel selectors, and generated project templates. Classify each reference
as active migration, retained newer backport, public compatibility alias, or historical evidence.
Record supported host/dependency/platform combinations and responsible maintainers.

Accept RFC-0099 and the support-policy amendment, including migration notice and the treatment of
existing deprecation/support windows. Freeze `>=3.11,<3.15`, default CPython 3.11–3.14, retained
backport reasons, reference-flow assertions, and exact evidence commands. Record baseline strict
check diagnostics and runtime/schema outputs. No required package may be excluded implicitly.

**Current state:** `POLICY-120` is accepted by D-120. The candidate's 23-package starting inventory
and declared interpreter matrix are recorded. The complete source/host/platform inventory and
retained evidence corpus still need release review; see `FREEZE-120`.

## W1 — Package requirements and check targets

**Implemented in tree:** Root and all workspace package metadata/classifiers, examples and
scaffolds, support manifests, lock resolution, BasedPyright 3.11, Ruff `py311`, 3.11–3.14 CI/local
matrices, and native wheel selectors now use the candidate floor. Strict typing coverage and the
no-Any policy remain enabled. Developer/docs interpreter defaults such as `.python-version = 3.12`
remain valid.

Release tooling selects phase 1.2 explicitly and rejects unknown 1.x packets instead of falling
through to historical release evidence. Metadata, artifact tags, minimum-runtime execution, and
the full CI matrix still require recorded release evidence; source edits alone do not verify those
gates.

**Evidence pending:** `METADATA-120` and `CHECKS-120` need clean 3.11 execution and built-artifact
metadata inspection. Other supported runtimes remain part of the release matrix.

## W2 — Standard-library typing and compatibility cleanup

**Implemented in tree:** Equivalent `Self` and `NotRequired` imports use `typing`; newer
`typing_extensions.override` and `TypeIs` imports retain direct package dependencies. No 3.12+
syntax is introduced. A future-annotations import does not make unavailable runtime names or newer
grammar valid on the minimum interpreter.

The enum/TOML implementations now use the standard library while preserving public compatibility
aliases. Fallback imports, direct `tomli` requirements, and obsolete stubs were removed after the
consumer audit. Runtime comparisons of resolved annotations, generated schemas, enum/string/JSON
behavior, TOML diagnostics, inherited return typing, and optional/required fields remain evidence
items for `TYPING-120`, `STDLIB-120`, and `COMPAT-120`.

Use focused existing regression cases; add a case only where cleanup introduces a distinct risk.
Avoid broad annotation rewrites or introducing newer async semantics solely because 3.11 has them.

**Evidence pending:** `TYPING-120`, `STDLIB-120`, and `COMPAT-120` require supported-runtime
verification without suppressions or public API loss.

## W3 — Installed application, hosts, dependencies, and native artifacts

Upgrade one 1.1.3 application through interpreter selection, fresh environment creation, lock
resolution, and installed-package execution. Exercise page/view/action binding, validation errors,
configuration parsing, and the ordinary HTTP/HTMX path. Record relevant schema/type parity and
security behavior. Cover the existing FastAPI, Flask, Django, HDJ, and supported satellite slices
through their owning suites. Optional dependencies must remain optional on base/core installs.

Run the declared 3.11–3.14 runtime matrix, dependency-bound combinations, clean wheel/sdist installs,
and native platform/interpreter conformance. Prove pure-Python fallback parity. Required missing
runtimes, native artifacts, or host services leave rows incomplete; a skip is not release evidence.

**Exit:** `RUNTIME-120`, `NATIVE-120`, and `PKG-120` Verified with source/artifact provenance.

## W4 — Migration docs and release decision

Explain explicit 3.10 candidate-install rejection and unpinned resolver fallback; demonstrate
rollback using the previous environment and lock. Update live support guidance at the implementation
cut while preserving immutable prior release evidence. Publish package-specific versions in the
existing order; coordinate independently versioned satellites and their dependency bounds.

Document each evidence result with commit, command, interpreter/dependency versions, platform,
artifact digest, and retained log location. Attach the support-policy decision and candidate
migration/rollback guidance. Recheck that metadata, support claims, wheel tags, strict targets,
and the release packet agree. Only then may the release decision promote the packet.

**Exit:** `DOCS-120` and `RELEASE-120` Verified; no remaining Required Planned row.

## Candidate checkpoints and handoff

| Checkpoint | Reviewable result |
|---|---|
| `1.2a0` | Accepted policy/scope, package and active-reference inventory, frozen matrix and parity corpus |
| `1.2a1` | Coherent metadata/check targets, standard-library cleanup, installed reference flow on 3.11 |
| `1.2rc1` | Full runtime/dependency/native artifact evidence, documentation and rollback rehearsal |
| Release decision | All Required rows Verified and publication approved against exact artifacts |

Checkpoint names are candidates, not existing tags. `scripts/check_python_311.py` enforces the
static support baseline, and `scripts/verify_pkg_120.py` binds it to package versions and the phase
packet. These are implementation checks, not runtime or release evidence. Hand phase 1.3 the 3.11
floor, retained-backport decisions, package inventory, and installed reference corpus; that phase
keeps ownership of the managed UI-testing harness.
