# Cutting a Hedron release

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.3.0`); Python package metadata omits it (`0.3.0`).

## Preconditions

1. `main` is green on CI for Python 3.11–3.14.
2. Package version, `__version__`, and changelog entry agree
   (`uv run python scripts/check_release_gate.py 0.4.0`).
3. Phase acceptance subsets for the release are checked (or explicitly Deferred):
   - [SECURITY.md](acceptance/SECURITY.md) phase 0.2 + 0.3 asset URL policy + 0.4 SARIF
   - [FASTAPI_INTEGRATION.md](acceptance/FASTAPI_INTEGRATION.md) MVP exit
   - [HTMX.md](acceptance/HTMX.md) phase 0.2
   - [EXPLORER.md](acceptance/EXPLORER.md) phase 0.4
   - [CLI.md](acceptance/CLI.md) phase 0.4
   - [PLUGINS.md](acceptance/PLUGINS.md) phase 0.4
   - [TESTING.md](acceptance/TESTING.md) phase 0.4
   - [COMPONENT_MODEL.md](acceptance/COMPONENT_MODEL.md) FastAPI parity + Python/HDN equivalence
   - [HDN.md](acceptance/HDN.md) phase 0.3 language/tooling exit
   - [SCOPED_STYLES.md](acceptance/SCOPED_STYLES.md) phase 0.3 compilation/delivery exit
   - Phase 0.6 and later: every completed item in the owning acceptance ledgers has a stable ID,
     named command, and retained evidence artifact; prose checkbox state alone is insufficient.
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

## Cut `v0.4.0` (developer platform)

> **Status:** Published as `v0.4.0` on 2026-08-03. Do not retag.

1. Confirm `check_release_gate.py 0.4.0` and acceptance suites for Explorer/CLI/Plugins/Testing.
2. Confirm latest `main` CI is green on 3.11–3.14 (including MkDocs strict build).
3. Tag and push:

```bash
git tag -a v0.4.0 -m "Hedron 0.4.0"
git push origin v0.4.0
```

4. After publish, update STATUS/README to record publication and point at phase 0.5.

## Cut `v0.5.0` (data application toolkit)

> **Status:** Published as `v0.5.0` on 2026-08-03. Do not retag.

1. Confirm `check_release_gate.py 0.5.0` and acceptance suites for DATA_EDITOR / CACHING.
2. Confirm latest `main` CI is green on 3.11–3.14.
3. Tag and push:

```bash
git tag -a v0.5.0 -m "Hedron 0.5.0"
git push origin v0.5.0
```

4. After publish, update STATUS/README to record publication and point at phase 0.6.

## Close and cut the `v0.6.x` line

Before any 0.7 adapter contract is implemented:

1. Run the phase 0.6 closure gate in the roadmap: interaction/header policy, OOB, fragment-region
   authorization, cache behavior, trusted SVG/chart fallback security, local chart runtimes,
   real-browser lifecycle, and bounded SQLAlchemy queries.
2. Link every completed 0.6 acceptance item to its test command and retained CI artifact.
3. Fix the behavior in a 0.6 maintenance release or mark it experimental in public API and status
   documentation. Do not promote unverified behavior into the portable adapter contract.

## Cut `v0.7.0` (portable adapters and operations)

1. Confirm staged gates 0.7A–0.7F and the adapter, operations, jobs, and observability ledgers.
2. Confirm every advertised adapter is labeled supported, experimental, or deferred; only supported
   adapters count toward the release claim.
3. Run native Flask/Django package and reference-slice tests without FastAPI installed, plus the
   FastAPI multi-worker/proxy/external-cache/job deployment proof.
4. Retain capability-matrix, browser, package, deployment, security, accessibility, and performance
   artifacts under the release evidence bundle.

## Cut `v0.8.0` (feature-freeze baseline)

1. Reject net-new subsystems, adapters, or transports after the freeze.
2. Freeze public API/artifact stability classifications and supported compatibility matrices.
3. Produce the SBOM, vulnerability reports, browser-asset/license inventory, provenance, migration,
   rollback, browser-matrix, performance, security, and accessibility evidence bundle.

## Rehearse and cut `v1.0.0`

1. Publish `1.0.0rc1` (and later `rcN` as required) through the same package pipeline as stable.
2. From published RC artifacts, run clean install, upgrade, complete reference deployment, native
   adapter slices, offline/no-Node, rollback, and acceptance-owner sign-off.
3. Publish `v1.0.0` only when the final RC evidence is green and the stable artifact differs only by
   approved version/release metadata.

## Cut `v0.6.0` (visualization and first-party integrations)

> **Status:** Published as `v0.6.0` on 2026-08-03. Do not retag.

1. Confirm `check_release_gate.py 0.6.0` and acceptance suites for VISUALIZATION / HTMX.
2. Confirm latest `main` CI is green on 3.11–3.14.
3. Tag and push:

```bash
git tag -a v0.6.0 -m "Hedron 0.6.0"
git push origin v0.6.0
```

4. After publish, update STATUS/README to record publication and point at phase 0.7.

## After publication

- Install from a clean venv and re-run the smoke render (and a quick
  `hedron build` against the reference app if convenient).
- Update `docs/STATUS.md` if the published state changed.
- Begin the next phase packet only after the release is confirmed.
