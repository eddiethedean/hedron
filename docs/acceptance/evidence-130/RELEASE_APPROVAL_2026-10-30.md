# Phase 1.3 release approval and cut authorization

**Decision date:** 2026-10-30 (UTC)
**Approver:** Odos Matthews (`@eddiethedean`)
**Decision:** Approved for the Hedron `v1.3.0` release cut.
**Authorization source:** The maintainer explicitly instructed Codex in the release-preparation task to merge and approve all for release.

This approval closes `RELEASE-130` and sets `release_cut_satisfied = true`. It authorizes the release cut after the approved change is merged. It does not publish Python or native artifacts; publication remains a separate action.

## Verified candidate

The current evidence-bound source revision is `e153dccffac042e63e959672b9c95af59220e00e`. Relative to the approved package source revision `dec75e9ab60a5632ce9d63d8662f01589e2ccb4d`, its only change is the ops test assertion updated to validate the now-approved release state; package implementation and artifacts are unchanged.

All required CI passed on this revision:

- [Final PR CI run 40987606933](https://github.com/eddiethedean/hedron/actions/runs/40987606933), including branch coverage, strict typing/docs, packaging, minimum/latest dependency bounds, host acceptance on CPython 3.11–3.14, Chromium/Firefox/WebKit acceptance, supply-chain evidence, reproducible distribution rehearsal, and `CI required`.
- [Full CI dispatch 40988708468](https://github.com/eddiethedean/hedron/actions/runs/40988708468), including the Python 3.11, 3.13, and 3.14 test matrix plus the complete CI workflow.
- [Native wheel matrix 40987606890](https://github.com/eddiethedean/hedron/actions/runs/40987606890) on Linux x86_64, Linux ARM64, macOS ARM64, and Windows.

The retained [Python distribution manifest](python-artifacts-40987606933.json) records two byte-identical builds of all 22 coordinated packages (44 distributions). The [CPython 3.11 upgrade/rollback rehearsal](upgrade-rollback-40987606933.json) passed baseline, upgrade, and rollback with the original lock restored. The [CI report](ci-run-40987606933.json) retains the host/browser/resource/privacy reports, supply-chain bundle, native artifact inventory, run job identities, and artifact digests. All 39 retained acceptance JSON reports were scanned for randomized privacy canary patterns; no hits were found.

All 16 non-release gates were verified with retained evidence before this decision. The exact candidate contract and package dispositions have maintainer acceptance; the v1.2.0 predecessor publication is recorded.

## Cut and publication boundary

The release gate records approval and authorizes cutting `v1.3.0` after merge. No version tag has been created and no artifacts have been published as part of this approval. The release commit and any publication workflow must use the approved source and its retained artifact evidence.
