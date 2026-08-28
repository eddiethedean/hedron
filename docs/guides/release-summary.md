# Release process summary

Hedron’s coordinated package train is preparing `v1.0.0`. The candidate is implemented and
Verified on branch `v1.0`; the public registry still serves `v0.66.2` until the authorized
publication workflow completes.

The exact maintainer commands and publication rules live in
[`docs/RELEASE.md`](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md).

## Current release facts

| Item | Value |
|---|---|
| Repository candidate | **v1.0.0** (`hedron` and coordinated packages) |
| Migration baseline | **v0.67.0** |
| PyPI latest | **v0.66.2** |
| Public-index pin | `hedron>=0.66.2,<0.67` |
| Repository development | `uv sync` (editable 1.0.0 workspace) |
| Charts satellite | `hedron-charts>=0.2.4,<0.3` |
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
5. Tag and publish only with explicit maintainer authorization.
6. After upload, verify PyPI artifacts and install smoke tests before changing
   `registry_status` to `uploaded` or publishing release notes.

Never retag or overwrite an existing published release.
