# Cutting a Hedron release

**Living runbook for the current train (`0.20`).** Historical cut records live under
[`docs/archive/`](https://github.com/eddiethedean/hedron/tree/main/docs/archive) and
per-phase acceptance notes — do not retag published versions.

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.20.0`); Python package metadata omits it (`0.20.0`).

## Current published train

**Last published train:** `v0.18.0` (packages `0.18.0` including first-party
`hedron-extras`; Alpha charts/sample-kit/native/notebook/mcp/gradio `0.1.x`).

**Prior published:** `v0.17.0`, `v0.16.0`, and earlier trains.

**Current cut target:** `v0.20.0` — Ready to cut / Implemented on `main` (packages
`0.20.0`); see
[STATUS.md](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md) and
[What’s ready](guides/whats-ready.md). Phase 0.20 evidence:
[release-gate-0.20.toml](acceptance/release-gate-0.20.toml) /
[RELEASE_0_20.md](acceptance/RELEASE_0_20.md)
(`python scripts/check_release_gate.py 0.20.0`).

Do not re-run tag steps for a published version. Do **not** treat `0.20.0` as published
until `v0.20.0` is tagged.

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
   install pins describe the Ready-to-cut train (run
   `uv run python scripts/check_docs_train_ssot.py`). Do **not** flip docs to
   “Published `v0.20.0`” before the tag.

### Cut steps

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

### Post-tag docs flip (same day as publish)

After the `v0.20.0` Git tag exists and wheels are on PyPI — **not** before:

1. Edit `docs/STATUS.md` and `docs/ROADMAP.md`: replace Ready-to-cut wording with the
   published-train status for tag `v0.20.0`; last published = that tag; cut target
   advances to `0.19.x` patches / next capability `0.20`.
2. Run `uv run python scripts/sync_status_roadmap.py` (then `--check`).
3. Update root + `docs/SECURITY.md` support window (`0.19.x` current published).
4. Flip Ready-to-cut / last-published-0.18 wording in guides, acceptance, API status pages,
   package READMEs, and install notes that claim PyPI availability.
5. Invert `scripts/check_docs_train_ssot.py` patterns: ban leftover Ready-to-cut / last
   published `v0.18.0`; allow the published-train wording for tag `v0.20.0`.
6. Re-run `uv run python scripts/check_docs_train_ssot.py` and commit the flip.

## Template: 0.19.x patch cut

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
