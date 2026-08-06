---
status: shipped
---

# Testing API


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Shipped in `0.4` · import from `hedron.testing`

| Helper | Signature (summary) | Returns | Purpose |
|---|---|---|---|
| `render_html` | `(node, *, mode=FRAGMENT)` | `str` | Render HTML string |
| `assert_renders` | `(node, *, contains, mode=FRAGMENT)` | `str` | Assert substring; return HTML |
| `assert_render_result` | `(result, *, contains)` | `None` | Assert against `RenderResult` |
| `fragment_client` | `(app)` | context manager | `TestClient` with HTMX fragment headers |
| `override_dependencies` | `(app, overrides)` | context manager | Temporary FastAPI `dependency_overrides` |
| `named_example` / `iter_named_examples` | registry helpers | examples | Named component examples |
| `normalize_snapshot_html` | `(html)` | `str` | Normalize fingerprinted asset hashes only |

```python
from hedron.testing import assert_renders, fragment_client, render_html
from hedron_core import Text

html = render_html(Text("hello"))
assert_renders(Text("world"), contains="world")

with fragment_client(app) as client:
    response = client.get("/status")
    assert response.status_code == 200
```

Optional browser extras live under `hedron.testing.browser` (`playwright()` context
manager; `axe_scan`) and require `hedron[browser]`.

## Portable adapter harness (0.11)

Import from `hedron.testing.adapters` for PAGE/FRAGMENT/POST scenarios shared across hosts:

| Helper | Role |
|---|---|
| `fastapi_fixture` / `flask_fixture` / `django_fixture` | Wrap host test clients |
| `assert_page_document` | Full HTML document (`<html>…</html>`) |
| `assert_fragment_body` | Fragment body without document chrome |
| `assert_htmx_trigger` | `HX-Trigger` presence |

Shared scenarios cover CSRF-seeded GET cookies, POST deny/allow with host CSRF, and
`HX-Trigger` on interaction responses. Cookies must be set **before** the request (Flask
fixture fixed in 0.11); responses expose a portable `cookies` map. Host-native clients
remain available for adapter-specific assertions.

## AppScenario and HTMX asserts (0.15)

`AppScenario` (`hedron.testing`) wraps get/post fixtures for application-flow tests.
HTMX helpers include asserts **#22–#26** such as `assert_undeclared_target_rejected`
(403 + region signal), fragment/OOB body checks, and related InteractionResult helpers.
See [Testing guide](../guides/testing.md).

## Errors

| Condition | Behavior |
|---|---|
| `assert_renders` miss | AssertionError with rendered HTML context |
| Browser extras missing | Import/install error pointing at `hedron[browser]` |

## See also

[Testing guide](../guides/testing.md)
