# RFC-0017: CLI

**Status:** Accepted

## Commands

The CLI provides `new`, `dev`, `build`, `check`, `inspect`, `eject`, `components`, `routes`, `graph`, `preview`, and `audit-components`. Commands operate on the same registry and compilers as the running application.

`check` covers models, legacy HDN inventory, styles, routes, OpenAPI, assets, security,
accessibility, and integration compatibility. It emits human-readable text plus stable JSON and
SARIF. `inspect` explains active component structure, templates, styles, routes, dependencies, and
inferred behavior. Under the D-040/RFC-0031 migration path, HDN `inspect`/`eject` behavior exists for legacy
migration and is not a promise that the language survives.

## Requirements

- No CLI command requires Node.js for official workflows.
- Commands are scriptable, deterministic, and non-interactive by default.
- Errors include stable codes, source locations, remediation, and responsible package.
- Build commands never fetch remote browser assets unless explicitly configured.

## Acceptance criteria

- CLI output and exit-code contracts are documented and snapshot tested.
- `check` can fail CI by severity.
- The CLI imports only requested optional integrations and reports missing extras precisely.
