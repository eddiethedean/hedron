# Cutting a Hedron release

This is the maintainer runbook for the `0.58.x` train. Historical cut records live under
`docs/archive/`. The in-tree tip is `v0.58.1`; PyPI serves `hedron` `0.58.0`
(`registry_status = deferred` for 0.58.1).

Hedron uses coordinated package versions for the core train. A Git tag includes `v`;
Python metadata does not. Never move or replace a published tag.

## Preconditions

1. The release commit is on green `main`, with no unexplained waived checks.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, CI gate version, security support window, and release notes agree.
3. `docs/acceptance/release-gate-0.53.toml` remains Verified and
   `scripts/verify_pkg_53.py` still passes as a historical packet. The living packet is
   `scripts/verify_pkg_58.py` (omit `--allow-planned`). Predecessor
   `scripts/verify_pkg_57.py` / `scripts/verify_pkg_56.py` also remain green.
4. The repository and PyPI trusted-publishing configuration are controlled by active
   maintainers; the release uses the GitHub Actions workflow.
5. The tag for the release being cut does not already exist locally or on the remote.
6. Keep `registry_status = "deferred"`, `pypi_version = "0.58.0"`, and application
   install pins aligned with the latest public PyPI version until upload.

## Local release candidate

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.58.1
bash scripts/ci_checks.sh browser --python 3.12
uv run python scripts/check_release_gate.py 0.58.1
uv run python scripts/verify_pkg_58.py
uv run python scripts/verify_pkg_57.py
uv run python scripts/verify_pkg_56.py
```

## Tag and publish

For a future cut, do not tag or upload until maintainers explicitly authorize the GitHub
Release / PyPI workflow.
