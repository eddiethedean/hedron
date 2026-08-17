# Release process (summary)

Hedron ships a **coordinated 0.x train**. The living runbook with exact cut commands is:

**[docs/RELEASE.md on GitHub](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md)**

## Current train

| Item | Value |
|---|---|
| Published | **v0.45.0** (`hedron` / Beta train packages `0.45.0`; Beta `hedron-elements` `0.45.0`; independent Beta `hedron-charts` `0.2.0`; `hedron-mcp` `0.2.0`; `fastapi-workbench` `1.0.0`) |
| Pin | `hedron>=0.45.0,<0.46` |
| Charts satellite | `hedron-charts>=0.2.0,<0.3` |
| Gate checker | `python scripts/check_release_gate.py 0.45.0` |
| Packet verify | `python scripts/verify_pkg_45.py` |

Adopter-facing notes: [What’s new in 0.45](whats-new-0.45.md) ·
[Release notes](release-notes.md) · [Upgrade](upgrade.md) ·
[What’s ready](whats-ready.md).

The `v0.45.0` Git tag is not created until a maintainer executes the RELEASE.md tag
step on green `main`. Do not retag `v0.44.0`.

## Contributor checklist (abbreviated)

1. Edit `docs/STATUS.md` / `docs/ROADMAP.md`; sync STATUS with `uv run python scripts/sync_status_roadmap.py`
2. Pass `bash scripts/ci_checks.sh` suites required by the train
3. Verify release-gate TOML + `verify_pkg_N.py` for the cut
4. Tag `v0.N.0` **only if that tag is missing**, publish wheels, attach evidence assets

Do **not** retag or overwrite an existing published tag. Full steps and patch template:
GitHub [RELEASE.md](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md).
