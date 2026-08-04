# Cutting a Hedron release

**Living runbook for the next coordinated train.** Historical cut notes for
`v0.1.0`–`v0.10.0` live in
[`docs/archive/RELEASE_HISTORY_0.1-0.10.md`](https://github.com/eddiethedean/hedron/blob/main/docs/archive/RELEASE_HISTORY_0.1-0.10.md)
(do not retag published versions).

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.11.0`); Python package metadata omits it (`0.11.0`).

## Current published train

**`v0.10.0`** (packages `0.10.0`) — see [STATUS.md](STATUS.md).

## Next cut: `v0.11.0` (native Flask/Django depth)

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.11.0` (use `--allow-planned` only
   during development).
3. Phase acceptance / gate file for 0.11 is checked (`Verified` or owned `Deferred`):
   see `docs/acceptance/` and [STATUS.md](STATUS.md).
4. **License (D-033):** root `LICENSE` and every publishable package declare license
   metadata. The release workflow refuses to publish without this.
5. `PYPI_API_TOKEN` is configured in GitHub Actions secrets.
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
