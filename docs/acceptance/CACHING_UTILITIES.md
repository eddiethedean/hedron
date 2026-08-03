# Caching and utility components acceptance

## Caching

- [x] `cache_data` and `cache_component` produce deterministic scoped keys and support sync/async functions.
- [x] User, tenant, locale, permission, and representation-sensitive values cannot cross cache scopes.
- [x] Secrets never appear in keys, logs, traces, or Explorer.
- [x] Single-flight behavior prevents duplicate loads and handles waiter cancellation safely.
- [x] Invalidation, failures, backend outages, and multi-worker limitations are documented and tested.

## Utility components

- [x] Metric, upload, download, code, JSON, progress, status, toast, expander, tabs, sidebar, and grid have documented Python contracts and examples.
- [x] Upload limits, accepted types, filenames, storage boundary, authorization, CSRF, and malformed content are tested.
- [x] Downloads validate filenames, content types, authorization, caching, and cancellation.
- [x] Code and JSON content remain escaped and bounded with secret redaction.
- [x] Interactive utilities meet keyboard, focus, announcement, reduced-motion, and server-fallback requirements.

## Exit

The reference application demonstrates at least one cache, upload/download flow, metric, status/progress interaction, and disclosure/navigation component under strict security and accessibility policies.
