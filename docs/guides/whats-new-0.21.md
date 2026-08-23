# What's new in 0.21

!!! note "Current train is 0.59"

    Pin `hedron>=0.53.0,<0.54` for new apps (checkout tip; current PyPI pin `>=0.58.0,<0.60`). The pin below is historical for this train only.
    See [What’s new in 0.51](whats-new-0.51.md).


**Published** as `v0.21.0`. Historical pin: `hedron>=0.21.0,<0.22`.

Phase 0.21 (D-052) is the human assistive-technology **engineering** train: protocol packet,
reference-app progressive-enhancement corpus, fragment allowlist parity, and release-gate
wiring. **Human AT sessions (`SR-021` / `PARTICIPANT-021`) remain Planned** — do not market
human AT as Supported. Automated AT (`AT-019` from 0.19) remains Supported and is not a
substitute for human AT.

## Highlights

- **Human AT packet** (`PROTOCOL-021` Verified) — protocol, privacy, task scripts, redacted
  ledger schema/example under `docs/acceptance/human-at/`;
  `scripts/check_human_at_packet.py` (+ `--require-sessions` / `--gate` floors for the
  Verified AT cut).
- **Reference-app PE** — create / update / delete succeed without `HX-Request` (303 redirect)
  and return `#user-table` fragments under HTMX; HTMX validation returns `ErrorState`.
- **Fragment allowlist parity** — FastAPI `@action` / `include_component` /
  `allow_undeclared_targets`; Flask `@action` + `respond(..., allow_undeclared_targets=...)`;
  Django `respond` same kwargs.
- **DataEditor** — Escape cancels edit without commit; 403 save responses skip `res.json()`.
- **Chart fragment host** — refresh/search target `#chart-panel` inside `#chart-region`; OOB
  status uses `element_id="oob-status"`.

CSRF composition (`CsrfField`, pluggable strategies, header merge) remains **0.22**.

See [upgrade](upgrade.md) · [what's ready](whats-ready.md) · [accessibility](accessibility.md) ·
[roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).
