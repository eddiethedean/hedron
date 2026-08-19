# Cutting a Hedron release

This is the living maintainer runbook for the `0.51.x` train. Historical cut records
live under `docs/archive/`. The published in-tree train is `v0.51.0`. PyPI currently
serves `hedron` `0.50.1` (Git tag `v0.50.1`) until the `v0.51.0` upload lands.

Hedron uses coordinated package versions for the core train. A Git tag includes `v`;
Python metadata does not. Never move or replace a published tag.

**Do not tag `v0.51.0` yet.** Keep `registry_status = "deferred"`. Issue
[#507](https://github.com/eddiethedean/hedron/issues/507) owns the tag and PyPI
upload. Do not run `.github/workflows/release.yml` until that upload is intended.

## Preconditions

1. The release commit is on green `main`, with no unexplained waived checks.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, CI gate version, security support window, and release notes agree.
3. `docs/acceptance/release-gate-0.50.toml` remains Verified and
   `scripts/verify_pkg_50.py` still passes as a historical packet. The living packet is
   `scripts/verify_pkg_51.py` (omit `--allow-planned`).
4. The repository and PyPI trusted-publishing configuration are controlled by active
   maintainers; the release uses the GitHub Actions workflow.
5. The tag `v0.51.0` does not already exist locally or on the remote.
6. Keep `registry_status = "deferred"` and `pypi_version = "0.50.1"` until PyPI
   actually serves `0.51.0`. First-run copy-paste must keep using `pypi_pin_*`.

## Local release candidate

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.51.0
bash scripts/ci_checks.sh browser --python 3.12
uv run python scripts/check_release_gate.py 0.51.0
uv run python scripts/verify_pkg_51.py
uv run python scripts/verify_pkg_50.py
```

## Tag and publish

Do **not** run this section until #507 is ready to close with a real upload.

```bash
git fetch --tags origin
git rev-parse v0.51.0 >/dev/null 2>&1 && { echo "tag exists; stop"; exit 1; }
git tag -a v0.51.0 -m "Hedron 0.51.0"
git push origin v0.51.0
```

Pushing `v0.51.0` runs `.github/workflows/release.yml`, which re-runs CI, publishes
coordinated wheels to PyPI (skipping satellite versions already on the index), and
creates the GitHub Release. Release CI requires SBOM/evidence-bundle attach on train
tags (SUPPLY-025) via `scripts/build_evidence_bundle.py` and `scripts/generate_sbom.py`.
Do not retag `v0.50.3`, `v0.50.2`, `v0.50.1`, `v0.50.0`, `v0.49.1`, or `v0.49.0`.

## After a successful upload

Confirm `docs/release.toml` has `pypi_version` equal to `published_version`, matching
`pypi_pin_floor` / `pypi_pin_ceiling`, and `registry_status = "uploaded"`. Adopter
first-run pages must not say the Git tag or PyPI upload is deferred.
