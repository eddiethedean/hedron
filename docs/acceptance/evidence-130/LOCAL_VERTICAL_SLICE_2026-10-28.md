# Phase 1.3 local vertical-slice and contribution probe

**State:** Observed locally; partial gate evidence only, not a release attestation<br>
**Date:** 2026-10-28<br>
**Source commit:** `fced98f466478dd9e1c31a8e13f3b1bae7ce4fc3` plus the dirty implementation worktree<br>
**Host:** macOS 26.6.2, arm64; CPython 3.12.13

## Runtime versions

| Component | Version |
|---|---|
| pytest | 9.1.1 |
| pytest-playwright | 0.10.0 |
| Playwright Python | 1.62.0 |
| Uvicorn | 0.52.1 |
| hedron-sample-kit | 0.2.6 |
| Chromium | 151.0.7922.34 |
| Firefox | 153.0 |
| WebKit | 26.5 |

## Command and result

The same command was run once per engine:

```bash
for engine in chromium firefox webkit; do
  HEDRON_BROWSER=1 .venv/bin/python -m pytest -q \
  tests/unit/test_ui_testing_contributions.py \
  tests/unit/test_ui_testing_host.py \
  tests/unit/test_ui_testing_artifacts.py \
  examples/ui-testing examples/ui-testing-satellite \
  -n 0 --browser "$engine"
done
```

| Engine | Result |
|---|---|
| Chromium | 31 passed in 7.46s |
| Firefox | 31 passed in 7.32s |
| WebKit | 31 passed in 6.76s |

The run covered spawned ASGI startup and lifespan, mount/root-path and static asset requests,
startup failure, the profile form's 422 and 200 HTMX flow, caller-owned external loopback mode,
JavaScript-disabled native form submission, package import isolation, private artifact-path
behavior, and the explicitly loaded sample-kit contribution with schema/version/fixture checks.
WebKit initially exposed an existing stale SHA-256 integrity value for
`hedron-alpine.mjs`; correcting the recorded digest made the full slice pass on all three engines.

Static checks on the changed UI-testing modules passed Ruff and BasedPyright with zero errors
(BasedPyright reports two standard-library source-resolution warnings for `json`).
`UV_CACHE_DIR=/private/tmp/hedron-ui-uv-cache uv lock --check --offline` passed.

The updated repository browser CI command also ran:

```bash
HEDRON_BROWSER=1 HEDRON_BROWSER_ENGINE=chromium \
  bash scripts/ci_checks.sh browser --python 3.12
```

It ended with `110 passed, 77 skipped, 26 deselected, 1 warning, 22 errors`. The errors came from
the existing `tests/browser/test_docs_sim_pages.py` fixture trying to bind its local HTTP server;
a single-test retry reproduced `PermissionError` on `127.0.0.1` in this restricted sandbox. The
strict MkDocs build itself succeeds (`.venv/bin/python -m mkdocs build --strict`, exit 0); its
MkDocs 2.0 message is an informational warning, not the fixture failure. The new UI examples
passed in the repository browser run. That run also flagged example-directory Markdown links;
those links have since been changed to inline paths.

## Limits

This is one local macOS/Python 3.12 probe with the current locked dependency versions. It does not
verify the Linux CI runtime, CPython 3.11/3.13/3.14, minimum dependency bounds, xdist/rerun
isolation, the full existing browser behavior corpus, confidential canaries, native-capture disk
limits, accessibility tooling evidence, measured performance budgets, fleet contribution conflict
behavior, package-disposition review, or release predecessor/approval. The source worktree was
dirty, and this note is not an immutable release artifact. No `*-130` gate is marked Verified.
