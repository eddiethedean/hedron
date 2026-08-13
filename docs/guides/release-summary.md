# Release process (summary)

Hedron ships a **coordinated 0.x train**. The living runbook with exact cut commands is:

**[docs/RELEASE.md on GitHub](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md)**

## Current train

| Item | Value |
|---|---|
| Published | **v0.34.0** (`hedron` / Beta packages `0.32.0`; `hedron-mcp` `0.2.0`; `fastapi-workbench` `1.0.0`) |
| Pin | `hedron>=0.34.0,<0.35` |
| Gate checker | `python scripts/check_release_gate.py 0.34.0` |
| Packet verify | `python scripts/verify_pkg_33.py` |

Adopter-facing notes: [What’s new in 0.32](whats-new-0.32.md) ·
[Release notes](release-notes.md) · [Upgrade](upgrade.md) ·
[What’s ready](whats-ready.md).

## Contributor checklist (abbreviated)

1. Sync STATUS/ROADMAP under `docs/`, then `uv run python scripts/sync_status_roadmap.py`
2. Pass `bash scripts/ci_checks.sh` suites required by the train
3. Verify release-gate TOML + `verify_pkg_N.py` for the cut
4. Tag `v0.N.0` **only if that tag is missing**, publish wheels, attach evidence assets

Do **not** retag or overwrite an existing published tag. Full steps and patch template:
GitHub [RELEASE.md](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md).
