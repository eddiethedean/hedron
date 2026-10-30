# Test your UI

Hedron components are deterministic Python objects, so most interface tests need neither
an ASGI server nor a browser. Add progressively broader tests only where HTTP or browser
behavior is part of the contract.

## Render a component

```python
from hedron import Card, Text
from hedron.testing import assert_renders, render_html


def test_welcome_card() -> None:
    card = Card(Text("Welcome, Ada"))

    assert_renders(card, contains="Welcome, Ada")
    assert "<script" not in render_html(card)
```

`render_html` is useful for focused assertions. `assert_renders` and
`assert_render_result` retain render metadata when assets or diagnostics are the behavior
under test.

## Exercise an HTMX fragment

```python
from hedron.testing import fragment_client


def test_home_fragment(app) -> None:
    with fragment_client(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "<html" not in response.text
```

The fragment client supplies the relevant HTMX request context so the test verifies the
fragment contract rather than an ordinary full-page response.

## Portable adapter harness (0.11)

For PAGE/FRAGMENT/POST+CSRF scenarios shared across FastAPI, Flask, and Django, use
`hedron.testing.adapters` (`fastapi_fixture` / `flask_fixture` / `django_fixture` plus
`assert_page_document` / `assert_fragment_body` / `assert_htmx_trigger`). See
[TESTING.md](../api/TESTING.md).

## AppScenario and HTMX asserts (0.15)

