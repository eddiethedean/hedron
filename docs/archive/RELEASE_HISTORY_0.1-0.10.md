# Historical release cuts (v0.1.0–v0.10.0)

> Archived. Living runbook: [RELEASE.md](../RELEASE.md).

# Cutting a Hedron release

Hedron uses a coordinated release train. The Git tag includes a leading `v`
(for example `v0.3.0`); Python package metadata omits it (`0.3.0`).

## Preconditions

1. `main` is green on CI for Python 3.11–3.14.
2. Package version, `__version__`, and changelog entry agree
   (`uv run python scripts/check_release_gate.py 0.4.0`).
3. Phase acceptance subsets for the release are checked (or explicitly Deferred):
   - [SECURITY.md](../acceptance/SECURITY.md) phase 0.2 + 0.3 asset URL policy + 0.4 SARIF
   - [FASTAPI_INTEGRATION.md](../acceptance/FASTAPI_INTEGRATION.md) MVP exit
   - [HTMX.md](../acceptance/HTMX.md) phase 0.2
   - [EXPLORER.md](../acceptance/EXPLORER.md) phase 0.4
   - [CLI.md](../acceptance/CLI.md) phase 0.4
   - [PLUGINS.md](../acceptance/PLUGINS.md) phase 0.4
   - [TESTING.md](../acceptance/TESTING.md) phase 0.4
   - [COMPONENT_MODEL.md](../acceptance/COMPONENT_MODEL.md) FastAPI component-model evidence
   - [JINJA.md](../acceptance/JINJA.md) phase 0.9 replacement and removal gate
   - [SCOPED_STYLES.md](../acceptance/SCOPED_STYLES.md) phase 0.3 compilation/delivery exit
   - Phase 0.6 and later: every completed item in the owning acceptance ledgers has a stable ID,
     named command, and retained evidence artifact; prose checkbox state alone is insufficient.
4. **License (D-033):** a root `LICENSE` file exists and every publishable
   package declares `[project].license` / `license-files`. The release workflow
   refuses to publish without this.
5. `PYPI_API_TOKEN` is configured in GitHub Actions secrets (already required by
   `.github/workflows/release.yml`).
6. **PyPI name:** the `hedron` project on PyPI is this FastAPI framework train
   (reclaimed at `0.2.0`). Keep the project description aligned after each publish.

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

> **Status:** Published as `v0.7.0`. Do not retag.

## Cut `v0.8.0` (hardening and compatibility baseline)

> **Status:** Published as `v0.8.0`. Do not retag.

1. Confirm phase 0.8 scope: hardening/classification only; no net-new subsystem, adapter, or transport.
2. Confirm `uv run python scripts/check_release_gate.py 0.8.0` and
   [release-gate-0.8.toml](../acceptance/release-gate-0.8.toml) (`Verified` or owned `Deferred`).
3. Confirm stability catalog ([api/STABILITY.md](../api/STABILITY.md)), compatibility/deprecation
   policy, upgrade guide, SBOM/license/asset audits, three-engine browser matrix, and performance
   budget enforcement are green.
4. Confirm CI green on Python 3.11–3.14 including adapter, ops, and browser (Chromium/Firefox/WebKit)
   suites.
5. Finalize per-package `CHANGELOG.md` `[0.8.0]` sections; sync versions/`__version__`.
6. Tag and push:

```bash
git tag -a v0.8.0 -m "Hedron 0.8.0"
git push origin v0.8.0
```

7. After publish, update STATUS/README to record publication and point at phase 0.9.
   Retain the evidence bundle (SBOM, licenses, asset audit, test summaries, lockfile digest).

## Build and cut `v0.9.0`

> **Status:** Published as `v0.9.0`. Do not retag.

1. Confirm phase 0.9 owning RFC revisions and API/implementation/acceptance contracts are accepted
   before implementation is claimed complete.
