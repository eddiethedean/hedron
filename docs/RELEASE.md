# Cutting a Hedron release

This is the maintainer runbook for the `0.61.x` train. Historical cut records live under
`docs/archive/`. The current repository release is `v0.61.0`, published on PyPI.

Hedron uses coordinated package versions for the core train. A Git tag includes `v`;
Python metadata does not. Never move or replace a published tag except for an explicitly
authorized corrective retag after a failed publication.

## Preconditions

1. The release commit is on green `main`, with no unexplained waived checks.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, CI gate version, security support window, and release notes agree.
3. `docs/acceptance/release-gate-0.61.toml` is Verified with zero Deferred gates and
   `scripts/verify_pkg_61.py` passes for the candidate. Historical packets `scripts/verify_pkg_60.py`,
   `scripts/verify_pkg_58.py`,
   `scripts/verify_pkg_57.py`, and `scripts/verify_pkg_56.py` remain green.
4. The repository and PyPI trusted-publishing configuration are controlled by active
   maintainers; the release uses the GitHub Actions workflow.
5. The tag for a new release does not already exist locally or on the remote. A failed
   publication may require an explicitly authorized corrective retag after the release
   metadata and workflow have been fixed.
6. After a successful upload, verify the PyPI artifact, trusted-publishing record, install
   smoke, and `registry_status = "uploaded"` before publishing release notes.

## Local release candidate

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.61.0
bash scripts/ci_checks.sh browser --python 3.12
uv run python scripts/check_release_gate.py 0.61.0
uv run python scripts/verify_pkg_61.py
uv run python scripts/verify_pkg_60.py
uv run python scripts/verify_pkg_59.py
uv run python scripts/verify_pkg_58.py
uv run python scripts/verify_pkg_57.py
uv run python scripts/verify_pkg_56.py
```

## Tag and publish

For a future cut, do not tag or upload until maintainers explicitly authorize the GitHub
Release / PyPI workflow.
