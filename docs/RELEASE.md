# Cutting a Hedron release

This is the living maintainer runbook for the `0.37.x` train. Historical cut records
live under `docs/archive/`. The last published release is `v0.37.0`; the next planned
patch is `v0.37.1`.

Hedron uses coordinated package versions for the core train. A Git tag includes `v`;
Python metadata does not. Never move or replace a published tag.

## Preconditions

1. The release commit is on green `main`, with no unexplained waived checks.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, CI gate version, security support window, and release notes agree.
3. `docs/acceptance/release-gate-0.37.toml` remains Verified and the 0.37 package verifier
   passes.
4. The repository and PyPI trusted-publishing configuration are controlled by active
   maintainers; the release uses the GitHub Actions workflow.
5. The tag does not already exist locally or on the remote.

## Local release candidate

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.37.0
bash scripts/ci_checks.sh browser --python 3.12
uv run python scripts/check_release_gate.py 0.37.0
uv run python scripts/verify_pkg_37.py
```

## Tag and publish

After reviewing the complete version/changelog diff (tip honesty already treats
`v0.37.0` as published in adopter docs/`docs/release.toml`):

```bash
git fetch --tags origin
git rev-parse v0.37.0 >/dev/null 2>&1 && { echo "tag exists; stop"; exit 1; }
git tag -a v0.37.0 -m "Hedron 0.37.0"
git push origin v0.37.0
```

## Template: next patch (`0.37.1`)

Bump the coordinated train to `0.37.1`, set `docs/release.toml` accordingly, then:

```bash
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.37.1
uv run python scripts/check_release_gate.py 0.37.1
git tag -a v0.37.1 -m "Hedron 0.37.1"
git push origin v0.37.1
```
