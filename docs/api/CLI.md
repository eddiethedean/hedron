# CLI API

**Status:** Accepted for phase 0.4

Entry point: `hedron` → `hedron.cli:main`.

## Commands

`new`, `dev`, `build`, `check`, `inspect`, `eject`, `components`, `routes`, `graph`, `preview`, `audit-components`.

`check --format text|json|sarif` emits diagnostics with stable codes. Exit code is non-zero when diagnostics meet or exceed the severity threshold (`error` by default).

Commands are non-interactive by default and do not require Node.js.
