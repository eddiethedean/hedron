# Workflow APIs (0.55)

Phase 0.55 adds opt-in `beta` workflow contracts under `hedron.workflow` and related
modules. See [RFC-0082](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0082-SECURE-UPGRADEABLE-WORKFLOWS.md).

## Public entry points

- `hedron.workflow.WorkflowManifest` — redacted inspection model for Explorer/CLI/upgrade
- `hedron.workflow.ReasonCode` — `Literal` of allowed reason strings (not a constructor)
- `hedron.workflow.WorkflowBudget` — declared budgets for inspection (not all limits are
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

Pin and maturity follow the living **0.60** train; 0.55 workflow symbols remain
`beta`.

## Example

```python
from hedron import Hedron, Stack, Text
from hedron.workflow import WorkflowManifest

app = Hedron(title="Workflows", security="standard", session_secret="replace-me", explorer="off")

manifest = WorkflowManifest(
    app_id="order-approve",
    reason_codes=("allowed", "denied", "rejected"),
)


@app.screen("/", title="Home")
def home():
    return Stack(
        Text(f"Workflow: {manifest.app_id}"),
        Text("Use workflow helpers for upgradeable, capability-aware actions."),
    )
```

See the [secure upgradeable workflows](../guides/upgrade.md) notes and the RFC for
enforcement details. FastAPI owns capability/idempotency action kwargs; Flask/Django
layout pieces are portable but those kwargs remain unsupported on adapter hosts.
