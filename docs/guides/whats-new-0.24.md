# What’s new in Hedron 0.24

!!! note "Living train is 0.30"

    Pin `hedron>=0.32.0,<0.33`. The pin below is historical for this train only.
    See [What’s new in 0.30](whats-new-0.30.md).


**Published** as `v0.24.0`. Historical pin: `hedron>=0.24.0,<0.25`.

Phase **0.24** Accepted live-transport disposition **`polling_only`** (D-053 / RFC-0056):
polling is the Supported production story; SSE / WebSocket / streaming / preload helpers
remain **experimental** under `hedron.experimental`.

- **Disposition B (`polling_only`)** — ends the undecided experimental-live fog without
  claiming ops proof that was never produced.
- **Prior Deferred IDs superseded** — `BROWSER-10-001`, `PERF-10-001`, and
  `LIVE-011-BROWSER` close via waive ledgers under `BROWSER-024` / `PERF-024`.
- **Claim honesty unchanged** — adopter docs must not call experimental live transports
  unqualified Supported (`live_claims` + `check_docs_024.py`).
- **`EXPLORER-10-001`** stays Deferred on `0.10.x` (not re-homed).

Contract: [LIVE_DISPOSITION.md](../api/LIVE_DISPOSITION.md) ·
[STABILITY.md](../api/STABILITY.md). Acceptance:
[RELEASE_0_24](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_24.md).

Gates: `DECIDE-024`, `BROWSER-024`, `PERF-024`, `DOCS-024`, `REGRESS-024`, `PKG-024`
(all Verified).

Human AT sessions (`SR-021` / …) remain Planned / not Supported. Next: production
archetype / experimental-surface isolation (**0.25**).
