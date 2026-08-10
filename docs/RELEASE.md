# Cutting a Hedron release

**Living runbook for the current train (`0.25`).** Historical cut records live under
[`docs/archive/`](https://github.com/eddiethedean/hedron/tree/main/docs/archive) and
per-phase acceptance notes.

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.25.0`); Python package metadata omits it (`0.25.0`).

## Current published train

**Last published train:** `v0.25.0` (packages `0.25.0` including first-party
`hedron-extras`; Alpha charts/sample-kit/native/notebook/mcp/gradio `0.1.x`).

**Prepared candidate (not tagged):** Beta packages `0.25.1`; charts and sample kit
`0.1.6`. Do not describe these versions as published until the tag workflow succeeds.

**Prior published:** `v0.24.0`, `v0.23.0`, `v0.22.0`, `v0.21.0`, `v0.20.0`, `v0.19.0`, `v0.18.0`, `v0.17.0`, `v0.16.0`, and earlier trains.

**Current train:** `0.25.x` — **Published** as `v0.25.0` (production archetype / landmines /
D-053). Gate index:
[release-gate-0.25.toml](acceptance/release-gate-0.25.toml) /
[RELEASE_0_25.md](acceptance/RELEASE_0_25.md);
`python scripts/check_release_gate.py 0.25.0`,
`python scripts/verify_pkg_25.py`.
Human AT **sessions** (`SR-021` / `PARTICIPANT-021`) remain **Planned** — not Supported
(carryover from 0.21). Phase 0.24 evidence remains:
[release-gate-0.24.toml](acceptance/release-gate-0.24.toml) /
[RELEASE_0_24.md](acceptance/RELEASE_0_24.md).

Production-quality maturity program (**D-053** / RFC-0056): packet **0.25** is **Verified** —
[PRODUCTION_ARCHETYPE](api/PRODUCTION_ARCHETYPE.md) ·
[production-quality guide](guides/production-quality.md);
`python scripts/verify_pkg_25.py`.

### Tag rule

- If `git rev-parse v0.25.0` **fails** (tag missing locally/remotely), run the **Cut
  steps** below once from green `main`.
- If `v0.25.0` **already exists** on the remote (and PyPI serves `0.25.0`), do **not**
  retag or overwrite the release — use the **0.25.x patch** template for later fixes.

### Supply chain attach (`SUPPLY-025`)

Train tags **require SBOM and evidence-bundle attach** on every train tag (`SUPPLY-025`).
Regenerate with:

```bash
uv run python scripts/build_evidence_bundle.py
uv run python scripts/generate_sbom.py
```

Attach the resulting artifacts to the GitHub Release for the train tag. Instructions for
the Evidence pack remain in [acceptance/EVIDENCE.md](acceptance/EVIDENCE.md).

## Record: `v0.25.0` cut

Commands for the `0.25.0` publish. Skip tagging when `v0.25.0` already exists (see **Tag
rule**). For later patches, replace with `0.25.1` / `v0.25.1` (see patch template below).

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, inter-package pins, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.25.0`
3. Phase 0.25 gate file: `docs/acceptance/release-gate-0.25.toml`
   (all Verified).
4. **License (D-033):** root `LICENSE` and every publishable package declare license
   metadata. The release workflow refuses to publish without this.
5. Trusted publishing / `PYPI_API_TOKEN` is configured in GitHub Actions as required by
   `.github/workflows/release.yml`.
6. STATUS, STABILITY, upgrade notes, What’s ready, SECURITY support window, and adopter
   install pins describe the Published train (run
   `uv run python scripts/check_docs_train_ssot.py`).

### Cut steps (`v0.25.0`)

`v0.25.0` is the **Published** production-archetype train. Use the patch
template for `v0.25.1+`.

1. Confirm the coordinated bump is committed on `main` (all package `pyproject.toml`,
   `__version__`, CHANGELOG sections, `uv.lock`, CI gate argument).
2. Re-run locally (same suites as CI — see `scripts/ci_checks.sh`):

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.25.0
# optional: bash scripts/ci_checks.sh browser --python 3.12
python scripts/verify_pkg_25.py
```

3. Build evidence + optional wheel rehearse:

```bash
uv run python scripts/build_evidence_bundle.py
rm -rf dist/wheels-scratch  # optional
# build packages as needed, then:
uv run python scripts/rehearse_release.py
```

4. Tag and push **only if** `v0.25.0` is still missing (trusted workflow publishes when
   configured):

```bash
git rev-parse v0.25.0 >/dev/null 2>&1 && echo "tag exists — do not retag" && exit 1
git tag -a v0.25.0 -m "Hedron 0.25.0"
git push origin v0.25.0
```

### Post-tag checklist

After the Git tag exists and wheels are on PyPI:

1. Keep `docs/STATUS.md` / `docs/ROADMAP.md` honest: Published 0.25 train; keep human AT sessions Planned until Verified.
2. Run `uv run python scripts/sync_status_roadmap.py` (then `--check`).
3. Confirm root + `docs/SECURITY.md` support window lists the current published line.
4. Re-run `uv run python scripts/check_docs_train_ssot.py`.

## Template: 0.25.x patch cut

Replace `0.25.1` with the next patch.

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, inter-package pins, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.25.1`
3. Phase 0.25 gate file: `docs/acceptance/release-gate-0.25.toml`.
4. **License (D-033):** root `LICENSE` and every publishable package declare license
   metadata. The release workflow refuses to publish without this.
5. Trusted publishing / `PYPI_API_TOKEN` is configured in GitHub Actions as required by
   `.github/workflows/release.yml`.
6. STATUS, STABILITY, upgrade notes, What’s ready, SECURITY support window, and adopter
   install pins describe the new patch version (run
   `uv run python scripts/check_docs_train_ssot.py`).

### Cut steps

1. Confirm the coordinated bump is committed on `main` (all package `pyproject.toml`,
   `__version__`, plugin metadata, CHANGELOG sections, `uv.lock`, CI gate argument).
   For this patch, confirm charts/sample-kit are `0.1.6` and `hedron[charts]` requires
   `hedron-charts>=0.1.6,<0.2`.
2. Re-run locally (same suites as CI — see `scripts/ci_checks.sh`):

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.25.1
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
git tag -a v0.25.1 -m "Hedron 0.25.1"
git push origin v0.25.1
```
