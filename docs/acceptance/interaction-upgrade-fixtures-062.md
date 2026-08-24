# Phase 0.62 upgrade fixtures

The 0.62 adapters are additive and opt-in.

- Existing full-page and HTMX navigation remains the fallback when the navigation module is not loaded.
- Existing `OptimisticMutation` payloads remain valid; `validate_phase062()` is required only for the new approved optimistic adapters.
- Unknown mutation outcomes remain explicitly reconcilable and are never treated as success.
- Removing the navigation adapter removes only enhancement behavior; it does not strand durable client-owned state.
- Progressive prefetch and View Transitions are omitted without affecting the Required cut.
