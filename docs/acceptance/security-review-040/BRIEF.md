# Security review brief — phase 0.40

**Status:** Stage 0 brief only (Planned). Full redacted report + disposition land at cut.

## Scope

- Public author kit and `hedron new element` scaffold (no private API leakage).
- Plugin / HDJ / Explorer metadata trust boundaries.
- Optional `@hedron/elements` modules/TS types and any npm mirror supply identity.
- Experimental React-island reference: CSP, pinned assets, no HTMX-region ownership,
  deterministic unmount, no arbitrary remote modules.

## Out of scope for 0.40

- Whole-platform graduation (0.42).
- Draft transfer / composition (0.41).
- Supported React islands or universal React parity.

## Tracking

[#95](https://github.com/eddiethedean/hedron/issues/95) · D-068 · RFC-0060 Resolved questions (D-068).
