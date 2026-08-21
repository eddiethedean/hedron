# What’s new in 0.55

Historical **0.55.0** in-tree Published cut (superseded by living tip **0.56.0**;
PyPI may still show **0.54.0** while deferred). Prefer
[What’s new in 0.56](whats-new-0.56.md) for the current train.

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
