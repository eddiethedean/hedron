# What's new in 0.20

**Published** as `v0.20.0`. Historical installs for this phase used a 0.20 upper-bound
pin; prefer the current `hedron>=0.56.0,<0.57` (PyPI) or `>=0.56.0,<0.57` (tip) train for new apps.

Phase 0.20 (D-051) is the production security floor and adapter-parity packet.

## Highlights

- **HTMX browser presets** (`HTMX-020`) — `standard`/`strict` disable eval, response scripts,
  and history cache; inspect with `SecurityPolicy.htmx_config_json()`; opt out via
  `htmx_browser_preset=False` or own `htmx-config` meta.
- **Python `js:` reject** (`EVAL-020`) — `html.*` rejects `hx-vals`/`hx-headers` `js:` by
  default (`HED-SEC-0011`); opt in with `allow_htmx_eval()` / `allow_htmx_eval=True`.
- **Mount path helpers** (`MOUNT-020`) — `resolve_mount_path`, `HEDRON_ROOT_PATH`, cookie
  `Path=auto`, single-prefix local redirects.
- **Production security gates** (`PROD-020`) — fail-closed weak secrets, development profile,
  Explorer, open redirects, missing CSP; override only via
  `HEDRON_SECURITY_RISK_ACCEPTANCE`.
- **Adapter parity** — Flask/Django `fragment_regions` on `InteractionResult` (`REGION-020`),
  portable `SecurityPolicy` headers from `hedron-core` (`CSP-020`), Flask-Login AuthSignal
  preference (`AUTH-020`).
- **`hedron new --flask` / `--django`** (`SCAFFOLD-020`) and CI adapter wheel smoke
  (`WHEEL-020`).

CSRF composition (`CsrfField`, pluggable strategies, header merge) remains **0.22**.
Human AT evaluation remains **0.21** (D-050).

See [upgrade](upgrade.md) · [what's ready](whats-ready.md) · [roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/ROADMAP.md).
