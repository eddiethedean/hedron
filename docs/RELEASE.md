# Cutting a Hedron release

This runbook covers the coordinated **1.0.0** release candidate on branch `v1.0`.
The latest public PyPI release is still `v0.66.2`; do not describe the candidate as
published until the tag, wheels, and registry evidence are verified. Historical cut
records live under `docs/archive/`.

Hedron is a Python monorepo with independently publishable distributions. The core
Hedron packages and `hedron-posit` share the `1.0.0` train. `fastapi-workbench` is an
independent package and is currently `1.0.1`. The removed `hedron-workbench` package is
not part of the release inventory.

A Git tag includes the `v` prefix; Python metadata does not. Never move or replace a
published tag except for an explicitly authorized corrective retag after a failed
publication.

## Preconditions

1. The release commit is on the `v1.0` branch with a clean working tree and green CI.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, security support window, and release notes agree.
3. Run `uv run python scripts/check_100.py --check-plan`; all 1.0-owned rows must be
   planned or verified with no unexpected deferred work.
4. Verify the release gate with `uv run python scripts/check_100.py --gate ENTRY-100
   --verify` and retain the generated evidence under `docs/acceptance/`.
5. Confirm the package inventory contains `hedron`, its maintained satellites,
   `hedron-posit`, and `fastapi-workbench`; it must not contain `hedron-workbench`.
6. Confirm the tag does not already exist locally or on the remote. A failed
   publication requires an authorized corrective action after metadata and workflow
   fixes.
7. Before publishing release notes, verify uploaded wheels, trusted publishing,
   install smoke tests, and `registry_status = "uploaded"` in `docs/release.toml`.

## Local release candidate

```bash
uv sync --locked --all-groups --python 3.12
uv run pytest -q
uv run ruff check packages tests examples --output-format concise
uv run python scripts/check_100.py --check-plan
uv run python scripts/check_100.py --gate ENTRY-100 --verify
uv lock --check
git diff --check
```

Build wheels and test them in a clean environment before tagging:

```bash
uv build --all-packages
uv run python scripts/check_published_quickstart.py 1.0.0 --dist-dir dist --attempts 1
```

The quick-start check is a pre-publication artifact check until the 1.0.0 wheels are
available from PyPI. After upload, rerun it against the registry and record the result.

## Tag and publish

Tagging and uploading require explicit maintainer authorization through the GitHub
Release / PyPI trusted-publishing workflow. After publication, update
`docs/release.toml`, `docs/guides/current-release.md`, and the package changelogs in
that order, then rerun the documentation and release checks.
