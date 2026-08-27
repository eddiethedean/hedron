# Release process (summary)

Hedron ships a **coordinated 0.x train**. The living runbook with exact cut commands is:

**[docs/RELEASE.md on GitHub](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md)**

## Current train

| Item | Value |
|---|---|
| Stable release | **v0.66.2** (`hedron` / coordinated train packages) |
| Beta preview | **v0.67.0** |
| PyPI latest stable | **v0.66.2** (`hedron`; published 2026-08-26) |
| Pin (PyPI) | `hedron>=0.66.2,<0.67` |
| Charts satellite | `hedron-charts>=0.2.3,<0.3` |
| Gate checker | `python scripts/check_release_gate.py 0.67.0` |
| Packet verify | `python scripts/check_063.py --gate CONTRACT-063 --verify` |

Adopter-facing notes: [What’s new in 0.63](whats-new-0.63.md) ·
[Release notes](release-notes.md) · [Upgrade](upgrade.md) ·
[What’s ready](whats-ready.md).

Future tags require green CI on `main` and explicit maintainer authorization.
Do not retag prior train tags.

## Contributor checklist (abbreviated)

1. Edit `docs/STATUS.md` / `docs/ROADMAP.md`; sync STATUS with `uv run python scripts/sync_status_roadmap.py`
2. Pass `bash scripts/ci_checks.sh` suites required by the train
3. Verify release-gate TOML + `verify_pkg_N.py` for the cut
4. Tag `v0.N.0` **only if that tag is missing**, publish wheels, attach evidence assets

Do **not** retag or overwrite an existing published tag. Full steps and patch template:
GitHub [RELEASE.md](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md).
