# Plugin loader implementation

## Discovery and selection

Plugins are discovered through a documented Python packaging entry-point group and may also be explicitly registered. Configuration filters enabled plugins before imports where possible. Discovery order never determines semantic priority.

## Resolution

The loader reads lightweight metadata, checks Hedron/Python compatibility, resolves required plugin dependencies, detects cycles, and creates a deterministic startup order. Contributions register into a temporary registry builder. Validation failure discards the builder so partially loaded state never becomes active.

Async or sync startup hooks run during application lifespan; shutdown hooks run in reverse order with failure aggregation and cleanup. Plugins receive narrow registration and application-context protocols rather than private global objects.

## Auditing

Capability metadata includes Python execution, browser JavaScript, styles, assets, Explorer panels, compiler helpers, routes, and remote-resource needs. `audit-components` reports these facts and upstream package versions.

## Verification

Test missing packages, incompatible versions, cycles, duplicate contributions, deterministic ordering, lazy imports, startup rollback, reverse shutdown, cancellation, and capability reporting.

