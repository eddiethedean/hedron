# REVIEW-033 security review brief

**Baseline:** Published `v0.32.0` tip; `hedron-workbench` / `fastapi-workbench` Supported Workbench
surface; Connect base-header helpers remain Experimental in inventory-029 until 0.33 native
graduation evidence.
**Package at cut:** `hedron-posit` `0.33.0` Beta + retained `hedron-workbench` `0.33.0` Beta.
**Owning decision:** D-061 / RFC-0066.
**Tracking:** [#167](https://github.com/eddiethedean/hedron/issues/167).

## Trust boundaries in scope

1. Package inversion / one-way dependency graph (`hedron-posit` must not import `hedron-workbench`)
2. Product resolution evidence (explicit / Connect / Workbench / inactive) and conflict fail-closed
3. Connect base header / ASGI `root_path` agreement; singular header; peer trust
4. Request/response cookie paths; owned-cookie allowlists; no Connect credentials as Hedron auth
5. Bridge secret/proxy/bypass/replay/logging **only if** Stage 0 keeps Supported bridge
6. Sessions / CSRF continuity under GUID (and vanity when declared Supported)
7. Diagnostics redaction (`HED-POSIT-*`); multi-worker / restart
8. Supply chain / offline install / SBOM / provenance for the new distribution
9. Rollback to ordinary `Hedron` / `hedron-workbench` without weaker security contracts

## Out of scope

- Posit Connect publishing, administration, or license management automation
- Renaming `fastapi-workbench` or adding `FastAPIPosit`
- Gradio / Web Component / presentation-quality programs as release blockers
- Commercial SLA / certification / Hedron `1.0`

## Adversarial suite

See [RELEASE_0_33.md](../RELEASE_0_33.md) “Required adversarial cases”. Suites land under
`tests/security/` and package-owned unit tests during Stage 2–4.

## Methodology

Structured maintainer-led review independent of the feature-authoring pass
(external firm optional). Findings land in `DISPOSITION.toml` and
`REDACTED_REPORT.md` at cut.

## Packet status

**Verified** — maintainer-led review complete for Supported 0.33 surface.
See `REDACTED_REPORT.md` and `DISPOSITION.toml` (`critical_high_open = false`).
