# Release process (summary)

Hedron ships a **coordinated 0.x train**. The living runbook with exact cut commands is:

**[docs/RELEASE.md on GitHub](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md)**

## Current train

| Item | Value |
|---|---|
| In-tree | **v0.52.0** (`hedron` / Beta train packages `0.52.0`) |
| PyPI latest | **v0.56.0** (`hedron`; the repository train is `0.56.x` and its upload is deferred) |
| Pin (PyPI) | `hedron>=0.56.0,<0.57` |
| Charts satellite | `hedron-charts>=0.2.0,<0.3` |
| Gate checker | `python scripts/check_release_gate.py 0.52.0` |
| Packet verify | `python scripts/verify_pkg_52.py` |

Adopter-facing notes: [What’s new in 0.52](whats-new-0.52.md) ·
[Release notes](release-notes.md) · [Upgrade](upgrade.md) ·
[What’s ready](whats-ready.md).

Tag `v0.52.0` only after CI on `main` is green (**do not tag yet** for this in-tree cut). Do not retag `v0.51.2`, `v0.51.1`, `v0.51.0`, `v0.50.3`, `v0.50.2`, `v0.50.1`, or `v0.50.0`.

## Contributor checklist (abbreviated)

1. Edit `docs/STATUS.md` / `docs/ROADMAP.md`; sync STATUS with `uv run python scripts/sync_status_roadmap.py`
2. Pass `bash scripts/ci_checks.sh` suites required by the train
3. Verify release-gate TOML + `verify_pkg_N.py` for the cut
4. Tag `v0.N.0` **only if that tag is missing**, publish wheels, attach evidence assets

Do **not** retag or overwrite an existing published tag. Full steps and patch template:
GitHub [RELEASE.md](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md).
