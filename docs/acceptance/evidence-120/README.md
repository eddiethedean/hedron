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

The native wheel run remains separate because it builds platform-specific wheels on Linux x86_64,
Linux ARM64, macOS, and Windows. Retain its successful run URL and downloaded wheel inventory with
the native evidence before marking `NATIVE-120` verified.

The final Python artifact ledger is intentionally absent until the rehearsal has run on the frozen
candidate. A placeholder or hash list copied from an earlier source commit is not release evidence.
