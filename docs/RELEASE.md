# Cutting a Hedron release

This is the maintainer runbook for the published `0.57.x` train. Historical cut records
live under `docs/archive/`. The living in-tree tip is `v0.57.0`; PyPI serves `hedron`
`0.56.0` (`registry_status = deferred` for 0.57.0 until upload).

Hedron uses coordinated package versions for the core train. A Git tag includes `v`;
Python metadata does not. Never move or replace a published tag.

## Preconditions

1. The release commit is on green `main`, with no unexplained waived checks.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, CI gate version, security support window, and release notes agree.
3. `docs/acceptance/release-gate-0.53.toml` remains Verified and
   `scripts/verify_pkg_53.py` still passes as a historical packet. The living packet is
   `scripts/verify_pkg_57.py` (omit `--allow-planned`). Predecessor
   `scripts/verify_pkg_56.py` / `scripts/verify_pkg_55.py` also remain green.
4. The repository and PyPI trusted-publishing configuration are controlled by active
   maintainers; the release uses the GitHub Actions workflow.
5. The tag for the release being cut does not already exist locally or on the remote.
6. While 0.57.0 remains deferred, keep `registry_status = "deferred"`, retain
   `pypi_version = "0.56.0"`, and keep application install pins on the PyPI version.

## Local release candidate

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.57.0
bash scripts/ci_checks.sh browser --python 3.12
uv run python scripts/check_release_gate.py 0.57.0
uv run python scripts/verify_pkg_57.py
uv run python scripts/verify_pkg_56.py
uv run python scripts/verify_pkg_55.py
```

## Tag and publish

For a future train, create and push its annotated version tag only after the gates pass:

```bash
git fetch --tags origin
git rev-parse v0.57.0 >/dev/null 2>&1 && { echo "tag exists; stop"; exit 1; }
git tag -a v0.57.0 -m "Hedron 0.57.0"
git push origin v0.57.0
```

Pushing a future release tag runs `.github/workflows/release.yml`, which re-runs CI, publishes
wheels, and creates the GitHub Release. **Do not tag yet** for the current deferred cut.
