# Cutting a Hedron release

This is the living maintainer runbook for the `0.50.x` train. Historical cut records
live under `docs/archive/`. The published in-tree train is `v0.50.1`; Git tag and PyPI
remain **deferred**. PyPI currently serves
`hedron` `0.48.0` (Git tag `v0.48.0`).

Hedron uses coordinated package versions for the core train. A Git tag includes `v`;
Python metadata does not. Never move or replace a published tag.

## Preconditions

1. The release commit is on green `main`, with no unexplained waived checks.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, CI gate version, security support window, and release notes agree.
3. `docs/acceptance/release-gate-0.49.toml` remains Verified and
   `scripts/verify_pkg_49.py` still passes as a historical packet. The living packet is
   `scripts/verify_pkg_50.py` (omit `--allow-planned`).
4. The repository and PyPI trusted-publishing configuration are controlled by active
   maintainers; the release uses the GitHub Actions workflow.
5. The tag `v0.50.1` does not already exist locally or on the remote.

## Local release candidate

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.50.1
bash scripts/ci_checks.sh browser --python 3.12
uv run python scripts/check_release_gate.py 0.50.1
uv run python scripts/verify_pkg_50.py
uv run python scripts/verify_pkg_49.py
```

## Tag and publish

After reviewing the complete version/changelog diff (tip honesty already treats
`v0.50.1` as published in adopter docs/`docs/release.toml`):

This in-tree **0.50.1** patch does **not** create a Git tag. The commands below are the
future upload template — do not run them now.

```bash
git fetch --tags origin
git rev-parse v0.50.1 >/dev/null 2>&1 && { echo "tag exists; stop"; exit 1; }
git tag -a v0.50.1 -m "Hedron 0.50.1"
git push origin v0.50.1
```

Pushing `v0.50.1` runs `.github/workflows/release.yml`, which re-runs CI, publishes
coordinated wheels to PyPI (skipping satellite versions already on the index), and
creates the GitHub Release. Release CI requires SBOM/evidence-bundle attach on train
tags (SUPPLY-025) via `scripts/build_evidence_bundle.py` and `scripts/generate_sbom.py`.
Do not retag `v0.41.0`, `v0.42.0`, `v0.43.0`, `v0.44.0`, `v0.45.0`, `v0.46.0`,
`v0.47.0`, `v0.48.0`, `v0.49.0`, or `v0.49.1`.

After a successful upload, set `docs/release.toml` `pypi_version = "0.50.1"`,
`pypi_pin_floor` / `pypi_pin_ceiling` to the in-tree pin, and
`registry_status = "uploaded"`, then drop first-run “tag/PyPI deferred” language so
adopter docs match the index.

## Future upload template (`v0.50.1`)

Do **not** run these commands for this in-tree patch. When the deferred upload happens:

```bash
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.50.1
uv run python scripts/check_release_gate.py 0.50.1
# git tag / push remains deferred until upload
```
