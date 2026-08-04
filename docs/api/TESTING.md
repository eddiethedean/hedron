---
status: shipped
---

# Testing API


!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted · **Shipped in 0.4**

Import helpers from `hedron.testing`:

| Helper | Signature (summary) | Purpose |
|---|---|---|
| `render_html` | `(node, *, mode=FRAGMENT) -> str` | Render HTML string |
| `assert_renders` | `(node, *, contains, mode=FRAGMENT) -> str` | Assert substring and return HTML |
| `assert_render_result` | `(result, *, contains) -> None` | Assert against `RenderResult` |
| `fragment_client` | `(app) -> context manager` | TestClient with HTMX fragment headers |
| `override_dependencies` | `(app, overrides) -> context manager` | Temporary FastAPI `dependency_overrides` |
| `named_example` / `iter_named_examples` | registry helpers | Named component examples |
| `normalize_snapshot_html` | `(html) -> str` | Normalize fingerprinted asset hashes only |

Optional browser extras live under `hedron.testing.browser` (`playwright()` context
manager; `axe_scan`) and require `hedron[browser]`.
