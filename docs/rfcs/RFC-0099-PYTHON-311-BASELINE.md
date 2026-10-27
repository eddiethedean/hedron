# RFC-0099: Python 3.11+ support and typing baseline

**Status:** Accepted (D-120); implementation in-tree, release evidence pending
**Target:** Hedron `1.2` planning candidate
**Baseline:** Published `v1.1.3`; current package metadata is authoritative
**Implementation:** [PYTHON_311_1_2](../implementation/PYTHON_311_1_2.md)
**Acceptance:** [RELEASE_1_2](../acceptance/RELEASE_1_2.md) ·
[release-gate-1.2.toml](../acceptance/release-gate-1.2.toml)

## Outcome and support contract

Phase 1.2 retires Python 3.10 support across the maintained Python workspace and adopts Python
3.11 typing semantics and automated checks. Its candidate runtime matrix is default-build CPython
3.11, 3.12, 3.13, and 3.14, with `requires-python = ">=3.11,<3.15"`. Raising the minimum does not
admit 3.15, PyPy, or free-threaded CPython. Those require separate support evidence.

The inventory starts with all 23 members of `tool.uv.workspace.members`, including Edron,
independently versioned satellites, Python tooling, and the native package's Python wrapper and
wheels. Stage 0 must reconcile membership with the release publish order, source trees, examples,
scaffolds, and supported external application templates. Independently versioned packages need
compatible releases, not forced version-number alignment. Retired packages and non-Python
runtimes receive explicit dispositions; they cannot silently disappear from the inventory.

Python 3.10 has reached end of security support and receives no further CPython security fixes.
Decision D-120 accepts the 1.2 support-policy amendment: candidate packages require CPython 3.11+
and remove 3.10 from runtime and wheel matrices. The published 1.1.3 artifact metadata remains
immutable and its compatibility facts are historical; no 1.1 security-window extension is implied.
The migration path is an interpreter upgrade, fresh environment, regenerated lockfile, and
coordinated package update. Stable application APIs remain protected.

## Typing rules

- Configure BasedPyright `pythonVersion = "3.11"` and Ruff `target-version = "py311"`.
  Keep BasedPyright `all` mode, explicit and inferred `Any` errors, and the existing fatal checks.
  Changing interpreter targets cannot justify exclusions, suppression growth, or weaker diagnostics.
- Use `typing.Self`, `Required`, `NotRequired`, `Never`, `LiteralString`, `TypeVarTuple`, and `Unpack`
  where supported by the existing contract. Prefer standard-library imports for existing equivalent
  annotations; new abstractions need a concrete use. This is not a quota to introduce each feature.
- Retain `typing_extensions` for features newer than 3.11, including `override` and `TypeIs`, and
  for any documented semantic requirement. Remove individual backports only after checking their
  availability and behavior on 3.11. Audit direct dependencies per package rather than relying on
  another distribution's transitive dependency.
- Python 3.12 type-parameter and `type` statement syntax, and later syntax, are outside this floor.
  Preserve 3.11-compatible `TypeVar`, `Generic`, and alias declarations where needed.
- Preserve annotation behavior used by FastAPI, Pydantic, schema generation, dependency injection,
  forms, and HDJ. Compare resolved type hints, optional/required fields, signatures, and generated
  schemas. `Self` may change subclass inference; `Never`, `NoReturn`, `TypeGuard`, and `TypeIs`
  are not interchangeable by spelling. Do not bulk-rewrite them to satisfy a style check.

## Runtime compatibility cleanup

Replace the 3.10 branches in `hedron_core.compat` with standard-library `enum.StrEnum` and
`tomllib`. Preserve inventoried public compatibility import paths with direct re-exports; retiring
an interpreter does not authorize removing a public symbol. Compare enum values, string behavior,
serialization, diagnostics, and TOML parsing on supported runtimes. Audit annotations referencing
backported types for schema and runtime introspection changes.

Remove direct `tomli` dependencies, fallback imports, and stubs only when their remaining consumers
have been migrated. A transitive lockfile occurrence is not itself a failure. Keep compatibility
code that serves a different supported interpreter, dependency, or host version. No asynchronous
runtime redesign, dependency major upgrade, or browser-asset change belongs to this phase.

## Checks and compatibility evidence

The minimum runtime must be exercised directly: installing a package on 3.12 while telling the
checker to target 3.11 is insufficient. Use clean 3.11 environments for package imports, typing,
scaffold execution, optional-extra isolation, and dependency-bound checks. Run the existing runtime
and host coverage across the declared 3.11–3.14 matrix. Record unsupported upstream combinations
explicitly and resolve them before declaring a Required row complete.

Update both native wheel selectors, package metadata/classifiers, root metadata, lockfile, CI test
and release matrices, local check defaults, support/release manifests, and generated project
requirements. Default developer and documentation interpreters may remain 3.12; the explicit 3.11
CI lane is mandatory. The native corpus must cover advertised platforms and the Python fallback.
Rebuild consumers from clean wheels in publish order; already published artifacts remain immutable.

Historical release notes, frozen baselines, archived fixtures, and signed evidence retain their
3.10 facts. The migration analyzer may continue accepting Python 3.10 source grammar to inspect old
application code; this source-analysis capability does not promise runtime support. Active fixtures
may otherwise retain a 3.10 reference solely to prove rejection or reproduce an explicit historical
baseline; a global text replacement is not an acceptable migration.

## Migration and rollout

The reference flow upgrades a small 1.1.3 application to Python 3.11, recreates its environment,
resolves a lockfile, and exercises a typed view/action plus validation and TOML configuration from
installed artifacts. Preserve authorization, CSRF, escaping, and error behavior. Use existing test
facilities; phase 1.3 owns the managed browser harness.

An explicit install of the candidate on 3.10 must be rejected by `Requires-Python`. An unpinned
install may legitimately select an older compatible release. Migration guidance explains this
resolver behavior, interpreter selection, environment recreation, lock regeneration, and coordinated
satellite selection. Rollback uses a retained 1.1 environment and its exact lockfile; do not promise
an extended 1.1 security window without a separate support decision.

## Completion

All Required `*-120` rows must be Verified with immutable evidence tied to the candidate source
and artifacts before publication. The support-policy decision, metadata, lint/type targets, actual
interpreter matrix, package releases, documentation, and rollback story must agree. This RFC records
the accepted support-policy amendment; the repository implementation is in-tree, while release
evidence and publication remain separate gates. Published 1.1 facts and the phase 1.3 scope remain
unchanged.
