# Cutting a Hedron release

**Living runbook for the current train (`0.21`).** Historical cut records live under
[`docs/archive/`](https://github.com/eddiethedean/hedron/tree/main/docs/archive) and
per-phase acceptance notes — do not retag published versions.

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.21.0`); Python package metadata omits it (`0.21.0`).

## Current published train

**Last published train:** `v0.21.0` (packages `0.21.0` including first-party
`hedron-extras`; Alpha charts/sample-kit/native/notebook/mcp/gradio `0.1.x`).

**Prior published:** `v0.20.0`, `v0.19.0`, `v0.18.0`, `v0.17.0`, `v0.16.0`, and earlier trains.

**Current train:** `0.21.x` — **Published** as `v0.21.0` (engineering release / D-052).
Human AT **sessions** (`SR-021` / `PARTICIPANT-021`) remain **Planned** — not Supported;
`PROTOCOL-021` is Verified. Gate index:
[release-gate-0.21.toml](acceptance/release-gate-0.21.toml) /
[RELEASE_0_21.md](acceptance/RELEASE_0_21.md) /
[human-at protocol](acceptance/human-at/);
`python scripts/check_release_gate.py 0.21.0 --allow-planned`,
`python scripts/verify_pkg_21.py`,
`python scripts/check_human_at_packet.py`.
Next capability phase: **0.22** (CSRF composition). Phase 0.20 evidence remains:
[release-gate-0.20.toml](acceptance/release-gate-0.20.toml) /
[RELEASE_0_20.md](acceptance/RELEASE_0_20.md)
(`python scripts/check_release_gate.py 0.20.0`).

Production-quality maturity program (**D-053** / RFC-0056): after 0.21/0.22, planned packets
**0.23** (stable-tier), **0.24** (live disposition), **0.25** (archetype) —
[production-quality guide](guides/production-quality.md);
`python scripts/check_release_gate.py 0.23.0 --allow-planned` (and `0.24.0` / `0.25.0`).

Do not re-run tag steps for a published version.

## Template: `v0.21.0` first cut

Use these commands for the initial `0.21.0` publish. For later patches, replace with
`0.21.1` / `v0.21.1` (see patch template below). Full Verified human-AT cut still requires
`--require-sessions` floors before flipping SR/PARTICIPANT/ARTIFACT/REMEDIATE.

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, inter-package pins, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.21.0 --allow-planned` for the engineering
   publish (session gates Planned). Drop `--allow-planned` only for the Verified human-AT cut
   when SR/PARTICIPANT/ARTIFACT/REMEDIATE are Verified.
3. Phase 0.21 gate file: `docs/acceptance/release-gate-0.21.toml`
   (`PROTOCOL-021` / `REGRESS-021` / `PKG-021` Verified; session rows Planned until real evidence).
4. **License (D-033):** root `LICENSE` and every publishable package declare license
   metadata. The release workflow refuses to publish without this.
5. Trusted publishing / `PYPI_API_TOKEN` is configured in GitHub Actions as required by
   `.github/workflows/release.yml`.
6. STATUS, STABILITY, upgrade notes, What’s ready, SECURITY support window, and adopter
   install pins describe the Published train (run
   `uv run python scripts/check_docs_train_ssot.py`).

### Cut steps (reference for `v0.21.0` / `0.21.x` patches)

`v0.21.0` is the **Published** engineering train. Use the patch template for `v0.21.1+`.
Do not invent human AT ledger rows to force Verified session gates.

1. Confirm the coordinated bump is committed on `main` (all package `pyproject.toml`,
   `__version__`, CHANGELOG sections, `uv.lock`, CI gate argument).
2. Re-run locally (same suites as CI — see `scripts/ci_checks.sh`):

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.21.0
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
git tag -a v0.21.0 -m "Hedron 0.21.0"
git push origin v0.21.0
```

### Post-tag docs flip (docs may already claim Published `v0.21.0`)

After the Git tag exists and wheels are on PyPI — **not** before inventing session evidence:

1. Keep `docs/STATUS.md` / `docs/ROADMAP.md` honest: Published engineering train; human AT
   sessions Planned until Verified.
2. Run `uv run python scripts/sync_status_roadmap.py` (then `--check`).
3. Update root + `docs/SECURITY.md` support window (current published line).
4. Re-run `uv run python scripts/check_docs_train_ssot.py` and commit any remaining pin flips.

## Template: 0.21.x patch cut

Replace `0.21.1` with the next patch.

### Preconditions

1. `main` is green on CI for Python 3.11–3.14 (including MkDocs `--strict`).
2. Package version, `__version__`, inter-package pins, and changelog entries agree:
   `uv run python scripts/check_release_gate.py 0.21.1 --allow-planned` while session gates
   remain Planned.
3. Phase 0.21 gate file: `docs/acceptance/release-gate-0.21.toml`.
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
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.21.1
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
git tag -a v0.21.1 -m "Hedron 0.21.1"
git push origin v0.21.1
```
