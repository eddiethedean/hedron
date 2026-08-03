# Cutting a Hedron release

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.1.0`); Python package metadata omits it (`0.1.0`).

## Preconditions

1. `main` is green on CI for Python 3.11–3.14.
2. Package version, `__version__`, and changelog entry agree.
3. Phase acceptance subsets for the release are checked.
4. **License (D-033):** a root `LICENSE` file exists and every publishable
   package declares `[project].license` / `license-files`. The release workflow
   refuses to publish without this.
5. `PYPI_API_TOKEN` is configured in GitHub Actions secrets (already required by
   `.github/workflows/release.yml`).

## Cut `v0.1.0` (`hedron-core` only)

1. Confirm `packages/hedron-core/pyproject.toml` and
   `packages/hedron-core/src/hedron_core/__init__.py` both say `0.1.0`.
2. Confirm `packages/hedron-core/CHANGELOG.md` has a dated `[0.1.0]` section.
3. Push `main` if needed, then create and push the annotated tag:

```bash
git tag -a v0.1.0 -m "hedron-core 0.1.0"
git push origin v0.1.0
```

4. The Release workflow runs the full matrix, builds artifacts, publishes to
   PyPI, and creates the GitHub Release from the changelog.
5. Verify:

```bash
pip index versions hedron-core
gh release view v0.1.0
```

Do not retag or republish the same version. Patch releases use `v0.1.1`, etc.,
and remain within the owning roadmap phase.

## Cut `v0.2.0` (coordinated train)

1. Confirm `packages/{hedron-core,hedron,hedron-explorer}` all say `0.2.0` in
   `pyproject.toml` and `__version__`, with matching `CHANGELOG.md` sections.
2. Confirm FastAPI/security/HTMX acceptance subsets for phase 0.2 are checked.
3. Push `main` if needed, then create and push the annotated tag:

```bash
git tag -a v0.2.0 -m "Hedron 0.2.0"
git push origin v0.2.0
```

4. The Release workflow builds and publishes every workspace package, then creates
   a GitHub Release attaching all wheels/sdists.
5. Verify:

```bash
pip index versions hedron-core
pip index versions hedron
pip index versions hedron-explorer
gh release view v0.2.0
```

## After publication

- Install from a clean venv and re-run the smoke render.
- Update `docs/STATUS.md` if the published state changed.
- Begin the next phase packet only after the release is confirmed.
