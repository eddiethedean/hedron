# Release process summary

Hedron’s coordinated `v1.0.1` package train is tagged, published, and Verified.

The exact maintainer commands and publication rules live in
[`docs/RELEASE.md`](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md).

## Current release facts

| Item | Value |
|---|---|
| Current stable release | **v1.0.1** (`hedron`, `hedron-core`, `edron`, `hedron-data`, `hedron-charts`, and `hedron-maps`) |
| Migration baseline | **v0.67.0** |
| PyPI latest | **v1.0.1** |
| Public-index pin | `hedron>=1.0.1,<1.1` |
| Repository development | `uv sync` (editable 1.0.1 workspace) |
| Charts package | `hedron-charts>=1.0.0,<2.0` |
| Maps package | `hedron-maps>=1.0.0,<2.0` |
| Generic Workbench adapter | `fastapi-workbench>=1.0.1,<2.0` |
| Plan checker | `python scripts/check_100.py --check-plan` |
| Entry gate | `python scripts/check_100.py --gate ENTRY-100 --verify` |

Adopter-facing sources of truth: [Current release](current-release.md) ·
[What’s new in 1.0](whats-new-1.0.md) · [Upgrade](upgrade.md) ·
[What’s ready](whats-ready.md).

## Contributor checklist

1. Update `docs/release.toml` first when release-channel facts change.
2. Synchronize `docs/STATUS.md` to root `STATUS.md`.
3. Run `bash scripts/ci_checks.sh docs`, the 1.0 packet checker, tests, lint, and package checks.
4. Build all packages and test the built artifacts in a clean environment.
5. Tag and publish only with explicit maintainer authorization; never move an existing tag.
6. After upload, verify PyPI artifacts and install smoke tests before changing
   `registry_status` to `uploaded` or publishing release notes.

Never retag or overwrite an existing published release.
