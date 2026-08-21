# Release process (summary)

Hedron ships a **coordinated 0.x train**. The living runbook with exact cut commands is:

**[docs/RELEASE.md on GitHub](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md)**

## Current train

| Item | Value |
|---|---|
| In-tree | **v0.57.0** (`hedron` / Beta train packages `0.57.0`) |
| PyPI latest | **v0.56.0** (`hedron`; 0.57.0 upload is deferred) |
| Pin (PyPI) | `hedron>=0.56.0,<0.58` |
| Charts satellite | `hedron-charts>=0.2.0,<0.3` |
| Gate checker | `python scripts/check_release_gate.py 0.57.0` |
| Packet verify | `python scripts/verify_pkg_57.py` |

Adopter-facing notes: [What’s new in 0.57](whats-new-0.57.md) ·
[Release notes](release-notes.md) · [Upgrade](upgrade.md) ·
[What’s ready](whats-ready.md).

Tag `v0.57.0` only after CI on `main` is green (**do not tag yet** for this in-tree cut).
Do not retag prior train tags.

## Contributor checklist (abbreviated)

1. Edit `docs/STATUS.md` / `docs/ROADMAP.md`; sync STATUS with `uv run python scripts/sync_status_roadmap.py`
2. Pass `bash scripts/ci_checks.sh` suites required by the train
3. Verify release-gate TOML + `verify_pkg_N.py` for the cut
4. Tag `v0.N.0` **only if that tag is missing**, publish wheels, attach evidence assets

Do **not** retag or overwrite an existing published tag. Full steps and patch template:
GitHub [RELEASE.md](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md).
