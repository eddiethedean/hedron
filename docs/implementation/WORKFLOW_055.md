# Implementation notes: phase 0.55 workflows

**Decision/RFC:** D-095, refined by D-096 /
[RFC-0082](../rfcs/RFC-0082-SECURE-UPGRADEABLE-WORKFLOWS.md)<br>
**Shared schema:** `hedron.workflow`

## Consume shipped, do not fork (D-096)

Extend `SecurityPolicy`, `AppShell`/`SplitView`, `@app.action` / `_wrap_endpoint`,
`FileUpload` / `FormBody`, and route/effect catalogs. Do not introduce parallel
registries.

## Stage 1 module map

| Module | Responsibility |
|---|---|
| `hedron_core.builtins.layout.MasterDetail` | Layout regions |
| `hedron.capabilities` | CapabilityProvider |
| `hedron.replay` | IdempotencyPolicy / ReplayStore |
| `hedron.upload` | UploadField / UploadHandle |
| `hedron.csp` | NonceContext / ingest_csp_report |
| `hedron.workflow` | Manifest, reason codes, budgets, upgrade report |
