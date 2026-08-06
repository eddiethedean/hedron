# Cutting a Hedron release

**Living runbook for the next coordinated train.** Executed cut records live in
[`docs/archive/`](https://github.com/eddiethedean/hedron/tree/main/docs/archive)
(do not retag published versions).

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.11.0`); Python package metadata omits it (`0.11.0`).

## Current published train

**Last published train:** `v0.18.0` (packages `0.18.0` including first-party `hedron-extras`;
Alpha charts/sample-kit/native/notebook/mcp/gradio `0.1.x`).
**Prior published:** `v0.17.0` (dashboards/agent interfaces), `v0.16.0`, `v0.15.0`, and earlier trains.
**Current cut target:** `v0.18.x` patches or `v0.19.0` (accessibility) — see
[STATUS.md](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md) and
[What’s ready](guides/whats-ready.md).
**Next capability phase:** `v0.19.0`.

Published trains include `v0.18.0`, `v0.17.0`, `v0.16.0`, `v0.15.0`, `v0.14.0`, `v0.13.0`, `v0.12.0`, `v0.11.0`, and
[`docs/archive/RELEASE_HISTORY_0.1-0.10.md`](https://github.com/eddiethedean/hedron/blob/main/docs/archive/RELEASE_HISTORY_0.1-0.10.md).
Do not re-run tag steps for a published version.

## Template: patch cut (`v0.10.x`)

Replace `0.10.2` with the next patch.

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, inter-package pins, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.10.2` (no `--allow-planned`).
3. Phase 0.10 gate file remains closed (`Verified` or owned `Deferred`):
   `docs/acceptance/release-gate-0.10.toml`.
4. **License (D-033):** root `LICENSE` and every publishable package declare license
   metadata. The release workflow refuses to publish without this.
5. Trusted publishing / `PYPI_API_TOKEN` is configured in GitHub Actions as required by
   `.github/workflows/release.yml`.
6. STATUS, STABILITY, upgrade notes, What’s ready, and adopter install pins describe the
   new patch version.

### Cut steps

1. Confirm the coordinated bump is committed on `main` (all package `pyproject.toml`,
   `__version__`, CHANGELOG sections, `uv.lock`, CI gate argument).
2. Re-run locally:

```bash
uv run python scripts/check_release_gate.py 0.10.2
uv run python scripts/verify_pkg_10.py
uv run ruff format --check packages tests examples
uv run ruff check packages tests examples
uv run pyright
uv run pytest -q
uv run --group docs mkdocs build --strict
uv run python scripts/sync_status_roadmap.py --check
```

3. Optional rehearse against local wheels:

```bash
rm -rf dist && for p in packages/*/pyproject.toml; do uv build --package "$(basename "$(dirname "$p")")"; done
uv run python scripts/rehearse_release.py
```

4. Tag and push (trusted workflow publishes):

```bash
git tag -a v0.10.2 -m "Hedron 0.10.2"
git push origin v0.10.2
```

5. After publish: verify clean-venv `pip install hedron==0.10.2`, update What’s ready /
   README pins if needed, and never retag. Yank and ship the next patch if a bad artifact
   ships.

### After publication

- Smoke: install from PyPI, render a page, optionally `hedron build` on the reference app.
- Keep root `STATUS.md` / `ROADMAP.md` mirrors synced:
  `uv run python scripts/sync_status_roadmap.py`.

## Published phase cut: `v0.11.0` (native Flask/Django depth)

Published train — do not retag. Preconditions and cut steps below are historical for the
`v0.11.0` cut.

### Preconditions (historical)

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.11.0` (use `--allow-planned` only
   during development).
3. Phase acceptance / gate file for 0.11 is checked (`Verified` or owned `Deferred`):
   see `docs/acceptance/release-gate-0.11.toml` and
   [STATUS.md](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md).
4. **License (D-033):** root `LICENSE` and every publishable package declare license
   metadata.
5. Trusted publishing / `PYPI_API_TOKEN` is configured in GitHub Actions secrets.
6. Stability catalog, compatibility notes, upgrade guide, and adopter docs match the
   claimed surface (Supported vs Deferred language aligned).

### Cut steps (historical)

1. Synchronize package versions and per-package `CHANGELOG.md` sections on the release
   branch; update the train [Release notes](guides/release-notes.md) page.
2. Close the 0.11 acceptance packet; replace Planned gate rows with Verified or owned
   Deferred.
3. Run supply-chain scripts (see [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md)):
   `build_evidence_bundle.py`, SBOM, license inventory, asset audit as required by the
   gate.
4. Rehearse install: `uv run python scripts/rehearse_release.py`.
5. Tag and push (trusted workflow publishes):

```bash
git tag -a v0.11.0 -m "Hedron 0.11.0"
git push origin v0.11.0
```

6. After publish: verify clean-venv install and hashes; update STATUS and What’s ready;
   run `uv run python scripts/sync_status_roadmap.py`.
7. Never retag or overwrite a published artifact. Yank and ship a patch if needed.

### After publication

- Smoke: install from PyPI, render a page, optionally `hedron build` on the reference app.
- Record any new Deferred rows honestly on [What’s ready](guides/whats-ready.md).

## Published phase cut: `v0.13.0` (advanced async and observability)

Published train — do not retag. See [`RELEASE_0_13.md`](acceptance/RELEASE_0_13.md) and
[`release-gate-0.13.toml`](acceptance/release-gate-0.13.toml).

## Published phase cut: `v0.14.0` (portable runtimes and acceleration)

Published train — do not retag. See [`RELEASE_0_14.md`](acceptance/RELEASE_0_14.md) and
[`release-gate-0.14.toml`](acceptance/release-gate-0.14.toml).

## Published phase cut: `v0.16.0` (curated extras and analysis workbenches)

Published train — do not retag. See [`RELEASE_0_16.md`](acceptance/RELEASE_0_16.md) and
[`release-gate-0.16.toml`](acceptance/release-gate-0.16.toml). Phase 0.15 acceptance remains at
[`RELEASE_0_15.md`](acceptance/RELEASE_0_15.md) for the prior `v0.15.0` tag.

## Published phase cut: `v0.17.0` (reactive dashboards and agent interfaces)

Published train — do not retag. See [`RELEASE_0_17.md`](acceptance/RELEASE_0_17.md) and
[`release-gate-0.17.toml`](acceptance/release-gate-0.17.toml). Alpha packages
`hedron-notebook` / `hedron-mcp` ship as `0.1.0` (Experimental).

## Scripts (maintainer)

See [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md) for `check_release_gate.py`,
`rehearse_release.py`, `verify_pkg_17.py` / `verify_pkg_16.py` / `verify_pkg_15.py` / `verify_pkg_14.py`, and
evidence helpers.
