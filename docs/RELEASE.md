# Cutting a Hedron release

**Living runbook for the next coordinated train.** Historical cut notes for
`v0.1.0`–`v0.10.0` live in
[`docs/archive/RELEASE_HISTORY_0.1-0.10.md`](https://github.com/eddiethedean/hedron/blob/main/docs/archive/RELEASE_HISTORY_0.1-0.10.md)
(do not retag published versions).

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.10.1`); Python package metadata omits it (`0.10.1`).

## Current published train

**Current train:** `v0.10.1` (packages `0.10.1`) — see [STATUS.md](STATUS.md).
**Next cut:** `v0.11.0` (capability phase) or `v0.10.2` (patch). Historical cuts:
[`docs/archive/RELEASE_HISTORY_0.1-0.10.md`](https://github.com/eddiethedean/hedron/blob/main/docs/archive/RELEASE_HISTORY_0.1-0.10.md).

## Cut: `v0.10.1` (0.10 security/correctness patch) — published

The checklist below is retained as the **executed** cut record for `v0.10.1`. Do not
re-run the tag steps. For a new patch, copy this section for `v0.10.2` (or proceed to
`v0.11.0`).

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, inter-package pins, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.10.1` (no `--allow-planned`).
3. Phase 0.10 gate file remains closed (`Verified` or owned `Deferred`):
   `docs/acceptance/release-gate-0.10.toml`.
4. **License (D-033):** root `LICENSE` and every publishable package declare license
   metadata. The release workflow refuses to publish without this.
5. Trusted publishing / `PYPI_API_TOKEN` is configured in GitHub Actions as required by
   `.github/workflows/release.yml`.
6. STATUS, STABILITY, upgrade notes, and adopter install pins describe `0.10.1`.

### Cut steps

1. Confirm the coordinated bump is committed on `main` (all package `pyproject.toml`,
   `__version__`, CHANGELOG `[0.10.1]` sections, `uv.lock`, CI gate argument).
2. Re-run locally:

```bash
uv run python scripts/check_release_gate.py 0.10.1
uv run python scripts/verify_pkg_10.py
uv run ruff format --check packages tests examples
uv run ruff check packages tests examples
uv run pyright
uv run pytest -q
uv run --group docs mkdocs build --strict
```

3. Optional rehearse against local wheels:

```bash
rm -rf dist && for p in packages/*/pyproject.toml; do uv build --package "$(basename "$(dirname "$p")")"; done
uv run python scripts/rehearse_release.py
```

4. Tag and push (trusted workflow publishes):

```bash
git tag -a v0.10.1 -m "Hedron 0.10.1"
git push origin v0.10.1
```

5. After publish: verify clean-venv `pip install hedron==0.10.1`, update any remaining
   “current train” copy if needed, and never retag. Yank and ship `0.10.2` if a bad
   artifact ships.

### After publication

- Smoke: install from PyPI, render a page, optionally `hedron build` on the reference app.
- Keep root `STATUS.md` / `ROADMAP.md` mirrors synced from `docs/`.

## Next phase cut: `v0.11.0` (native Flask/Django depth)

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.11.0` (use `--allow-planned` only
   during development).
3. Phase acceptance / gate file for 0.11 is checked (`Verified` or owned `Deferred`):
   see `docs/acceptance/` and [STATUS.md](STATUS.md).
4. **License (D-033):** root `LICENSE` and every publishable package declare license
   metadata. The release workflow refuses to publish without this.
5. Trusted publishing / `PYPI_API_TOKEN` is configured in GitHub Actions secrets.
6. Stability catalog, compatibility notes, upgrade guide, and adopter docs match the
   claimed surface (Supported vs Deferred language aligned).

### Cut steps

1. Synchronize package versions and per-package `CHANGELOG.md` sections on the release
   branch.
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

6. After publish: verify clean-venv install and hashes; update [STATUS.md](STATUS.md)
   and README; run `uv run python scripts/sync_status_roadmap.py`.
7. Never retag or overwrite a published artifact. Yank and ship a patch if needed.

### After publication

- Smoke: install from PyPI, render a page, optionally `hedron build` on the reference app.
- Keep root `STATUS.md` / `ROADMAP.md` mirrors synced from `docs/`.
- Record any new Deferred rows honestly on [What’s ready](guides/whats-ready.md).

## Scripts (maintainer)

See [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md) for `check_release_gate.py`,
`verify_pkg_*.py`, `rehearse_release.py`, and evidence helpers.
