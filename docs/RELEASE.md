# Cutting a Hedron release

**Living runbook for the current train (`0.20`).** Historical cut records live under
[`docs/archive/`](https://github.com/eddiethedean/hedron/tree/main/docs/archive) and
per-phase acceptance notes — do not retag published versions.

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.20.0`); Python package metadata omits it (`0.20.0`).

## Current published train

**Last published train:** `v0.20.0` (packages `0.20.0` including first-party
`hedron-extras`; Alpha charts/sample-kit/native/notebook/mcp/gradio `0.1.x`).

**Prior published:** `v0.19.0`, `v0.18.0`, `v0.17.0`, `v0.16.0`, and earlier trains.

**Current train:** `0.20.x` — **Published** as `v0.20.0`. Next capability phase: **0.21**
(human AT / D-052 — **Refined / Planned**;
[release-gate-0.21.toml](acceptance/release-gate-0.21.toml) /
[RELEASE_0_21.md](acceptance/RELEASE_0_21.md) /
[human-at protocol](acceptance/human-at/);
`python scripts/check_release_gate.py 0.21.0 --allow-planned`). Patch cuts use the template
below (`v0.20.1`, …). Phase 0.20 evidence:
[release-gate-0.20.toml](acceptance/release-gate-0.20.toml) /
[RELEASE_0_20.md](acceptance/RELEASE_0_20.md)
(`python scripts/check_release_gate.py 0.20.0`).

Do not re-run tag steps for a published version.

## Template: `v0.20.0` first cut

Use these commands for the initial `0.20.0` publish. For later patches, replace with
`0.20.1` / `v0.20.1` (see patch template below).

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, inter-package pins, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.20.0` (no `--allow-planned` for publish).
3. Phase 0.20 gate file remains closed (`Verified` or owned `Deferred`):
   `docs/acceptance/release-gate-0.20.toml`.
4. **License (D-033):** root `LICENSE` and every publishable package declare license
   metadata. The release workflow refuses to publish without this.
5. Trusted publishing / `PYPI_API_TOKEN` is configured in GitHub Actions as required by
   `.github/workflows/release.yml`.
6. STATUS, STABILITY, upgrade notes, What’s ready, SECURITY support window, and adopter
   install pins describe the Published train (run
   `uv run python scripts/check_docs_train_ssot.py`). For a fresh major/minor cut, do
   **not** flip docs to “Published `vX.Y.0`” before that tag exists.

### Cut steps (historical for `v0.20.0`; reuse for `0.20.x` patches)

`v0.20.0` is **Published**. Use the patch template below for `v0.20.1+`. The numbered
steps remain as the reference procedure for the next capability tag.

1. Confirm the coordinated bump is committed on `main` (all package `pyproject.toml`,
   `__version__`, CHANGELOG sections, `uv.lock`, CI gate argument).
2. Re-run locally (same suites as CI — see `scripts/ci_checks.sh`):

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.20.0
# optional: bash scripts/ci_checks.sh browser --python 3.12
```

3. Build evidence + optional wheel rehearse:

```bash
uv run python scripts/build_evidence_bundle.py
rm -rf dist/wheels-scratch  # optional
# build packages as needed, then:
uv run python scripts/rehearse_release.py
```

4. Tag and push (trusted workflow publishes when configured):

```bash
git tag -a v0.20.0 -m "Hedron 0.20.0"
git push origin v0.20.0
```

### Post-tag docs flip (completed for `v0.20.0`)

After the Git tag exists and wheels are on PyPI — **not** before:

1. Edit `docs/STATUS.md` and `docs/ROADMAP.md`: set **Published** for the tag; last
   published = that tag; next capability advances (for 0.20 → `0.20.x` patches / **0.21**).
2. Run `uv run python scripts/sync_status_roadmap.py` (then `--check`).
3. Update root + `docs/SECURITY.md` support window (current published line).
4. Flip pre-tag cut-status / prior last-published wording in guides, acceptance, API status
   pages, package READMEs, and install notes.
5. Invert `scripts/check_docs_train_ssot.py`: ban leftover pre-tag cut wording / prior last
   published; allow Published wording for the new tag.
6. Re-run `uv run python scripts/check_docs_train_ssot.py` and commit the flip.

## Template: 0.20.x patch cut

Replace `0.20.1` with the next patch.

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, inter-package pins, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.20.1` (no `--allow-planned` for publish).
3. Phase 0.20 gate file remains closed (`Verified` or owned `Deferred`):
   `docs/acceptance/release-gate-0.20.toml`.
4. **License (D-033):** root `LICENSE` and every publishable package declare license
   metadata. The release workflow refuses to publish without this.
5. Trusted publishing / `PYPI_API_TOKEN` is configured in GitHub Actions as required by
   `.github/workflows/release.yml`.
6. STATUS, STABILITY, upgrade notes, What’s ready, SECURITY support window, and adopter
   install pins describe the new patch version (run
   `uv run python scripts/check_docs_train_ssot.py`).

### Cut steps

1. Confirm the coordinated bump is committed on `main` (all package `pyproject.toml`,
   `__version__`, CHANGELOG sections, `uv.lock`, CI gate argument).
2. Re-run locally (same suites as CI — see `scripts/ci_checks.sh`):

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.20.1
# optional: bash scripts/ci_checks.sh browser --python 3.12
```

3. Build evidence + optional wheel rehearse:

```bash
uv run python scripts/build_evidence_bundle.py
rm -rf dist/wheels-scratch  # optional
# build packages as needed, then:
uv run python scripts/rehearse_release.py
```

4. Tag and push (trusted workflow publishes when configured):

```bash
git tag -a v0.20.1 -m "Hedron 0.20.1"
git push origin v0.20.1
```
