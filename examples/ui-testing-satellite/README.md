# Sample-kit UI-testing contribution

This opt-in example proves how a specialist package can contribute core-only, versioned test
metadata, a synthetic FastAPI factory, and a fixture resource without taking ownership of the
browser or test host. The factory uses `hedron-core` and FastAPI, and the sample-kit distribution
remains independently importable without the flagship `hedron` package.

This example uses the unreleased 1.3 candidate API. From the Hedron repository root, install the
locked development environment and a Playwright browser:

```bash
uv sync --locked --all-groups --python 3.12
uv run playwright install chromium
```

The repository root `conftest.py` explicitly loads `hedron.testing.pytest_plugin` and
`hedron_sample_kit.pytest_plugin`. For an example project outside the Hedron repository, activate
both plugins with `-p` after installing the candidate from a Hedron source checkout. The test
explicitly names the contribution with
`@pytest.mark.hedron_ui_contribution("hedron_sample_kit.ui_testing:CONTRIBUTION")`; collection
validates the JSON-shaped schema, package version, Hedron compatibility range, capability
uniqueness, and declared fixture resources before creating any browser context.

Run it from the repository with:

```bash
HEDRON_BROWSER=1 uv run pytest -q -n 0 --browser chromium
```
