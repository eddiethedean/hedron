# Caching and utility components acceptance

## Caching

- [ ] `cache_data` and `cache_component` produce deterministic scoped keys and support sync/async functions.
- [ ] User, tenant, locale, permission, and representation-sensitive values cannot cross cache scopes.
- [ ] Secrets never appear in keys, logs, traces, or Explorer.
- [ ] Single-flight behavior prevents duplicate loads and handles waiter cancellation safely.
- [ ] Invalidation, failures, backend outages, and multi-worker limitations are documented and tested.

## Utility components

- [ ] Metric, upload, download, code, JSON, progress, status, toast, expander, tabs, sidebar, and grid have documented Python contracts and examples.
- [ ] Upload limits, accepted types, filenames, storage boundary, authorization, CSRF, and malformed content are tested.
- [ ] Downloads validate filenames, content types, authorization, caching, and cancellation.
- [ ] Code and JSON content remain escaped and bounded with secret redaction.
- [ ] Interactive utilities meet keyboard, focus, announcement, reduced-motion, and server-fallback requirements.

## Exit

The reference application demonstrates at least one cache, upload/download flow, metric, status/progress interaction, and disclosure/navigation component under strict security and accessibility policies.

