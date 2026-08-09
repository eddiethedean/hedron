# Cutting a Hedron release

**Living runbook for the current train (`0.24`).** Historical cut records live under
[`docs/archive/`](https://github.com/eddiethedean/hedron/tree/main/docs/archive) and
per-phase acceptance notes — do not retag published versions.

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.24.0`); Python package metadata omits it (`0.24.0`).

## Current published train

**Last published train:** `v0.24.0` (packages `0.24.0` including first-party
`hedron-extras`; Alpha charts/sample-kit/native/notebook/mcp/gradio `0.1.x`).

**Prior published:** `v0.23.0`, `v0.22.0`, `v0.21.0`, `v0.20.0`, `v0.19.0`, `v0.18.0`, `v0.17.0`, `v0.16.0`, and earlier trains.

**Current train:** `0.24.x` — **Published** as `v0.24.0` (live disposition `polling_only` / D-053).
Gate index:
[release-gate-0.24.toml](acceptance/release-gate-0.24.toml) /
[RELEASE_0_24.md](acceptance/RELEASE_0_24.md);
`python scripts/check_release_gate.py 0.24.0`,
`python scripts/verify_pkg_24.py`.
Human AT **sessions** (`SR-021` / `PARTICIPANT-021`) remain **Planned** — not Supported
(carryover from 0.21). Phase 0.23 evidence remains:
[release-gate-0.23.toml](acceptance/release-gate-0.23.toml) /
[RELEASE_0_23.md](acceptance/RELEASE_0_23.md).

Production-quality maturity program (**D-053** / RFC-0056): next packet
**0.25** (archetype) — **packet refine complete**;
[PRODUCTION_ARCHETYPE](api/PRODUCTION_ARCHETYPE.md) ·
[production-quality guide](guides/production-quality.md);
`python scripts/verify_pkg_25.py --allow-planned`.

### Supply chain attach (`SUPPLY-025`)

Train tags **require SBOM and evidence-bundle attach** on every train tag (`SUPPLY-025`).
Regenerate with:

```bash
uv run python scripts/build_evidence_bundle.py
uv run python scripts/generate_sbom.py
```

Attach the resulting artifacts to the GitHub Release for the train tag. Instructions for
the Evidence pack remain in [acceptance/EVIDENCE.md](acceptance/EVIDENCE.md).

Do not re-run tag steps for a published version.

## Record: `v0.24.0` cut

Reference commands for the `0.24.0` publish. Do **not** re-run tag steps for a published
version. For later patches, replace with `0.24.1` / `v0.24.1` (see patch template below).

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, inter-package pins, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.24.0`
3. Phase 0.24 gate file: `docs/acceptance/release-gate-0.24.toml`
   (all Verified).
4. **License (D-033):** root `LICENSE` and every publishable package declare license
   metadata. The release workflow refuses to publish without this.
5. Trusted publishing / `PYPI_API_TOKEN` is configured in GitHub Actions as required by
   `.github/workflows/release.yml`.
6. STATUS, STABILITY, upgrade notes, What’s ready, SECURITY support window, and adopter
   install pins describe the Published train (run
   `uv run python scripts/check_docs_train_ssot.py`).

### Cut steps (reference for `v0.24.0` / `0.24.x` patches)

`v0.24.0` is the **Published** live-disposition (`polling_only`) train. Use the patch
template for `v0.24.1+`.

1. Confirm the coordinated bump is committed on `main` (all package `pyproject.toml`,
   `__version__`, CHANGELOG sections, `uv.lock`, CI gate argument).
2. Re-run locally (same suites as CI — see `scripts/ci_checks.sh`):

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.24.0
# optional: bash scripts/ci_checks.sh browser --python 3.12
python scripts/verify_pkg_24.py
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
git tag -a v0.24.0 -m "Hedron 0.24.0"
git push origin v0.24.0
```

### Post-tag docs flip

After the Git tag exists and wheels are on PyPI — **not** before inventing session evidence:

1. Keep `docs/STATUS.md` / `docs/ROADMAP.md` honest: Published 0.24 train; keep human AT sessions Planned until Verified.
2. Run `uv run python scripts/sync_status_roadmap.py` (then `--check`).
3. Update root + `docs/SECURITY.md` support window (current published line).
4. Re-run `uv run python scripts/check_docs_train_ssot.py` and commit any remaining pin flips.

## Template: 0.24.x patch cut

Replace `0.24.1` with the next patch.

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, inter-package pins, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.24.1`
3. Phase 0.24 gate file: `docs/acceptance/release-gate-0.24.toml`.
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
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.24.1
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
git tag -a v0.24.1 -m "Hedron 0.24.1"
git push origin v0.24.1
```
