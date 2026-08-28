# Navigation, optimism, and failure isolation

These bounded contracts are available on 1.0 and were introduced in phase 0.62. They cover
navigation, optimistic edits, localized failures, and state identity. The server remains
authoritative and ordinary HTML/HTMX navigation remains the fallback.

## Navigation

Use `hedron_core.navigation.NavigationMachine` for one target's generation-safe lifecycle. A
response may commit only when its `NavigationIdentity` still matches the pending generation and
target. `NavigationPolicy` keeps retention, focus, scroll, and prefetch limits explicit.

FastAPI/Starlette responses can expose the identity with
`hedron.navigation.apply_navigation_headers`. The browser adapter is the opt-in
`hedron_elements/static/navigation-062.mjs` asset; mark links with
`data-hedron-navigation="enhance"` and a declared `data-hedron-target`. If the target, request,
script, or transition is unavailable, the link falls back to ordinary navigation.

Prefetch is progressive and disabled unless explicitly enabled. It permits only policy-approved
safe methods and same-origin URLs, applies bounded concurrency/bytes/cache behavior, and grants no
authority.

## Optimistic mutations

`OptimisticMutation.from_reversible_toggle`, `from_scalar_edit`, and the existing cell-edit adapter
are the approved 0.62 inventory. Every new adapter requires a base revision and idempotency key,
and must be confirmable, rollback-capable, and conflict-safe. Authorization, tenant, payment,
secret, destructive, and other uninventoried actions stay server-confirmed.

An uncertain response uses the explicit `unknown` state and must be reconciled with a refetch. It
is never treated as success or silently rolled back.

## Failure and identity boundaries

`FailureBoundary` localizes retryable errors to a declared target and propagates missing fallback,
fatal, or policy-defined shared-shell failures. `IdentityRegistry` requires one declared writer,
matching targets and schemas, and bounded JSON-compatible state transfer.

See the [0.62 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_62.md) for the locked risk inventory,
diagnostics, browser disposition, and release gates.
