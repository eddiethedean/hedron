# Authoring loop and chrome API (`v0.54`)

**Status:** Implemented (D-093 / D-094 / RFC-0081), introduced in `v0.54.0` and
available on the verified `1.0.x` repository train. PyPI remains on `v0.66.2`
until the 1.0 publication.

## Shared schema

Import path (locked): `hedron_conformance.authoring_loop`.

Exports include:

- `AUTHORING_LOOP_SCHEMA_VERSION`
- `AuthoringLoopFixture` / `AuthoringLoopDiagnostic`
- failure code constants (`HED-SIM-*`, `HED-NOTEBOOK-*`, `HED-PACKAGE-DOCTOR`)

## Package doctor

CLI: `hedron package doctor` — external package-author validation. Distinct from
`hedron fleet` (installed-application triage) and Explorer package health
(`package_doctor: False`).

## Display handles

Notebook surface: `update`, `snapshot`, `open_in_browser`, `close`, plus
static HTML/image/text fallbacks via `DisplayHandle` / `NotebookSession`.

## Chrome companions

Wave 1: layout (`PageHeader`, `SplitView`, `FormGrid`, `ActionGroup`), AppShell
slots, Theme design-system fields, `SkipLink`, `RequestIndicator`, `ProcessFlow`.
Wave 2: `Icon`, typography roles, palette compiler, theme tooling, shared
appearance vocabulary, theme inheritance, overlays, `StateView`, production
`Table` / `DescriptionList`.

Tracking: [#538](https://github.com/eddiethedean/hedron/issues/538)–[#543](https://github.com/eddiethedean/hedron/issues/543),
[#523](https://github.com/eddiethedean/hedron/issues/523)–[#537](https://github.com/eddiethedean/hedron/issues/537).
