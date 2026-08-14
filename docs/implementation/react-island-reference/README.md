# Experimental React-island reference (MIGRATE-040)

**Status:** Experimental docs/reference only. **Not** shipped inside the `hedron-elements`
Python package runtime. Do not market as Supported.

## Contract

- Single owned root element
- Pinned, non-transitive assets
- Typed props/events
- SSR fallback markup remains visible without the island
- CSP / supply inventory required for any assets
- Deterministic unmount / disposal
- **No HTMX region ownership** — islands must not claim `hx-target` / fragment regions
- Explicit removal ledger when retiring the island

## Files

- `island.mjs` — minimal mount/unmount reference
- `island.d.ts` — TypeScript types only
