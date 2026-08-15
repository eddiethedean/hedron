# Upgrade fixtures — phase 0.41 browser composition, state, and navigation

**Status:** Planned Stage 0 corpus. Baseline Published `v0.40.0`; target `v0.41.0`.

## Required matrix

- 0.40 pages without graph/transfer declarations behave identically on 0.41 assets.
- 0.41 server + 0.40 module and 0.40 server + 0.41 module fail visibly per element and preserve SSR,
  links, forms, and full-fragment navigation.
- Unknown event/edge/envelope/trace versions fail closed; no implicit downgrade accepts data.
- Eligible draft transfer survives only the declared same-subject route-family swap. Logout,
  subject/authority change, submit, discard, expiry, incompatible schema/ABI, rollback, storage
  denial/quota/corruption, and second consumption prove clearing/rejection.
- Back/forward, history cache, fragment-only URLs, validation errors, missing focus targets, titles,
  scroll restoration, reduced motion, no View Transitions, and no preload retain semantics.
- Upgrade and rollback leave no stale graph registrations, storage entries, listeners, observers,
  timers, transition names, preload requests, or trace buffers.

## Rollback

Pin the coordinated train to `hedron>=0.40.0,<0.41`, remove 0.41-only graph/transfer declarations,
clear the versioned 0.41 session-storage namespace, and verify ordinary form/link/full-fragment
flows. Drafts are disposable; rollback never migrates them into server state or 0.40 storage.

## Evidence artifacts at cut

- before/after/mixed-version HTML and registry fixtures;
- three-engine history/focus/title/scroll recordings and privacy assertions;
- storage-denied/quota/corrupt/logout/identity-change envelopes;
- failure-injection traces containing metadata only; and
- exact 14-issue regression fixtures linked from `REGRESS-041`.
