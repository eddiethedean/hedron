# Hedron `v1.2.0` Python 3.11+ acceptance plan

**Status:** Published on PyPI on 2026-10-27; coordinated Python artifacts verified
**Baseline:** Published `v1.1.3`
**Target:** Published `v1.2.0`; independently versioned packages retain their own release lines
**Authority:** [RFC-0099](../rfcs/RFC-0099-PYTHON-311-BASELINE.md)
**Implementation:** [PYTHON_311_1_2](../implementation/PYTHON_311_1_2.md)
**Machine packet:** [release-gate-1.2.toml](release-gate-1.2.toml)

Decision D-120 accepts retiring Python 3.10 because it no longer receives CPython security fixes.
The candidate implementation updates maintained package metadata, typing/runtime checks, stdlib
compatibility paths, release selection, and migration guidance. The required runtime, native, and
artifact evidence is recorded against the frozen candidate, and the machine gate records maintainer
acceptance and release approval. Publication is recorded in
[evidence-120/PUBLICATION.md](evidence-120/PUBLICATION.md). It does not extend the 1.1 support
window. The separate `hedron-native` 0.1.4 PyPI upload remains unconfirmed; its platform artifacts
are tracked independently.

## In-tree implementation

- All 23 workspace distributions and generated project templates declare `>=3.11,<3.15`;
  package versions/changelogs identify the 1.2.0 candidate train while published 1.1.3 facts stay
  immutable.
- Ruff targets `py311`; BasedPyright targets Python 3.11 in `all` mode. CI and local matrices cover
  CPython 3.11–3.14, and both native wheel selectors omit `cp310`.
- Equivalent `Self` and `NotRequired` types use `typing`; stdlib `StrEnum` and `tomllib` replace
  compatibility branches while public aliases remain available. Obsolete direct `tomli`
  requirements and stubs are removed; newer `typing_extensions` imports have direct dependencies.
- `scripts/check_python_311.py` checks the maintained support baseline, and
  `scripts/verify_pkg_120.py` binds that check to candidate package versions and this packet.
- Live install/support guidance describes moving to 3.11+, environment recreation, and rollback;
  historical published-release metadata remains unchanged.

Supported-runtime, dependency-bound, required host/satellite contract, native-wheel,
installed-application upgrade, and rollback evidence is retained in `evidence-120/` and bound to the
frozen candidate. The artifact rehearsal binds Python 3.10 rejection and unpinned resolver fallback
to the exact candidate wheel. The separately licensed live Connect smoke is advisory.

The [1.2 artifact rehearsal workflow](../../.github/workflows/release-artifacts-1.2.yml)
builds the 22 coordinated Python distributions twice, compares the complete 44-file inventory and
hashes, checks Python 3.10 rejection/resolution fallback, rehearses an installed 1.1.3 app upgrade
and lock-based rollback on Python 3.11, and retains the results with a source-linked ledger. The
reviewed ledger is committed under `evidence-120/` after the source freeze; the release workflow
verifies it against its own build before publication. Native platform wheels remain a separate
workflow and evidence set.

## Required gates

| Gate | Required evidence |
|---|---|
| `POLICY-120` | Accepted RFC and explicit support-policy amendment authorizing retirement of 3.10 in the candidate 1.2 line; migration notice, support-window treatment, package coordination, and rollback decision recorded |
| `FREEZE-120` | Complete workspace/release/retired-tree inventory; active versus historical reference dispositions; named maintainers; frozen interpreter/host/dependency/native matrix and parity corpus; exact evidence commands |
| `METADATA-120` | Root, all maintained distributions, classifiers, generated project requirements, lockfile, and live support manifests agree on `>=3.11,<3.15`; built metadata agrees; explicit 3.10 install rejected |
| `CHECKS-120` | BasedPyright targets 3.11 in all mode with no weakening of no-Any or other fatal diagnostics; Ruff targets py311; actual 3.11 typing/import lane plus 3.11–3.14 runtime/release/local matrices; release tooling selects the new packet explicitly |
| `TYPING-120` | Equivalent available typing imports use the stdlib; retained newer backports have reasons and direct dependency coverage; subclass inference, resolved hints, TypedDict requirements, schemas, and signatures remain correct; no newer syntax enters the 3.11 floor |
| `STDLIB-120` | Native enum/TOML paths replace obsolete fallbacks; required public aliases remain; direct tomli/stub cleanup follows consumer audit; enum/string/serialization/TOML behavior preserved |
| `COMPAT-120` | Stable public imports and API inventory preserved on remaining runtimes; FastAPI/Pydantic/HDJ forms, DI, schemas, validation and relevant security contracts retain parity; historical baselines remain intact |
| `RUNTIME-120` | Required runtime and nonlicensed host/satellite suites pass on declared 3.11–3.14 combinations; minimum/latest dependency cases reproduce; installed reference application upgrade succeeds on 3.11; no skipped Required row. The live licensed Connect Docker smoke is advisory. |
| `NATIVE-120` | Both active wheel selectors retire cp310; metadata/tags and all 16 advertised platform/runtime wheels agree; native and pure-Python fallback conformance passes on the declared matrix |
| `PKG-120` | Clean wheel/sdist builds and installs for all maintained packages; base/extra import isolation, direct dependencies, coordinated ranges and publish order verified; 3.10 explicit rejection and unpinned older-release resolution documented and exercised |
| `DOCS-120` | Live support, install, contributor, generated-app, migration and release guidance agree with artifacts; environment recreation and lockfile upgrade/rollback demonstrated; historical 3.10 evidence preserved; no unsupported security/LTS promise |
| `RELEASE-120` | Every other Required row Verified; immutable commit/artifact-linked logs and hashes, policy decision, compatibility/support inventory, migration/rollback notes, and explicit release approval present |

## Evidence rules

Each gate records interpreter and dependency versions, OS/architecture, command and result,
source commit, artifact digest where applicable, and a retained evidence location. Schema/type
comparisons distinguish expected interpreter metadata changes from regressions in public behavior.
An unavailable required interpreter, browser/service used by an existing required slice, or native
wheel is incomplete evidence. It cannot become a pass through a skip or narrower undocumented matrix.
Every listed gate is required for this cut: the strict release checker requires all rows to be
`Verified` and `release_cut_satisfied = true`; `Deferred` does not authorize publication.
The licensed Posit Connect Docker smoke is supplemental: its redacted Actions log is informational,
and the release workflow does not wait for or gate on its license, service, or probe outcome.
In-tree Connect adapter and contract tests remain part of the required runtime/compatibility suites.

The packet begins with the current 23 workspace packages. The maintainer reviewed the reconciled
release inventory and its reference dispositions; any future exclusion or changed support claim
requires a new explicit disposition. Default-build CPython 3.11–3.14 is the candidate matrix;
3.15, PyPy, and free-threaded builds are outside the claim. Package maturity remains governed by
the existing stability inventory.

Phase-specific enforcement is in place: `scripts/check_python_311.py` checks the maintained
interpreter, typing, dependency, and native-wheel baseline; `scripts/verify_pkg_120.py` binds that
check to the 1.2.0 package inventory and acceptance packet. The release workflow selects this
packet explicitly. Its strict release check rejects `Planned`, `Implemented`, and `Blocked` rows,
so implementation CI cannot authorize publication while release evidence is incomplete. All
required phase 1.2 rows are now `Verified`; the packet records the maintainer's release approval
and `release_cut_satisfied = true`. Publication remains a separate action.
