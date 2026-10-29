# Hedron browser testing example

This example shows a real browser test against a synthetic profile form. The app factory runs in
the isolated child process owned by `hedron.testing.pytest_plugin`, while the test uses ordinary
Playwright `Page`, `Locator`, and `expect` APIs.

This example uses the unreleased 1.3 candidate API. From the Hedron repository root, install the
locked development environment and a Playwright browser:

```bash
uv sync --locked --all-groups --python 3.12
uv run playwright install chromium
```

The repository root `conftest.py` explicitly loads Hedron's pytest plugin for this workspace. For
an example project outside the Hedron repository, activate it with `-p` after installing the
candidate from a Hedron source checkout:

```bash
HEDRON_BROWSER=1 uv run pytest -q -n 0 --browser chromium
```

Use `--browser firefox` or `--browser webkit` for the other engines. The sample covers a 422
validation response, focus and live-region feedback, a successful HTMX submission, an externally
owned loopback server, and a JavaScript-disabled native form submission. Its data is synthetic.

The [browser-testing guide](../../docs/guides/testing.md#real-browser-scenarios-13-beta) describes
the helper contract, structured failure artifacts, and current limits.
