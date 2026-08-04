# CLI acceptance

## Commands *(phase 0.4)*

- [x] `routes`, `components`, `preview`, `inspect`, `eject`, `build`, and `dev` remain scriptable and non-interactive.
- [x] `new` scaffolds a project with `[tool.hedron]`, a page stub, and a components root.
- [x] `check` covers models/CSS/routes/assets/security/a11y subset and emits text, JSON, and SARIF.
- [x] `check` exits non-zero by severity threshold (errors by default).
- [x] `graph` reports component dependencies and inverse consumers.
- [x] `audit-components` reports capabilities and distribution/version metadata for registry and plugins.
- [x] No official CLI command requires Node.js.

## Exit

CLI output and exit-code contracts are documented and covered by automated tests.
