# Cutting a Hedron release

This is the maintainer runbook for the published `0.64.x` train. Historical cut records live
under `docs/archive/`. The current repository and latest public PyPI release are `v0.64.0`.

Hedron uses coordinated package versions for the core train. A Git tag includes `v`;
Python metadata does not. Never move or replace a published tag except for an explicitly
authorized corrective retag after a failed publication.

## Preconditions

1. The release commit is on green `main`, with no unexplained waived checks.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, CI gate version, security support window, and release notes agree.
3. `docs/acceptance/release-gate-0.64.toml` must match the bounded 0.64.0 release packet and
   `scripts/check_064.py --gate CONTRACT-064 --verify` must pass for the release. Historical packets
   `scripts/verify_pkg_58.py`,
   `scripts/verify_pkg_57.py`, and `scripts/verify_pkg_56.py` remain green.
4. The repository and PyPI trusted-publishing configuration are controlled by active
   maintainers; the release uses the GitHub Actions workflow.
5. The tag for a new release does not already exist locally or on the remote. A failed
   publication may require an explicitly authorized corrective retag after the release
   metadata and workflow have been fixed.
6. After a successful upload, verify the PyPI artifact, trusted-publishing record, install
   smoke, and `registry_status = "uploaded"` before publishing release notes.
7. Ordinary quality CI and the release workflow must pass the built-wheel quick-start gate
   before a tag or first PyPI upload. The post-upload quick-start remains an independent
   registry verification.

## Local release candidate

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.64.0
bash scripts/ci_checks.sh browser --python 3.12
uv run python scripts/check_release_gate.py 0.64.0
uv run python scripts/check_published_quickstart.py 0.64.0 --dist-dir dist --attempts 1
uv run python scripts/check_063.py --gate CONTRACT-063 --verify
uv run python scripts/verify_pkg_60.py
uv run python scripts/verify_pkg_59.py
uv run python scripts/verify_pkg_58.py
uv run python scripts/verify_pkg_57.py
uv run python scripts/verify_pkg_56.py
```

## Tag and publish

For a future cut, do not tag or upload until maintainers explicitly authorize the GitHub
Release / PyPI workflow.
