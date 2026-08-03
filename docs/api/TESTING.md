# Testing API

**Status:** Accepted for phase 0.4

Import helpers from `hedron.testing`:

- `render_html` / `assert_renders` / `assert_render_result` for component trees
- `fragment_client` for HTMX-style fragment requests
- `override_dependencies(app, overrides)` wiring FastAPI `dependency_overrides` (restored on exit)
- `named_example` / `iter_named_examples` for registry examples
- `normalize_snapshot_html` for documented nondeterminism only

Optional browser extras live under `hedron.testing.browser` (`playwright()` context manager; `axe_scan`) and require `hedron[browser]`.
