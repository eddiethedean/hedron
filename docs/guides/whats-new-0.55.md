# What’s new in 0.55

Published in-tree **0.55.0** (PyPI still **0.54.0** while deferred). Pin
`hedron>=0.54.0,<0.55` from PyPI until the 0.55 wheel lands; checkout tip is
`0.55.0`.

## 0.55.0

Secure, upgradeable application workflows (RFC-0082 / D-095 / D-096;
[#544](https://github.com/eddiethedean/hedron/issues/544)–[#549](https://github.com/eddiethedean/hedron/issues/549)):

- `MasterDetail` responsive list/detail with named fragment regions.
- Request-bound `CapabilityProvider` with server-side action enforcement.
- Opt-in action `idempotency=` / `ReplayStore` with conflict outcomes.
- `UploadField` / `UploadHandle` multipart lifecycle with budgets and cleanup.
- CSP nonce helpers and bounded redacted report ingestion.
- Offline `hedron upgrade-report` JSON with reviewed baselines.
- Workflow manifest, reason codes, and budgets under `hedron.workflow`.
- Reference app: `examples/workflow-055/`.

All new APIs are opt-in `beta` (action kwargs, providers, and helpers). Existing apps
stay on legacy behavior until they opt in; `WorkflowManifest.migration_status` is for
inspection/upgrade reports, not a silent runtime switch.

See [Release notes](release-notes.md) and [Installation](../getting-started/installation.md).
