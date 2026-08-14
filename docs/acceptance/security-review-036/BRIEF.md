# Security review brief — phase 0.36 (Web Component ABI)

**Package / train at cut:** Hedron `v0.36.0` + Alpha `hedron-elements` `0.36.0`  
**Owning RFC:** [RFC-0060](../../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md)  
**Gate:** `SECURITY-036` (cross-cutting with `SSR-036` / `PKG-036`)  
**Tracking:** [#92](https://github.com/eddiethedean/hedron/issues/92)

## Scope

Independent review of the **element ABI / bridge** surface:

- Strict CSP and Trusted Types without inline handlers, `eval`, or remote runtime fetches
- Structured-input escaping, bounds, and non-executable encoding
- Event detail schema validation; no secrets/capabilities/DOM/executable values in events
- Version skew / ABI mismatch fails closed with usable SSR fallback
- Local fingerprinted modules; no CDN defaults for Supported assets
- Registration conflicts and `HED-ELEMENT-*` diagnostics redact payloads

## Out of scope

- Form-associated controls, `InteractionState`, gestures (phase 0.37)
- High-fidelity charts (phase 0.38) and optimistic/rich-surface adapters (phase 0.39)
- Production-grade / `stable` promotion (phase 0.42)
- Reopening `polling_only` live-transport disposition
- Treating Shadow DOM or element events as an authorization boundary

## Required artifacts at cut

- `REDACTED_REPORT.md` — findings with severity and disposition
- `DISPOSITION.toml` — machine-checked closure of critical/high items

## Review questions

1. Can an incompatible module/markup pair execute or silently override server fallback?
2. Do structured inputs or event details ever carry secrets, trusted HTML, or executable callbacks?
3. Does the shared bridge stay within the 12 KiB gzip budget without undeclared executable assets?
4. Are CSP / Trusted Types scenarios enforced for upgrade, swap, and failed-module paths?
5. Do diagnostics redact payloads while remaining actionable for operators?

## Status

**Verified** (2026-08-13) — maintainer-led review complete; see `REDACTED_REPORT.md` and `DISPOSITION.toml`.
