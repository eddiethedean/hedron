# Phase 1.2 release evidence

This directory holds evidence tied to the frozen v1.2.0 source. Keep source changes out of
evidence-only commits after artifact hashes are recorded; the artifact verifier rejects a ledger
whose source commit is followed by package, workflow, test, or implementation changes.

## Python release artifacts

**Release artifact rehearsal (1.2.0)** runs for relevant pushes to `main` and can also be manually
dispatched. On the frozen source commit, it builds all 22
Python distributions in `release/publish-order.toml` except `hedron-native`, which is built and
published by the native wheel workflow. It builds the set twice with `SOURCE_DATE_EPOCH=315619200`,
requires one wheel and one sdist per distribution, compares the complete inventories and SHA-256
hashes, proves that the 1.2.0 wheel is rejected by Python 3.10 and that an unpinned Python 3.10
resolver selects the 1.1.3 predecessor, and retains both builds plus the ledgers in the Actions run
for 90 days. On Python 3.11 it also installs the published 1.1.3 scaffold, upgrades it using the
candidate Hedron and hedron-core wheels, restores the original project and lock, and checks the app
after each step. All results and candidate wheel digests are included in `python-artifacts.json`.

Download `python-artifacts.json` from that Actions artifact, review its source commit, environment,
package list, hashes, and retention reference, then place the reviewed file at
`python-artifacts.json` in this directory. Commit that evidence file by itself after the frozen
source commit. The 1.2.0 publish workflow checks the ledger against the newly built 44-file release
set and rejects missing, changed, extra, stale, or non-reproducible artifacts.

The native wheel matrix workflow in `.github/workflows/native-wheels-ci.yml` builds and tests
CPython 3.11–3.14 wheels on Linux x86_64, Linux ARM64, macOS ARM64, and Windows x64. It rejects a
missing interpreter or platform wheel and retains the 16-wheel inventory, binary hashes, and
combined evidence artifact for 90 days. The publishing workflow uses the same cibuildwheel version
and per-wheel conformance command. Retain the successful run URL and reviewed
`native-artifacts.json` at this path in the evidence-only commit alongside `python-artifacts.json`
before marking `NATIVE-120` verified.

The Python artifact ledger must come from a successful rehearsal on the frozen source commit. If
package, workflow, test, or implementation files change afterward, rerun the Python rehearsal and
native wheel matrix on the updated source before replacing both ledgers. A placeholder or hash list
copied from an earlier source commit is not release evidence.
