# Cutting a Hedron release

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.1.0`); Python package metadata omits it (`0.1.0`).

## Preconditions

1. `main` is green on CI for Python 3.11–3.14.
2. Package version, `__version__`, and changelog entry agree
   (`uv run python scripts/check_release_gate.py 0.2.0`).
3. Phase acceptance subsets for the release are checked:
   - [SECURITY.md](acceptance/SECURITY.md) phase 0.2
   - [FASTAPI_INTEGRATION.md](acceptance/FASTAPI_INTEGRATION.md) MVP exit
   - [HTMX.md](acceptance/HTMX.md) phase 0.2
   - [EXPLORER.md](acceptance/EXPLORER.md) phase 0.2 preview
   - [COMPONENT_MODEL.md](acceptance/COMPONENT_MODEL.md) FastAPI parity
4. **License (D-033):** a root `LICENSE` file exists and every publishable
   package declares `[project].license` / `license-files`. The release workflow
   refuses to publish without this.
5. `PYPI_API_TOKEN` is configured in GitHub Actions secrets (already required by
   `.github/workflows/release.yml`).
6. **PyPI name:** publishing `hedron==0.2.0` reclaims the existing PyPI project
   `hedron` (same author; prior geolocation releases ≤`0.0.6`). Confirm that
   reclaim is intentional before pushing the tag.

## Cut `v0.1.0` (`hedron-core` only)

Already published. Do not retag.

## Cut `v0.2.0` (coordinated train)

> **Status:** Implementation and acceptance subsets for the 0.2 MVP are on
> `main` at package version `0.2.0`. Cut when CI is green and maintainers are
> ready to publish.

1. Confirm `packages/{hedron-core,hedron,hedron-explorer}` all say `0.2.0` in
   `pyproject.toml` and `__version__`, with matching `CHANGELOG.md` sections.
2. Confirm the acceptance subsets listed under Preconditions.
3. Confirm the latest `main` CI run is green (format, lint, pyright, tests,
   build, smoke on 3.11–3.14).
4. Push `main` if needed, then create and push the annotated tag:

```bash
git tag -a v0.2.0 -m "Hedron 0.2.0"
git push origin v0.2.0
```

5. The Release workflow builds and publishes every workspace package, then creates
   a GitHub Release attaching all wheels/sdists.
6. Verify:

```bash
pip index versions hedron-core
pip index versions hedron
pip index versions hedron-explorer
gh release view v0.2.0
```

7. Point changelog compare URLs at the new release tag and update
   `docs/STATUS.md` to record publication.

## After publication

- Install from a clean venv and re-run the smoke render.
- Update `docs/STATUS.md` if the published state changed.
- Begin the next phase packet only after the release is confirmed.
