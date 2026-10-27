# Phase 1.2 maintainer review and release approval

**Decision date:** 2026-10-27  
**Maintainer and approver:** Odos Matthews (`@eddiethedean`)  
**Decision:** Approved for the v1.2.0 release cut; this approval clears the gate and does not
publish artifacts.

Odos Matthews explicitly approved formal clearance of v1.2.0 in the Codex task. The connected
GitHub identity is `eddiethedean` / Odos Matthews and has `admin` and `maintain` permissions on
`eddiethedean/hedron`.

## Freeze inventory review

The maintainer reviewed and accepted the 23-distribution inventory, release order, support matrix,
exclusions, and active-versus-historical Python 3.10 reference dispositions in [SCOPE.md](SCOPE.md).
No maintained package is excluded from the release order. The required support claim is CPython
3.11–3.14 (`>=3.11,<3.15`); the Connect Docker smoke is advisory while in-tree Connect contracts
remain in the required CI suite.

The exact frozen source commit for this approval is recorded as the shared `source_commit` value in
[`python-artifacts.json`](python-artifacts.json) and [`native-artifacts.json`](native-artifacts.json).
Both ledgers must name the same full commit hash. Artifact ledger updates are evidence-only commits;
the frozen source has no subsequent package, workflow, test, or implementation changes.

The reference scan is defined by the dispositions above and the executable baseline check
`python scripts/check_python_311.py`. That check verifies the 23 workspace members, candidate
metadata/classifiers, typing targets, lockfile, interpreter matrices, native selectors, direct
typing backport dependencies, and scaffold requirements on the frozen source.

## Release evidence

- The Python artifact rehearsal run and retained build are linked by
  `retention_reference` in `python-artifacts.json`. It records two identical builds of the 22
  coordinated Python distributions (44 wheel and sdist files), Python 3.10 rejection, predecessor
  resolver fallback, and installed 1.1.3 application upgrade and rollback on Python 3.11.
- The native wheel run is linked by `workflow_run` in `native-artifacts.json`. It records all 16
  CPython 3.11–3.14 wheels across Linux x86_64, Linux ARM64, macOS ARM64, and Windows x64.
- The final `main` CI run is attached to the frozen source commit in GitHub checks. Its required
  summary, runtime matrix, dependency bounds, Chromium/Firefox/WebKit suites, package and quality
  checks, Workbench smoke, in-tree Connect contracts, and configured Connect smoke all passed.
- The strict local artifact verifier matched the Python rehearsal's 44 approved artifact hashes;
  the native inventory verifier accepted the 16 retained wheels.

The manifest's `FREEZE-120` review and `RELEASE-120` approval entries record this decision.
`release_cut_satisfied = true` authorizes the v1.2.0 release cut; publication remains a separate
release action.
