# Phase 0.40 implementation plan: authoring and interoperability

**Status:** Historical implementation plan; the `v0.40.0` cut is published. This file records
the accepted target and work slicing, not the exact current runtime surface. Use
[What’s new in 0.40](../guides/whats-new-0.40.md), [Plugin authoring](../guides/plugin-authoring.md),
and [hedron-elements](../packages/hedron-elements.md) for adopter contracts.

This plan turned [RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) / D-068 into reviewable
work. Tracking [#95](https://github.com/eddiethedean/hedron/issues/95) closed. Catalog:
[REACT_MIGRATION_MATRIX_040.md](REACT_MIGRATION_MATRIX_040.md). Interaction contracts:
[WEB_COMPONENT_INTERACTION_CONTRACTS.md](WEB_COMPONENT_INTERACTION_CONTRACTS.md).

## Outcome

Publish Hedron `v0.40.0` where third parties can author/package/test/inspect elements via public
contracts only, plugins/HDJ/Explorer/themes share element metadata, an optional `@hedron/elements`
modules/TS mirror may exist without requiring Node for Python consumers, and a React migration
matrix ships with an Experimental island bridge as docs/reference only.

Completion requires every row in
[`release-gate-0.40.toml`](../acceptance/release-gate-0.40.toml) Verified — **done**
(React-island remains Experimental per D-068).

## Locked architecture

| Layer | Contract |
|---|---|
| Author kit | Public metadata/events/lifecycle/fallback/assets/a11y/diagnostics; `hedron new element` |
| Plugins | External consumer built without private APIs |
| HDJ / Explorer / theme | Shared element metadata; parts/slots/tokens |
| React matrix | Dispositions native/hedron/element/react-island/not-a-fit |
| Island bridge | Experimental docs/reference; not inside hedron-elements |
| Supply | Optional npm mirror content identity with wheels |

## Work breakdown

### Stage 0 — contract and evidence packet (complete)

- Accept D-068 / RFC-0060 Resolved questions (D-068).
- Add this plan, release packet, gate manifest, inventories, upgrade fixtures, review brief,
  [REACT_MIGRATION_MATRIX_040.md](REACT_MIGRATION_MATRIX_040.md), and scoped [AT-040](../acceptance/human-at/040/PROTOCOL.md).
- Bind tracking [#95](https://github.com/eddiethedean/hedron/issues/95) and remediations
  #162/#203/#204/#219/#220/#222.

### Stages 1–5 — implementation through cut (complete)

See [`RELEASE_0_40.md`](../acceptance/RELEASE_0_40.md) for the Published acceptance packet.
