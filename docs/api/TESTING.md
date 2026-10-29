---
status: shipped
---

# Testing API


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Available on 1.0 (introduced in `0.4`) · import from `hedron.testing`

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

Real browser page scenarios are a separate beta surface in
`hedron.testing.browser_scenario`, activated by `hedron.testing.pytest_plugin` and installed with
`hedron[testing]`. They preserve native Playwright `Page`/`Locator`/`expect` usage and use the
supported pytest-playwright context fixture. See the [browser scenario guide](../guides/testing.md#real-browser-scenarios-13-beta).

| Beta helper | Signature (summary) | Returns | Purpose |
|---|---|---|---|
| `BrowserScenarioFactory.from_app` | `(factory, *, config=None, root_path=None, allowed_origins=(), synthetic=False)` | context manager | Spawn an importable ASGI factory with bounded JSON config |
| `BrowserScenarioFactory.from_url` | `(base_url, *, allowed_origins=(), synthetic=False)` | context manager | Observe a caller-owned literal-loopback HTTP(S) service |
| `BrowserScenario.page` / `.context` | properties | native Playwright objects | Use Playwright directly for locators, actions, and assertions |
| `BrowserScenario.checkpoint` / `.settle` | `(checkpoint, target, timeout=10, generation=None, user_action=True)` | `Checkpoint` / `SettleResult` | Match a trusted user-triggered HTMX request by default; filter by generation or set `user_action=None` for any trigger; ambiguous matches raise `AmbiguousSettleError` |
| `BrowserScenario.expect_http` | `(method, path, status, count=1, since=None)` | context manager | Allow an exact expected HTTP response without suppressing unrelated errors |
| `BrowserScenario.mark` / `.region` | `(name)` | native `Locator` | Resolve a test id or stable region id again after DOM swaps |
| `UITestingContribution` | `(package_id, package_version, hedron_version_range, capabilities, fixture_resources=(), schema_version=1)` | immutable metadata | Declare bounded capabilities and required fixtures for an explicitly loaded package contribution |

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
