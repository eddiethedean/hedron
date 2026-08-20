# Notebook preview (0.54)

`hedron-notebook` remains **localhost-only / tooling-grade**. It is not a
Supported production server.

## Display handles

`DisplayHandle` operations: `update`, `snapshot`, `open_in_browser`, `close`.
Static fallbacks: `as_html()`, `as_text()`, image placeholder. Multi-view sessions
use `NotebookSession` with deterministic cleanup.

## Security and topology

- Non-loopback hosts are rejected by default (`HED-NOTEBOOK-TOPOLOGY`).
- Token failures use `HED-NOTEBOOK-TOKEN`.
- Snapshots redact tokens and local paths.
- Opt-in real-server handoff prints an explicit security/topology disposition and
  never silently binds a public interface.

## Frontend matrix

Supported evidence targets JupyterLab / classic-compatible frontends where
available, IPython current/previous lines, VS Code notebook disposition, and
headless saved-output rendering across Python 3.11–3.14.
