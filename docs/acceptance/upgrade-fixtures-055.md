# Upgrade fixtures for 0.55

PKG-055 upgrade source is **0.54** (`v0.54.0`).

## Compatibility modes

- `legacy` — existing action/form/security/layout behavior unchanged unless opted in.
- `workflow_055` — enables MasterDetail regions, capabilities, idempotency, UploadField,
  CSP reporting helpers, and workflow manifest consumers.

## Required fixtures

1. 0.54 app without 0.55 policies still renders and mutates identically.
2. Opt-in capability-gated action rejects unauthorized POST.
3. Opt-in idempotent action rejects conflicting replay.
4. Opt-in multipart UploadField cleans temp files on failure.
5. Offline `hedron upgrade-report --from 0.54 --to 0.55` emits JSON without network.
