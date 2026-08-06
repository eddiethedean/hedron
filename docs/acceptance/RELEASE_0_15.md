# Hedron `v0.15` data-app surface completeness acceptance

Phase 0.15 delivers typed data-app controls, media delivery, maps, browser context,
identity/session helpers, connection registry ergonomics, AppScenario / HTMX testing
helpers, and interaction authoring sugar (`region` / `@fragment` / `swap`) without
adopting Streamlit-style whole-script reruns or NiceGUI Vue/outbox mutation. Evidence is
indexed by [`release-gate-0.15.toml`](release-gate-0.15.toml).
**Zero Deferred:** every 0.15-owned gate row must be Verified at cut. Prior-phase live
ops Deferred rows remain owned by `0.10.x` / `0.11.x`.

## Spec packet

- [x] ROADMAP §0.15 scope accepted; Streamlit and NiceGUI cross-checks refreshed.
- [x] Entry gate: 0.14 evidence remains closed; 0.15 gate TOML owns Verified rows only.

## Testing and interaction ergonomics

- [x] HTTP-faithful `AppScenario` application-flow harness. *(`TEST-APP-015`)*
- [x] HTMX InteractionResult / fragment / region / shell asserts (#22–#26).
  *(`HTMX-ASSERT-015`)*
- [x] `region` / `@fragment` / `swap` builders (RFC-0039). *(`ERGONOMICS-015`)*

## Controls, media, and maps

- [x] Typed controls and surface chrome (RFC-0035). *(`CONTROLS-015`)*
- [x] Media Range / download helpers (RFC-0034). *(`MEDIA-015`)*
- [x] Map / GeoJSON with accessible table alternative (RFC-0033). *(`MAP-015`)*

## Browser, identity, and connections

- [x] `BrowserContext` / `BrowserStorage`, Math, IFrame. *(`BROWSER-015`)*
- [x] OIDC / session hardening helpers. *(`IDENTITY-015`)*
- [x] Named connection registry. *(`CONNECTIONS-015`)*

## Exit

- [x] Full regression suite. *(`REGRESS-015`)*

**Exit met** as coordinated `0.15.0` (`v0.15.0`) when every gate row is Verified and the
release tag is cut (implemented pending cut).
