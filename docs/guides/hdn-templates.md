# HDN templates (`.hdx`)

Hedron Discovery Notation (HDN) lets component folders ship markup templates next to
Python. On the 0.8 train the **preferred filename is `template.hdx`** (JSX-familiar).
Legacy `template.hdn` remains a discoverable compatibility fallback.

## Discovery

When both `template.hdx` and `template.hdn` exist in a component folder, discovery uses
`.hdx` and may log a warning. Prefer renaming to `.hdx` when convenient.

## Authoring

1. Create a component folder under a configured `component_roots` path.
2. Add `template.hdx` with HDN markup and a Python module that registers the component.
3. Run `hedron check` / tests to validate discovery.

Eject / scaffold tooling writes `.hdx` for new overrides (`hedron eject`).

## Relation to Python components

HDN is optional. Many apps use pure Python `html.*` / built-ins without templates.
Templates are for authoring convenience and Explorer-friendly structure—not a second
runtime.

## See also

- [Component API](../api/COMPONENT.md)
- [Upgrade notes](upgrade.md) (0.7 → 0.8 `.hdx` preference)
- [Glossary](../GLOSSARY.md)
