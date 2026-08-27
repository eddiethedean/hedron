# Hedron 1.0 compatibility report

**Status:** Draft / blocked on the immutable `v1.0.0` artifact

This directory records executable bridge evidence without pretending that a
working-tree build is a published release. The canonical fixture suite is green
against the immutable 0.67 snapshot and the current 1.0.0 checkout, and the
workspace build produces all 22 declared distributions. The target-side rows
remain blocked until reproducible, retained v1.0.0 artifacts and a lock are
available; temporary build output is not treated as release evidence. Packaging
rehearsals fix `SOURCE_DATE_EPOCH=0`, and the native wheel has been verified
byte-for-byte reproducible under that input.

`python scripts/check_upgrade_100.py --baseline v0.67.0 --json` reruns the
canonical Python/HDJ/HTTP probe against both the immutable baseline and the
current checkout.

The report is intentionally fail-closed. A future cut must replace the blocked
target row with the exact artifact digest, Python/dependency environment,
adapter/satellite matrix, browser identity, and retained command output.
