# React migration matrix and authoring catalog (0.40)

**Status:** Historical catalog for Published `v0.40.0` (D-068 / RFC-0060). Adopter entry points:
[What’s new in 0.40](../guides/whats-new-0.40.md) ·
[Experimental island reference](react-island-reference/README.md).

## ReactMigrationMatrix dispositions

| Disposition | Meaning |
|---|---|
| `native` | Use platform HTML / HTMX / Hedron primitives; no React |
| `hedron` | Map to first-party Hedron components/elements |
| `element` | Author a portable Hedron custom element via the public kit |
| `react-island` | Bounded Experimental island (docs/reference); not Supported |
| `not-a-fit` | Explicit non-fit (document why) |

## Honest non-fits (examples)

- Offline-first / client-authoritative auth flows
- Games / continuous canvas / WebGL loops
- Arbitrary npm dependency graphs without a pinned supply inventory
- High-frequency multiplayer collaboration UIs

## Island bridge (Experimental)

- Docs and reference code only; **not** shipped inside `hedron-elements`
- Single owned root; pinned assets; typed props/events; SSR fallback
- CSP / supply inventory; deterministic unmount; no HTMX-region ownership
- Removal ledger; non-transitive; never default

## Author kit surfaces

- Public element metadata, events, lifecycle, fallback, assets, a11y, diagnostics
- Scaffold: `hedron new element`
- External plugin consumer proof (`PLUGIN-040`)

## Theme / HDJ / Explorer

Shared element metadata across HDJ declarations, plugin registration, Explorer inspection, and
theme tokens/parts/slots.
