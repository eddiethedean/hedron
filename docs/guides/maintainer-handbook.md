# Maintainer handbook

Index for contributors cutting releases, editing RFCs, and reading acceptance evidence.
**Adopters** should stay on [Start](../getting-started/index.md) and
[What's ready today](whats-ready.md) — this page is not part of the day-one product path.

Maintainer corpus (RFCs, acceptance gates, STATUS, RELEASE, ROADMAP, decisions,
specification, and engineering baselines) lives in the repository on **GitHub only**.
Those files are excluded from the public MkDocs site so search and navigation stay
adopter-focused. The adopter maturity snapshot is **What's ready today** only.

| Area | Source in the repo |
|---|---|
| Contributor setup | [Contributing](../CONTRIBUTING.md) |
| Authority / coding gates | [`docs/SPECIFICATION.md`](https://github.com/eddiethedean/hedron/blob/main/docs/SPECIFICATION.md) |
| Phase evidence | [`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md) |
| Capability phases | [Roadmap](../ROADMAP.md) |
| Decisions | [`docs/DECISIONS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/DECISIONS.md) |
| Cut procedure | [`docs/RELEASE.md`](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md) (living); historical cuts in [`docs/archive/`](https://github.com/eddiethedean/hedron/tree/main/docs/archive) |
| Production-quality program | [Production-quality maturity](production-quality.md) (D-053 / RFC-0056) |
| Scripts index | [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md) |
| RFC catalog | [`docs/rfcs/`](https://github.com/eddiethedean/hedron/tree/main/docs/rfcs) |
| Foundations | [`docs/foundations/`](https://github.com/eddiethedean/hedron/tree/main/docs/foundations) |
| Implementation contracts | [`docs/implementation/`](https://github.com/eddiethedean/hedron/tree/main/docs/implementation) |
| Acceptance checklists | [`docs/acceptance/`](https://github.com/eddiethedean/hedron/tree/main/docs/acceptance) |
| Feature research | [`docs/guides/feature-research.md`](https://github.com/eddiethedean/hedron/blob/main/docs/guides/feature-research.md) |
| Competitive / adapter research notes | Repo `docs/*FEATURE*`, `docs/*ADAPTER_RESEARCH*`, `docs/HTMX_2_*` — **excluded from the public MkDocs site**; browse on GitHub only |
| Public evidence for evaluators | [Evidence pack](evidence-pack.md) |

!!! note "STATUS sync"

    Edit `docs/STATUS.md`, then run
    `uv run python scripts/sync_status_roadmap.py` so root `STATUS.md` stays current.
    The roadmap is only `docs/ROADMAP.md` (edit it in place; no generated copies).
    MkDocs does **not** copy root → docs (that previously clobbered docs edits).
    CI runs `scripts/sync_status_roadmap.py --check`.

!!! note "Historical RFC"

    [RFC-0005 HDN](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0005-HDN-LANGUAGE.md)
    is historical; HDJ replaced HDN in 0.9.
