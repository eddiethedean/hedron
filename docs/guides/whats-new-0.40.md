!!! note "Current train is 0.46"

    Pin `hedron>=0.46.0,<0.47` for new apps. See [What's new in 0.41](whats-new-0.41.md).

# What's new in Hedron 0.40

**Published** as `v0.40.0` on 2026-08-14. Historical pin: `hedron>=0.40.0,<0.41`. Charts remain on the
Published 0.2 line: `hedron-charts>=0.2.0,<0.3`.

Phase **0.40** enables third-party authors to build portable Hedron elements without private
APIs and aligns plugins, HDJ, Explorer, themes, and conformance on shared element metadata
([RFC-0060](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) / D-068).

## Highlights

- Public **author kit** and `hedron new element` scaffold with an external consumer plugin proof
- `PluginContext.register_element_definition` / `register_asset` (first-party false by default)
- Extended **`ElementDefinitionMeta`** (`parts` / `slots` / `tokens`) with HDJ / Explorer /
  theme / conformance parity
- **`ReactMigrationMatrix`** dispositions (`native` / `hedron` / `element` / `react-island` /
  `not-a-fit`); Experimental island bridge as docs/reference only
- Optional in-repo **`@hedron/elements`** modules/TS types; Python no-Node path unchanged
- Remediations **#162**, **#203**, **#204**, **#219**, **#220**, and **#222**

## Honesty

- Human screen-reader / compensated AT (`SR-021`) remains **Planned** — not Supported.
- React-island remains **Experimental** docs/reference only; not shipped inside
  `hedron-elements`.
- Live SSE / WebSocket / streaming remain **experimental**; polling is the Supported production
  story.

## See also

- [Upgrade to 0.41](upgrade.md)
- [Plugin authoring](plugin-authoring.md)
- [HDJ authoring](hdj-authoring.md)
- [hedron-elements](../packages/hedron-elements.md)
- [Release notes](release-notes.md)
- [RELEASE_0_40](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_40.md)
- [React island reference](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/react-island-reference/README.md)