Use `AppScenario` from `hedron.testing` for multi-step application flows, and the HTMX
assert helpers (**#22–#26**) for InteractionResult / fragment / undeclared-target checks
(for example `assert_undeclared_target_rejected` requires **403** plus a region-specific
signal). See [TESTING.md](../api/TESTING.md).

## Override FastAPI dependencies

```python
from hedron.testing import override_dependencies


def test_as_an_admin(app, current_user, fake_admin) -> None:
    with override_dependencies(app, {current_user: lambda: fake_admin}):
        # Make requests while the override is active.
        ...
```

The context manager restores `dependency_overrides` even if an assertion fails, keeping
tests isolated.

## Snapshot intentionally

Use `normalize_snapshot_html` only for documented nondeterminism. Prefer semantic
assertions for text, attributes, diagnostics, and assets; broad snapshots can obscure a
small but important accessibility or security regression.

Browser-level accessibility checks are available from `hedron.testing.browser` after
installing `hedron[browser]`. Keep those for interaction and platform behavior that a
render test cannot prove.

## Real browser scenarios (1.3 beta)

Use `hedron.testing.pytest_plugin` when a test needs a real browser, HTMX requests, and an
isolated ASGI app. The 1.3 API is still an unpublished candidate; from the Hedron repository,
prepare the locked development environment and browser once:

```bash
uv sync --locked --all-groups --python 3.12
uv run playwright install chromium
```

Load the plugin explicitly in the test directory's `conftest.py`:

```python
pytest_plugins = ["hedron.testing.pytest_plugin"]
```

For a new FastAPI app, hedron new myapp --with-ui-tests opts into a minimal-template example:
it adds a managed-host factory, an explicit plugin conftest.py, a native Playwright smoke test,
and a separate test dependency group. The default scaffold is unchanged, and this option currently
supports only the minimal FastAPI template. The package release has not occurred yet, so these
generated-project setup commands describe post-release use; candidate source tests use the locked
workspace environment above.

    hedron new myapp --with-ui-tests
    cd myapp
    uv sync --group test
    uv run playwright install chromium
    HEDRON_BROWSER=1 uv run pytest -q --browser chromium -n 0

Run the packaged synthetic example with an installed browser:

```bash
HEDRON_BROWSER=1 uv run pytest -q examples/ui-testing -n 0 --browser chromium
```

Use `--browser firefox` or `--browser webkit` to select the other Playwright engines. The
repository browser CI runs `tests/browser` and both UI-testing examples. On failure, structured
manifests go to `.pytest_cache/hedron-ui`; set `--hedron-ui-artifacts DIR` to choose a dedicated
private directory.

Then keep native Playwright in control of locators, actions, and assertions. Hedron supplies a
managed ASGI process, a function-scoped context from pytest-playwright, semantic marks/regions,
scoped HTTP expectations, and checkpoint-based HTMX settling:

```python
from playwright.sync_api import expect


def test_profile(hedron_ui) -> None:
    with hedron_ui.from_app(
        "myapp.testing:create_app",
        config={"root_path": "/account"},
        root_path="/account",
    ) as ui:
        ui.page.goto(ui.url)
        name = ui.page.get_by_label("Display Name")
        cursor = ui.checkpoint()
        with ui.expect_http(
            method="POST", path="/account/profile", status=422, since=cursor
        ):
            name.fill("Al")
            name.press("Enter")
            ui.settle(since=cursor, target="hedron-errors")

        expect(ui.page.locator("#hedron-validation-errors")).to_be_visible()
        expect(name).to_be_focused()
```

The example app and full validation/save test live in `examples/ui-testing`. An external server can be selected with
`ui.from_url("http://127.0.0.1:8000")`; the caller owns it, and lifespan/server-exception facts
are reported as unavailable. Both modes reject non-loopback hosts and block unlisted browser
origins. Redirect responses are denied because Playwright cannot safely re-check each redirect hop.
Server-sent event requests are rejected, and routed responses are buffered; do not use this profile
for long-lived or streaming responses.

Specialist packages can declare a versioned `UITestingContribution` and explicitly load it with
`@pytest.mark.hedron_ui_contribution("module:CONTRIBUTION")`. The sample-kit implementation in
`examples/ui-testing-satellite` demonstrates capability,
fixture-resource, and version checks without taking ownership of the browser or host.

Unexpected browser errors, failed required assets, unexpected HTTP errors, blocked requests,
server exceptions from a managed app, and teardown problems fail the scenario. An exact
`expect_http` rule accepts only its method, path, status, count, and checkpoint. It does not
disable page-error or unrelated console checks. `ui.mark("save")` selects a real
`data-testid="save"` element, and `ui.region("results")` re-queries a real element by id after
swaps.

`ui.settle` matches trusted user-triggered HTMX requests by default, so a same-target background
poll does not satisfy a user action. If multiple user actions target the same region after one
checkpoint, settle raises `AmbiguousSettleError`; set a stable
`data-hedron-action-generation="N"` on each initiating element and pass `generation=N` to select
one. Use `user_action=False` for explicitly programmatic HTMX events, or `user_action=None` when
the test intentionally accepts any trigger.

The default failure artifact is a bounded structured manifest under
`.pytest_cache/hedron-ui`; it omits page text, request URLs, form values, headers, cookies,
console messages, and target identifiers. Native trace/screenshot capture is a separate
synthetic-data-only profile and labels retained output unredacted. Its resource ceilings are
still part of the 1.3 release gate, so do not use it for real or confidential data.
On Linux, opted-in native capture must run through Hedron's budget wrapper with pytest-playwright
output inside a private 128 MiB tmpfs, a monitored 64 MiB total-tree threshold, 25 ms process-group
checks, and a 64 MiB per-file limit. Crossing the tree threshold terminates and fails the test
process; direct `pytest --tracing` use is rejected.
The release CI browser lane configures this wrapper and tmpfs automatically.
From a source checkout, the equivalent command is:

```bash
export HEDRON_BROWSER=1
python scripts/run_ui_budgeted.py \
  --output-json test-results/ui-resources.json \
  --tempfs-limit-mib 128 --tempfs-usage-limit-mib 64 \
  --sample-interval-ms 25 --max-file-mib 64 -- \
  python -m pytest -p hedron.testing.pytest_plugin -q \
  --browser chromium --tracing=retain-on-failure \
  --output "$TMPDIR/playwright-output" path/to/test_ui.py
```

This API is beta. It supports synchronous pytest with pytest-playwright; asyncpytest, WSGI host
launchers, remote services, and visual snapshot management are outside this cut. The lower-cost
render helpers and `AppScenario` remain the default for tests that do not need a real browser.

See the [testing API contract](../api/TESTING.md) for the complete helper inventory.
