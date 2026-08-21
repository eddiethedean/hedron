# Workflow APIs (0.55)

Phase 0.55 adds opt-in `beta` workflow contracts under `hedron.workflow` and related
modules. See [RFC-0082](../rfcs/RFC-0082-SECURE-UPGRADEABLE-WORKFLOWS.md).

## Public entry points

- `hedron.workflow.WorkflowManifest`
- `hedron.workflow.ReasonCode`
- `hedron.workflow.WorkflowBudget`
- `hedron.capabilities.Capability` / `CapabilityProvider`
- `hedron.replay.IdempotencyPolicy` / `MemoryReplayStore`
- `hedron.upload.UploadField` / `UploadHandle`
- `hedron.csp.NonceContext` / `ingest_csp_report`
- `hedron_core.builtins.MasterDetail`
- CLI: `hedron upgrade-report`

Pin and maturity follow the living train; new symbols are `beta` for the first
0.55 release.
