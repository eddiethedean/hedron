# Cutting a Hedron release

**Living runbook for the current train (`0.18`).** Historical cut records live under
[`docs/archive/`](https://github.com/eddiethedean/hedron/tree/main/docs/archive) and
per-phase acceptance notes — do not retag published versions.

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.18.0`); Python package metadata omits it (`0.18.0`).

## Current published train

**Last published train:** `v0.18.0` (packages `0.18.0` including first-party
`hedron-extras`; Alpha charts/sample-kit/native/notebook/mcp/gradio `0.1.x`).

**Prior published:** `v0.17.0`, `v0.16.0`, `v0.15.0`, and earlier trains.

**Current cut target:** `v0.18.x` patches or `v0.19.0` — see
[STATUS.md](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md) and
[What’s ready](guides/whats-ready.md). Phase 0.19 evidence scaffold:
[release-gate-0.19.toml](acceptance/release-gate-0.19.toml) /
[RELEASE_0_19.md](acceptance/RELEASE_0_19.md)
(`python scripts/check_release_gate.py 0.19.0 --allow-planned` after the package train bumps to
`0.19.0`; until then validate the manifest with
`python scripts/check_release_gate.py 0.18.0 --allow-planned --evidence-manifest docs/acceptance/release-gate-0.19.toml`).

Do not re-run tag steps for a published version.

## Template: 0.18.x patch cut

Replace `0.18.1` with the next patch (or use `0.18.0` only as a historical checklist).

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, inter-package pins, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.18.1` (no `--allow-planned` for publish).
3. Phase 0.18 gate file remains closed (`Verified` or owned `Deferred`):
   `docs/acceptance/release-gate-0.18.toml`.
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
2. Re-run locally:

```bash
uv run python scripts/check_release_gate.py 0.18.1
uv run python scripts/verify_pkg_18.py
uv run python scripts/check_docs_train_ssot.py
uv run ruff format --check packages tests examples
uv run ruff check packages tests examples
uv run pyright
uv run pytest -q
uv run --group docs mkdocs build --strict
uv run python scripts/sync_status_roadmap.py --check
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
git tag -a v0.18.1 -m "Hedron 0.18.1"
git push origin v0.18.1
```

5. Publish / attach a GitHub Release for the tag with wheels (at least `hedron` +
   `hedron-core`) and `dist/evidence-bundle/*` (SBOM, license inventory, bundle tarball).
   PyPI remains authoritative for package versions; Release assets support evaluators —
   see [Evidence pack](guides/evidence-pack.md).

6. After publish: verify clean-venv `pip install hedron==0.18.1`, update What’s ready /
   README pins if needed, and never retag. Yank and ship the next patch if a bad artifact
   ships.

### After publication

- Smoke: install from PyPI, render a page, optionally `hedron build` on the reference app.
- Keep root `STATUS.md` / `ROADMAP.md` mirrors synced:
  `uv run python scripts/sync_status_roadmap.py`.

## Historical trains

Published cut notes (do not retag):

| Train | Notes |
|---|---|
| `v0.17.0` | [`RELEASE_0_17.md`](acceptance/RELEASE_0_17.md) / `release-gate-0.17.toml` |
| `v0.16.0` | [`RELEASE_0_16.md`](acceptance/RELEASE_0_16.md) |
| `v0.15.0` | [`RELEASE_0_15.md`](acceptance/RELEASE_0_15.md) |
| `v0.14.0` | [`RELEASE_0_14.md`](acceptance/RELEASE_0_14.md) |
| `v0.13.0` | [`RELEASE_0_13.md`](acceptance/RELEASE_0_13.md) |
| `v0.11.0` / `0.10.x` | Archive under [`docs/archive/`](https://github.com/eddiethedean/hedron/tree/main/docs/archive); older verify scripts `verify_pkg_10.py` … `verify_pkg_17.py` |

## Scripts (maintainer)

See [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md)
for `check_release_gate.py`, `rehearse_release.py`, **`verify_pkg_18.py`**,
`build_evidence_bundle.py`, and `check_docs_train_ssot.py`.
