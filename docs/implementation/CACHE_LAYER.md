# Cache layer implementation

## Architecture

The cache package defines an async-capable backend protocol, deterministic key builder, serialization policy, scope metadata, invalidation tags, and single-flight coordinator. In-memory storage is suitable for development and tests; production applications select an external backend when multi-worker consistency matters.

## Key construction

Keys combine callable/component identity, contract version, normalized declared inputs, and explicit vary dimensions such as tenant, user, roles/permissions, locale, theme, and representation. Dependency objects and request objects are never serialized. Secret-bearing inputs follow security policy and never appear in diagnostics.

## Single flight and cancellation

Concurrent misses for the same scoped key share a load. Waiter cancellation detaches that waiter; ownership and cancellation of the underlying load follow backend policy. Exceptions are not cached unless a typed negative-cache policy is configured.

## Component caching

Only deterministic prepared state or render results with complete asset and header metadata are cacheable. The system rejects user-specific output under a public scope and records the policy decision in Explorer.

## Verification

Test scope isolation, key determinism, secrets, tenant/permission variation, stampede prevention, waiter cancellation, invalidation, backend failure, serialization versions, and multi-worker documentation.

