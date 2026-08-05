# Maintainer handbook

Index for contributors cutting releases, editing RFCs, and reading acceptance evidence.
**Adopters** should stay on [Learn](../getting-started/index.md) and
[What's ready today](whats-ready.md).

Maintainer corpus (RFCs, acceptance gates, STATUS, RELEASE, ROADMAP, decisions,
specification, and engineering baselines) lives in the repository on **GitHub only**.
Those files are excluded from the public MkDocs site so search and navigation stay
adopter-focused.

| Area | Source in the repo |
|---|---|
| Contributor setup | [Contributing](../CONTRIBUTING.md) |
| Day-to-day maintainer notes | [For maintainers](maintainers.md) |
| Authority / coding gates | [`docs/SPECIFICATION.md`](https://github.com/eddiethedean/hedron/blob/main/docs/SPECIFICATION.md) |
| Phase evidence | [`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md) |
| Capability phases | [`docs/ROADMAP.md`](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md) |
| Decisions | [`docs/DECISIONS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/DECISIONS.md) |
| Cut procedure | [`docs/RELEASE.md`](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md) |
| Scripts index | [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md) |
| RFC catalog | [`docs/rfcs/`](https://github.com/eddiethedean/hedron/tree/main/docs/rfcs) |
| Acceptance checklists | [`docs/acceptance/`](https://github.com/eddiethedean/hedron/tree/main/docs/acceptance) |
| Public evidence for evaluators | [Evidence pack](evidence-pack.md) |

!!! note "STATUS / ROADMAP sync"

    Edit `docs/STATUS.md` and `docs/ROADMAP.md`, then run
    `uv run python scripts/sync_status_roadmap.py` so root mirrors stay current.
    CI runs `scripts/sync_status_roadmap.py --check`.
