# Security review — phase 0.36 (redacted)

**Package / train at cut:** Hedron `v0.36.0` + Alpha `hedron-elements` `0.36.0`  
**Owning RFC:** RFC-0060 · **Gate:** `SECURITY-036` · **Tracking:** #92  
**Reviewer:** maintainer-led (2026-08-13)

## Findings

No open critical or high findings.

| ID | Severity | Summary | Disposition |
|---|---|---|---|
| EL-036-01 | info | Shared bridge is small and local; gzip ≤12 KiB verified in BROWSER-036 | accepted |
| EL-036-02 | info | Structured inputs use `application/json` inert scripts; size/depth bounded | accepted |
| EL-036-03 | low | Custom-element events remain untrusted; server must revalidate | accepted — documented |
| EL-036-04 | info | Form-associated controls deferred to 0.37; no ElementInternals authority in 0.36 | accepted |

## Adversarial coverage exercised

- Markup injection via server_content / closing tags
- Oversized structured inputs (`HED-ELEMENT-0005`)
- ABI/tag registration conflicts (`HED-ELEMENT-0001` / `0002` / `0003`)
- Capability fields refused for element-owned modes (`HED-ELEMENT-STATE-0002`)
- Draft transfer refused (`HED-ELEMENT-STATE-0006`)

## Residual risk

Alpha `hedron-elements` is not production-grade. Adopters must pin and treat the ABI as evolving until phase 0.41.
