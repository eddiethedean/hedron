# Security review brief — phase 0.34 (`hedron-gradio`)

**Package at cut:** `hedron-gradio` `0.2.0` Beta  
**Owning RFC:** [RFC-0067](../rfcs/RFC-0067-PRODUCTION-GRADE-GRADIO.md)  
**Gate:** `REVIEW-034`  
**Tracking:** [#90](https://github.com/eddiethedean/hedron/issues/90)

## Scope

Independent review of the **Supported** remote client-interop surface:

- Destination allowlist and SSRF/redirect/TLS defenses (`EGRESS-034`)
- File and stream bounds, artifact retention, cleanup (`FILES-034`)
- Job timeout, cancellation, disconnect, polling integration (`JOBS-034`)
- HF token scope and diagnostic redaction (`VENDOR-034`)
- Disabled-by-default adapter; no ambient authority on install

## Out of scope

- Gradio UI runtime, share tunnels, MCP auto-composition
- Application-owned authorization of remote model output
- Default presentation refresh (`PRESENT-034`)

## Required artifacts at cut

- `REDACTED_REPORT.md` — findings with severity and disposition
- `DISPOSITION.toml` — machine-checked closure of critical/high items

## Review questions

1. Can an attacker reach undeclared hosts via redirects, DNS, or encoded URLs?
2. Do logs/errors ever emit HF tokens or Authorization material?
3. Can artifact storage grow without bound or escape temp directories?
4. Are job ids enumerable across tenants/scopes under multi-worker polling?
5. Does disabled/default-off behavior hold when the package is installed but unused?

## Status

**Planned** — maintainer-led or external review completes before `REVIEW-034` Verified at cut.
