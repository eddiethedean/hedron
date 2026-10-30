# Phase 1.3 release approval and cut authorization

**Decision date:** 2026-10-30 (UTC)
**Approver:** Odos Matthews (`@eddiethedean`)
**Decision:** Approved for the Hedron `v1.3.0` release cut.
**Authorization source:** The maintainer explicitly instructed Codex in the release-preparation task to merge and approve all for release.

This approval closes `RELEASE-130` and sets `release_cut_satisfied = true`. It authorizes the release cut after the approved change is merged. It does not publish Python or native artifacts; publication remains a separate action.

## Verified candidate

The original approved candidate was built at `e153dccffac042e63e959672b9c95af59220e00e`. After merge, the release tag preflight correctly rejected five documentation/simulator changes that entered through the mainline merge and were not included in that candidate. No package was published. The merged source at `a99ddec3333d5773f0d6b8e3ffda70a1ba486eee` was rechecked by main CI and the native wheel matrix; the release artifact rehearsal was repeated from evidence commit `8bacd7075c6302d1b953a4aeb739fc14f6e2cb16`, whose only changes from the tested merge commit were release evidence records.

All required CI passed on this revision:

- [Final PR CI run 40987606933](https://github.com/eddiethedean/hedron/actions/runs/40987606933), including branch coverage, strict typing/docs, packaging, minimum/latest dependency bounds, host acceptance on CPython 3.11–3.14, Chromium/Firefox/WebKit acceptance, supply-chain evidence, reproducible distribution rehearsal, and `CI required`.
- [Full CI dispatch 40988708468](https://github.com/eddiethedean/hedron/actions/runs/40988708468), including the Python 3.11, 3.13, and 3.14 test matrix plus the complete CI workflow.
- [Native wheel matrix 40987606890](https://github.com/eddiethedean/hedron/actions/runs/40987606890) on Linux x86_64, Linux ARM64, macOS ARM64, and Windows.

The refreshed [Python distribution manifest](python-artifacts.json) records two byte-identical builds of all 22 coordinated packages (44 distributions) from the merged source, and the retained builds are available from [workflow run 40993249628](https://github.com/eddiethedean/hedron/actions/runs/40993249628). The refreshed [CPython 3.11 upgrade/rollback rehearsal](recheck-40993249628/upgrade-rollback-1.3.json) passed baseline, upgrade, and rollback with the original lock restored. The [merge-commit CI and native matrix record](ci-run-40990900936.json) links successful validation on the merged source. The earlier 39 retained acceptance reports remain attached to the PR candidate.

All 16 non-release gates were verified with retained evidence before this decision. The exact candidate contract and package dispositions have maintainer acceptance; the v1.2.0 predecessor publication is recorded.

## Cut and publication boundary

The maintainer instructed Codex to merge and approve all for release. That authorization covers the refreshed candidate and its exact reproduced artifact set. The first tag-triggered workflow stopped at strict source validation before publication; the corrected release commit must use the refreshed source and retained artifact evidence.
