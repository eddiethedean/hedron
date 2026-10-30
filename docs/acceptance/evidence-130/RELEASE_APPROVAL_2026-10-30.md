# Phase 1.3 release approval and cut authorization

**Decision date:** 2026-10-30 (UTC)
**Approver:** Odos Matthews (`@eddiethedean`)
**Decision:** Approved for the Hedron `v1.3.0` release cut.
**Authorization source:** The maintainer explicitly instructed Codex in the release-preparation task to merge and approve all for release.

This approval closes `RELEASE-130` and sets `release_cut_satisfied = true`. It authorizes the release cut after the approved change is merged. It does not publish Python or native artifacts; publication remains a separate action.

## Verified candidate

The release candidate source is `dec75e9ab60a5632ce9d63d8662f01589e2ccb4d`. The following all passed:

- [Final PR CI run 40974810399](https://github.com/eddiethedean/hedron/actions/runs/40974810399), including required coverage, strict typing and docs, package install, minimum/latest dependency bounds, host acceptance on CPython 3.11–3.14, Chromium/Firefox/WebKit acceptance, supply-chain evidence, reproducible distribution rehearsal, and `CI required`.
- [Native wheel matrix 40974810366](https://github.com/eddiethedean/hedron/actions/runs/40974810366) on Linux x86_64, Linux ARM64, macOS ARM64, and Windows.
- [Build-only native wheel dispatch 40974767465](https://github.com/eddiethedean/hedron/actions/runs/40974767465), with PyPI and crates.io publishing disabled.
- The retained [Python distribution manifest](python-artifacts-40973136018.json) and [upgrade/rollback rehearsal](upgrade-rollback-40973136018.json).

All 16 non-release gates were verified with retained evidence before this decision. The exact candidate contract and package dispositions have maintainer acceptance; the v1.2.0 predecessor publication is recorded.

## Cut and publication boundary

The release gate records approval and authorizes cutting `v1.3.0` after merge. No version tag has been created and no artifacts have been published as part of this approval. The release commit and any publication workflow must use the approved source and its retained artifact evidence.
