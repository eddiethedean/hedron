# Hedron 1.0 compatibility report

**Status:** Verified candidate evidence; publication remains deferred until an authorized tag and registry upload

This directory records executable bridge evidence without pretending that a
working-tree build is a published release. The canonical fixture suite is green
against the immutable 0.67 snapshot and the current 1.0.0 checkout, and the
workspace build produces all 22 declared distributions. The target-side rows are
verified against reproducible candidate artifacts and a committed hash lock;
temporary build output is not treated as a public release. Packaging
rehearsals fix `SOURCE_DATE_EPOCH=315619200` and disable maturin's non-deterministic
generated Rust SBOM; all 44 workspace artifacts, including the native wheel,
are byte-for-byte reproducible under that input. The retained
[`local-build-evidence.json`](local-build-evidence.json) records SHA-256s for
the 26 coordinated 1.0.0 artifacts; the corresponding files remain temporary
and are deliberately not treated as published release artifacts.

The [`verification-100.json`](verification-100.json) ledger records the exact
local phase, bridge, quality, Chromium/Firefox/WebKit browser, and
reproducible-build checks. Historical 0.x alias fixtures are explicitly retired
on the 1.0 train by the test harness; they remain available when the same suite
is run against the immutable 0.67 baseline. The ledger deliberately keeps command
output non-retained and records release evidence separately from public publication.

`python scripts/check_upgrade_100.py --baseline v0.67.0 --json` reruns the
canonical Python/HDJ/HTTP probe against both the immutable baseline and the
current checkout.

The report is intentionally fail-closed. A future cut must replace the blocked
target row with the exact artifact digest, Python/dependency environment,
adapter/satellite matrix, browser identity, and retained command output.