2. During development, validate the planned evidence shape with
   `uv run python scripts/check_release_gate.py 0.9.0 --allow-planned` after synchronizing package
   versions and changelogs on the release branch.
3. Close [RELEASE_0_9.md](../acceptance/RELEASE_0_9.md): complete HDN removal, `.hdj` format/profile
   conformance, HDJ's standards-first HTML/CSS/JS/Jinja/HTMX surface, Hedron feature parity,
   dynamic trust and CSP capability
   boundaries, metadata preservation, manual upgrade, package isolation, and artifact evidence.
4. Replace every Planned row in
   [release-gate-0.9.toml](../acceptance/release-gate-0.9.toml) with `Verified` evidence or an explicitly
   owned `Deferred` disposition. The strict gate must pass before publication:
   `uv run python scripts/check_release_gate.py 0.9.0`.
5. Build the coordinated artifacts once through the trusted workflow. From those artifacts, run
   `scripts/rehearse_release.py`, the manual 0.8→0.9 authoring upgrade fixture, rollback,
   documentation examples, supported Python/Jinja matrices, and the supply-chain bundle.
6. Tag and publish `v0.9.0`; retain exact source tag, artifact hashes, commands, matrix dimensions,
   logs, SBOM, licenses, provenance, migration proof, and owner approvals. Never retag or overwrite
   a published artifact.
7. Immediately verify public-index installation and hashes. If an artifact is wrong, yank it when
   appropriate, publish the disposition, and prepare the next valid patch release.

## Build and cut `v0.10.0`

> **Status:** Published as `v0.10.0`. Do not retag.

1. Confirm phase 0.10 owning RFC-0032 and revised RFCs 0009/0013/0021/0025/0031 are accepted
   before implementation is claimed complete.
2. During development, validate the planned evidence shape with
   `uv run python scripts/check_release_gate.py 0.10.0 --allow-planned` after synchronizing package
   versions and changelogs on the release branch.
3. Close [RELEASE_0_10.md](../acceptance/RELEASE_0_10.md): SSE, focused streaming, WebSocket channels,
   Chat/Dialog, media chunk transport, HDJ head/streaming, navigation preload, and three-engine
   evidence.
4. Replace every Planned row in
   [release-gate-0.10.toml](../acceptance/release-gate-0.10.toml) with `Verified` evidence or an
   explicitly owned `Deferred` disposition. The strict gate must pass before publication:
   `uv run python scripts/check_release_gate.py 0.10.0`.
5. Build the coordinated artifacts once through the trusted workflow. From those artifacts, run
   `scripts/rehearse_release.py`, browser/load matrices, documentation examples, and the
   supply-chain bundle.
6. Tag and publish `v0.10.0`; retain exact source tag, artifact hashes, commands, matrix dimensions,
   logs, SBOM, licenses, provenance, migration proof, and owner approvals. Never retag or overwrite
   a published artifact.
7. Immediately verify public-index installation and hashes. If an artifact is wrong, yank it when
   appropriate, publish the disposition, and prepare the next valid patch release.

## Cut `v0.6.0` (visualization and first-party integrations)

> **Status:** Published as `v0.6.0`. Do not retag.

1. Confirm `check_release_gate.py 0.6.0`, [release-gate-0.6.toml](../acceptance/release-gate-0.6.toml),
   and acceptance suites for VISUALIZATION / HTMX / SECURITY (closure IDs Verified or Deferred).
2. Confirm latest `main` CI is green on 3.11–3.14 (including browser job when present).
3. Tag and push:

```bash
git tag -a v0.6.0 -m "Hedron 0.6.0"
git push origin v0.6.0
```

4. After publish, update STATUS/README to record publication and point at phase 0.7.

## After publication

- Install from a clean venv and re-run the smoke render (and a quick
  `hedron build` against the reference app if convenient).
- Keep `docs/STATUS.md` / root `STATUS.md` aligned with the published train.
- After `v0.10.0`, begin the **0.11** phase packet (native Flask/Django depth).
