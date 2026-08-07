# Hedron `v0.20` production security floor and adapter parity acceptance

Phase 0.20 delivers HTMX browser hardening, Python `html.*` eval-attribute reject, trusted
mount-path helpers, production startup security gates, Flask/Django fragment-region and
profile-header parity, Flask-Login AuthSignal verify/docs, adapter scaffolds, and clean-wheel
smoke — without becoming an identity provider or inventing a pluggable CSRF protocol.
Evidence is indexed by [`release-gate-0.20.toml`](release-gate-0.20.toml).
**Zero Deferred:** every 0.20-owned gate row must be Verified at cut.

Owning RFCs: [RFC-0012](../rfcs/RFC-0012-SECURITY.md),
[RFC-0021](../rfcs/RFC-0021-BROWSER-RUNTIME.md),
[RFC-0028](../rfcs/RFC-0028-DEPLOYMENT.md). Decision: [D-051](../DECISIONS.md).

Issues [#1](https://github.com/eddiethedean/hedron/issues/1),
[#3](https://github.com/eddiethedean/hedron/issues/3),
[#6](https://github.com/eddiethedean/hedron/issues/6),
[#12](https://github.com/eddiethedean/hedron/issues/12),
[#14](https://github.com/eddiethedean/hedron/issues/14),
[#17](https://github.com/eddiethedean/hedron/issues/17),
[#18](https://github.com/eddiethedean/hedron/issues/18),
[#19](https://github.com/eddiethedean/hedron/issues/19), and
[#20](https://github.com/eddiethedean/hedron/issues/20) remain normative for gate acceptance.
CSRF composition ([#36](https://github.com/eddiethedean/hedron/issues/36)–[#38](https://github.com/eddiethedean/hedron/issues/38))
is owned by **0.22**, not this checklist.

## Spec packet

- [x] ROADMAP §0.20 scope accepted; D-051 recorded; §0.22 split named.
- [x] RFC-0012 / RFC-0021 / RFC-0028 baselines current for host floor deltas (no new RFC numbers).
- [x] Entry gate: 0.19 evidence remains closed or Ready to cut; 0.20 gate TOML owns
  Planned→Verified rows only.
- [x] Gate checker recognizes `0.20` (`python scripts/check_release_gate.py 0.20.0 --allow-planned`).

## HTMX browser + attribute floor

- [x] Documented `standard` / `strict` HTMX browser preset with inspectable opt-out. *(`HTMX-020`)*
- [x] Reject `hx-vals` / `hx-headers` `js:` on Python `html.*` (HDJ parity). *(`EVAL-020`)*

## Production and deployment fail-closed

- [x] Trusted mount-path / cookie `Path=auto` / redirect prefix helpers. *(`MOUNT-020`)*
- [x] Fail-closed production startup gates under `HEDRON_ENV=production`. *(`PROD-020`)*

## Adapter parity

- [x] Flask/Django `fragment_regions` + starters/examples truth. *(`REGION-020`)*
- [x] Profile security headers applied on Flask/Django without FastAPI imports. *(`CSP-020`)*
- [x] Flask-Login `AuthSignal` bridge verified and documented. *(`AUTH-020`)*

## Adapter DX and CI

- [x] `hedron new --flask` / `--django` secure scaffolds. *(`SCAFFOLD-020`)*
- [x] CI clean-wheel smoke for `hedron_flask` / `hedron_django`. *(`WHEEL-020`)*

## Packaging

- [x] Coordinated package verify (`scripts/verify_pkg_20.py`). *(`PKG-020`)*

## Exit

- [x] Full regression suite. *(`REGRESS-020`)*

**Exit met** — coordinated `0.20.0` (**Ready to cut / Implemented on `main`**; last published
PyPI/git = `v0.19.0`); every 0.20 gate row Verified.
