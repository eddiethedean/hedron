# What’s new in Hedron 0.25

**Published** as `v0.25.0` (last 0.25 patch `v0.25.2`). Living train is **0.26** — pin `hedron>=0.26.0,<0.27`.

Phase **0.25** makes the production posture explicit: a runnable multi-worker archetype,
critical-path load budgets in CI, and an opt-in boundary so specialty experimental UI widgets are
not implied by `hedron[extras]`. Polling remains the Supported live-status story (from
0.24).

## For adopters

- **Reference app as production kitchen sink** — [`examples/reference-app`](../examples/reference-app.md)
  documents reverse-proxy subpath, Redis job/cache, signed sessions, `HEDRON_ENV=production`,
  CSP, Explorer off, and multi-worker. Prefer [session auth](../examples/session-auth.md) +
  [notes](../examples/notes-sqlalchemy.md) for a shorter path; use the reference app when you
  want the full checklist in one tree.
- **Ship checklist** — Follow [Ship a Hedron app](ship.md); maturity claims
  stay on [What’s ready](whats-ready.md).
- **Extras quarantine** — `CodeEditor` / `TerminalView` / joystick / device move behind
  `hedron[experimental-ui]` (and `hedron_extras.experimental`). Plain `hedron[extras]` no
  longer registers those experimental widgets as product UI.
- **Charts on 0.25.1** — the `hedron-charts 0.1.6` satellite restores
  `hedron[charts]>=0.26.0,<0.27`. Matplotlib/static charts remain the conservative default;
  Plotly / Altair stay experimental. See
  [Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).
- **Supply-chain evidence** — Train tags attach SBOM / evidence bundles in release CI.


## 0.25.2 patch

Additional fail-closed hardening on the published tip (see [release notes](release-notes.md)):

- Mount path rejects `..` / `%2e` segments; redirect prefixes re-validate with `is_local_path`.
- RedisStatusStore CAS matches RedisJobBackend; Celery/RQ cancel restore is CAS-only.
- Adapter prepare raises under a running loop; Flask gains `respond_async`.
- SSE/streaming force `Cache-Control: no-store`; adapter SSE accepts only `SseEvent`.
- SafeUrl/Hx require root-relative form/nav URLs; reserved OOB always wraps; WS swap validated.

## Upgrade notes

| If you… | Do this |
|---|---|
| Are on 0.24 | Pin `>=0.26.0,<0.27`; re-read [upgrade](upgrade.md#upgrade-from-024-025) |
| Used CodeEditor / TerminalView / joystick / device | Install `hedron[experimental-ui]` and import from `hedron_extras.experimental` |
| Deploy multi-worker | Prefer the reference-app compose archetype + Redis |

Contract: [PRODUCTION_ARCHETYPE.md](../api/PRODUCTION_ARCHETYPE.md) ·
[STABILITY.md](../api/STABILITY.md). Acceptance:
[RELEASE_0_25](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_25.md).

Human AT sessions (`SR-021` / …) remain Planned / not Supported.

## Maintainer gates (Verified)

`ARCHETYPE-025`, `BUDGET-025`, `EXTRAS-025`, `CHARTS-025`, `SUPPLY-025`, `REGRESS-025`,
`PKG-025`.
