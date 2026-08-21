# Workflow APIs (0.55)

Phase 0.55 adds opt-in `beta` workflow contracts under `hedron.workflow` and related
modules. See [RFC-0082](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0082-SECURE-UPGRADEABLE-WORKFLOWS.md).

## Public entry points

- `hedron.workflow.WorkflowManifest`
- `hedron.workflow.ReasonCode`
- `hedron.workflow.WorkflowBudget` (declared budgets for inspection; not all limits are
  auto-enforced on every request path)
- `hedron.capabilities.Capability` / `CapabilityProvider`
- `hedron.replay.IdempotencyPolicy` / `MemoryReplayStore`
- `hedron.upload.UploadField` / `UploadHandle` (buffered materialization)
- `hedron.csp.NonceContext` / `ingest_csp_report` / `compose_csp` (helpers; apps opt in
  to managed headers)
- `hedron_core.builtins.MasterDetail`
- CLI: `hedron upgrade-report`

FastAPI owns action `capability=` / `idempotency=` enforcement introduced in the
0.55 workflow train. Flask/Django layout components are portable; capability and
replay action kwargs remain `unsupported` on those adapters
(`docs/acceptance/workflow-parity-055.toml`).

Pin and maturity follow the living **0.58** train; 0.55 workflow symbols remain
`beta`.
