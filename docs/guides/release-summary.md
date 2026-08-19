# Release process (summary)

Hedron ships a **coordinated 0.x train**. The living runbook with exact cut commands is:

**[docs/RELEASE.md on GitHub](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md)**

## Current train

| Item | Value |
|---|---|
| In-tree | **v0.50.3** (`hedron` / Beta train packages `0.50.3`; Git tag/PyPI deferred) |
| PyPI latest | **v0.50.1** (`hedron` / Beta train `0.50.1`; independent Beta `hedron-maps` `0.1.0`; `hedron-charts` `0.2.0`; `hedron-mcp` `0.2.1`; `fastapi-workbench` `1.0.0`) |
| Pin (PyPI) | `hedron>=0.50.1,<0.51` |
| Charts satellite | `hedron-charts>=0.2.0,<0.3` |
| Gate checker | `python scripts/check_release_gate.py 0.50.3` |
| Packet verify | `python scripts/verify_pkg_50.py` |

Adopter-facing notes: [What’s new in 0.50](whats-new-0.50.md) ·
[Release notes](release-notes.md) · [Upgrade](upgrade.md) ·
[What’s ready](whats-ready.md).

Tag `v0.50.3` only after CI on `main` is green (not part of this in-tree cut). Do not retag `v0.50.1`, `v0.49.1`, `v0.48.0`, or `v0.47.0`.

## Contributor checklist (abbreviated)

1. Edit `docs/STATUS.md` / `docs/ROADMAP.md`; sync STATUS with `uv run python scripts/sync_status_roadmap.py`
2. Pass `bash scripts/ci_checks.sh` suites required by the train
3. Verify release-gate TOML + `verify_pkg_N.py` for the cut
4. Tag `v0.N.0` **only if that tag is missing**, publish wheels, attach evidence assets

Do **not** retag or overwrite an existing published tag. Full steps and patch template:
GitHub [RELEASE.md](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md).
