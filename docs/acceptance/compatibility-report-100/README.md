# Hedron 1.0 compatibility report

**Status:** Draft / blocked on the immutable `v1.0.0` artifact

This directory records executable bridge evidence without pretending that the
current `v0.67.0` checkout is a second release. The canonical fixture suite is
green against the in-tree 0.67 implementation, and the workspace build produces
all 22 declared distributions. The target-side rows remain blocked until a
reproducible v1.0.0 wheel/sdist and lock are available; temporary build output is
not treated as retained release evidence.

`python scripts/check_upgrade_100.py --baseline v0.67.0 --json` reruns the
canonical Python/HDJ/HTTP probe against both the immutable baseline and the
current checkout.

The report is intentionally fail-closed. A future cut must replace the blocked
target row with the exact artifact digest, Python/dependency environment,
adapter/satellite matrix, browser identity, and retained command output.
