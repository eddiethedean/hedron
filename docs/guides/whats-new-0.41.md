# What's new in Hedron 0.41

**Published** as `v0.41.0` on 2026-08-14 (in-tree tip; tag/PyPI may follow). Pin:
`hedron>=0.41.0,<0.42`. Charts remain on `hedron-charts>=0.2.0,<0.3`.

Phase **0.41** adds allowlisted typed browser composition, subject-bound draft transfer,
progressive navigation/restoration, content-free traces, and element/region failure isolation
([RFC-0060](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) / D-069).

## Highlights

- Allowlisted typed composition with schema / authz / bounds / fallback
- Draft-only `sessionStorage` transfer with subject namespace and single-consume clearing
- Native/HTMX navigation ownership with deterministic title/focus/scroll/popstate behavior
- Content-free traces and per-element/region failure containment
- Regression packet for the locked 0.41 issue list

## Honesty

- Human screen-reader / compensated AT (`SR-021`) remains **Planned** — not Supported.
- Live SSE / WebSocket / streaming remain **experimental**; polling is the Supported production
  story.
- Optional preload / View Transitions never affect correctness and honor reduced motion.

## See also

- [Upgrade to 0.41](upgrade.md)
- [Release notes](release-notes.md)
- [RELEASE_0_41](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_41.md)
