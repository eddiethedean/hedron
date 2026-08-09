# What’s new in Hedron 0.25

**Published** as `v0.25.0`. Pin `hedron>=0.25.0,<0.26`.

Phase **0.25** ships the production archetype and landmine quarantine packet (D-053 /
RFC-0056):

- **`examples/reference-app`** is the canonical multi-worker production archetype
  (reverse-proxy subpath, Redis job/cache, signed cookie sessions, `HEDRON_ENV=production`,
  CSP, Explorer off, multi-worker).
- **`BUDGET-025`** — runnable CI evidence for `W-025-FRAGMENT`, `W-025-JOB-POLL`, and
  `W-025-DATAEDITOR`.
- **`EXTRAS-025` quarantine** — `CodeEditor` / `TerminalView` / joystick / device move behind
  **`hedron[experimental-ui]`** so `hedron[extras]` does not imply product UI.
- **`CHARTS-025`** — Matplotlib remains the conservative Supported charts default; Plotly /
  Altair stay experimental (graduation checklist documented).
- **`SUPPLY-025`** — RELEASE requires SBOM / evidence-bundle attach on every train tag
  (fail-closed in release CI).

Contract: [PRODUCTION_ARCHETYPE.md](../api/PRODUCTION_ARCHETYPE.md) ·
[STABILITY.md](../api/STABILITY.md). Acceptance:
[RELEASE_0_25](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_25.md).

Gates: `ARCHETYPE-025`, `BUDGET-025`, `EXTRAS-025`, `CHARTS-025`, `SUPPLY-025`,
`REGRESS-025`, `PKG-025` (all Verified).

Human AT sessions (`SR-021` / …) remain Planned / not Supported.
