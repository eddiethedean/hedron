# Edron 0.7 → 0.8 upgrade fixtures

The 0.8 deployment contract changes the package train and adds deployment metadata. It does not
change Edron page, action, data, job, or native-object identity contracts.

## Required fixture facts

1. An existing 0.7 application can install `edron>=0.8,<0.9` against the compatible Hedron train
   without importing a second Edron runtime.
2. A production deployment runs `hedron build` again and ships the resulting `manifest.json`; a
   missing or invalid manifest fails startup/checks before serving application routes.
3. Root path, cookie path, CSRF, redirect, static asset, and HTMX URLs remain one native mounted-path
   contract when the deployment profile changes from `single-process` to `reverse-proxy`.
4. Multi-worker deployments explicitly declare shared state and job backends. Process-local claims
   are retained as findings and are never silently promoted during upgrade.
5. Rollback restores the prior application artifact and package pin only. Application-owned data
   migrations, queued work, secret rotation, and external side effects require a separate runbook.
6. Artifact records contain package/version identity, SHA-256, size, license/SBOM/provenance links,
   and exact verification commands; no secret, absolute source path, or runtime install instruction
   is embedded in the Edron report.

## Compatibility disposition

| Surface | 0.8 disposition |
|---|---|
| Page, fragment, action, form, data, chart, map, job, and native ejection APIs | Preserved |
| `edron check`, `edron explain`, `edron doctor` | Preserved; `doctor` may include deployment facts |
| New `edron deploy-check` command | Added, read-only |
| `edron>=0.7,<0.8` generated pins | Regenerated as `edron>=0.8,<0.9` |
| Flask/Django Edron page-class parity | Not introduced |
| Notebook production hosting / cloud provisioning | Not introduced |
