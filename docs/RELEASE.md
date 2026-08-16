# Cutting a Hedron release

This is the living maintainer runbook for the `0.44.x` train. Historical cut records
live under `docs/archive/`. The last published release is `v0.44.0`; the next planned
phase is `v0.45.0`.

Hedron uses coordinated package versions for the core train. A Git tag includes `v`;
Python metadata does not. Never move or replace a published tag.

## Preconditions

1. The release commit is on green `main`, with no unexplained waived checks.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, CI gate version, security support window, and release notes agree.
3. `docs/acceptance/release-gate-0.43.toml` remains Verified and `scripts/verify_pkg_43.py`
   still passes as a historical packet. The living packet is `scripts/verify_pkg_44.py`
   (omit `--allow-planned`).
4. The repository and PyPI trusted-publishing configuration are controlled by active
   maintainers; the release uses the GitHub Actions workflow.
5. The tag does not already exist locally or on the remote.

## Local release candidate

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.44.0
bash scripts/ci_checks.sh browser --python 3.12
uv run python scripts/check_release_gate.py 0.44.0
uv run python scripts/verify_pkg_44.py
```

## Tag and publish

After reviewing the complete version/changelog diff (tip honesty already treats
`v0.44.0` as published in adopter docs/`docs/release.toml`):

```bash
git fetch --tags origin
git rev-parse v0.44.0 >/dev/null 2>&1 && { echo "tag exists; stop"; exit 1; }
git tag -a v0.44.0 -m "Hedron 0.44.0"
git push origin v0.44.0
```

Pushing `v0.44.0` runs `.github/workflows/release.yml`, which re-runs CI, publishes
coordinated wheels to PyPI, and creates the GitHub Release. Do not retag `v0.41.0`,
`v0.42.0`, or `v0.43.0`.

## Template: next patch (`0.44.1`)

Bump the coordinated train to `0.44.1`, set `docs/release.toml` accordingly, then:

```bash
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.44.1
uv run python scripts/check_release_gate.py 0.44.1
git tag -a v0.44.1 -m "Hedron 0.44.1"
git push origin v0.44.1
```
