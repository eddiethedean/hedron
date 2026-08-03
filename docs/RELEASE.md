# Cutting a Hedron release

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.3.0`); Python package metadata omits it (`0.3.0`).

## Preconditions

1. `main` is green on CI for Python 3.11–3.14.
2. Package version, `__version__`, and changelog entry agree
   (`uv run python scripts/check_release_gate.py 0.3.0`).
3. Phase acceptance subsets for the release are checked (or explicitly Deferred):
   - [SECURITY.md](acceptance/SECURITY.md) phase 0.2 + 0.3 asset URL policy
   - [FASTAPI_INTEGRATION.md](acceptance/FASTAPI_INTEGRATION.md) MVP exit
   - [HTMX.md](acceptance/HTMX.md) phase 0.2
   - [EXPLORER.md](acceptance/EXPLORER.md) phase 0.2 preview
   - [COMPONENT_MODEL.md](acceptance/COMPONENT_MODEL.md) FastAPI parity + Python/HDN equivalence
   - [HDN.md](acceptance/HDN.md) phase 0.3 language/tooling exit
   - [SCOPED_STYLES.md](acceptance/SCOPED_STYLES.md) phase 0.3 compilation/delivery exit
4. **License (D-033):** a root `LICENSE` file exists and every publishable
   package declares `[project].license` / `license-files`. The release workflow
   refuses to publish without this.
5. `PYPI_API_TOKEN` is configured in GitHub Actions secrets (already required by
   `.github/workflows/release.yml`).
6. **PyPI name:** the `hedron` project on PyPI is this FastAPI framework train
   (reclaimed at `0.2.0`). Prior geolocation releases (`<=0.0.6`) remain
   historical; keep the project description aligned after each publish.

## Cut `v0.1.0` (`hedron-core` only)

Already published. Do not retag.

## Cut `v0.2.0` (coordinated train)

> **Status:** Published as `v0.2.0` on 2026-08-03. Do not retag.

## Cut `v0.3.0` (authoring, styles, assets, themes)

> **Status:** Published as `v0.3.0` on 2026-08-03. Do not retag.

## After publication

- Install from a clean venv and re-run the smoke render (and a quick
  `hedron build` against the reference app if convenient).
- Update `docs/STATUS.md` if the published state changed.
- Begin the next phase packet only after the release is confirmed.
