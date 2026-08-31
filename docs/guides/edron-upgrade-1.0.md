---
description: Upgrade an Edron 0.9 application to the stable 1.0 contract.
---

# Upgrade Edron 0.9 to 1.0

Edron 1.0 freezes the public page, fragment, action, resource, data, job, and deployment
contracts documented in the 1.0 reference. Upgrade in a branch and keep the old environment
available until the application passes its own integration tests.

## 1. Update the dependency requirement

```bash
uv add "edron>=1.0.0"
# or: python -m pip install -U "edron>=1.0.0"

# For repository development, use `uv sync` from the checkout.
```

## 2. Run static checks before importing the app

```bash
edron check app.py --format text
```

Review every error and warning. Migration tools never execute or overwrite untrusted input.

## 3. Verify native escape hatches

Use `app.native` to access the underlying Hedron application. If code resolves the Hedron
object registered for an Edron surface, use `app.native_surface(surface)`.

## 4. Verify application boundaries

- Page instances remain request-local, not session state.
- Actions own authorization, validation, transactions, and idempotency.
- Multi-worker deployments use shared state, cache, and job backends.
- Diagnostic metadata names secret references, never secret values.

## 5. Exercise the deployed shape

```bash
edron explain app:app
edron doctor app:app --profile container
edron deploy-check --profile container
```

Then run browser/integration tests for forms, CSRF, authorization, root paths, assets, and
background work before switching production traffic.
