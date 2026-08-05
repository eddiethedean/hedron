# Scripts

Maintainer and contributor utilities for the Hedron monorepo. Prefer documenting new
scripts here when you add them.

## Everyday contributor

| Script | When to run |
|---|---|
| `mkdocs.sh` | Docs preview / build wrapper (`./scripts/mkdocs.sh serve`) |
| `generate_component_docs.py` | After changing the component docs manifest; `--check` in CI/PR |
| `sync_status_roadmap.py` | After editing `docs/STATUS.md` or `docs/ROADMAP.md` (updates root mirrors). CI: `--check` |

## Release / gate (maintainers)

| Script | Role |
|---|---|
| `check_release_gate.py` | Gate TOML vs claimed version (`0.10.1`, `0.11.0`, …) |
| `rehearse_release.py` | Clean install rehearsal before tagging |
| `build_evidence_bundle.py` | Collect release evidence artifacts |
| `verify_pkg_13.py` / `verify_pkg_12.py` / `verify_pkg_11.py` / `verify_pkg_10.py` / `verify_pkg_09.py` | Phase-tied package verify helpers |
| `generate_sbom.py` | SBOM generation |
| `license_inventory.py` | License inventory |
| `dep_audit.py` | Dependency audit |
| `asset_audit.py` | Packaged asset audit |
| `release_notes.py` | Release notes helper |
| `check_stability_inventory.py` | Stability catalog checks |
| `check_hdn_removed.py` | Guard against HDN resurfacing |
| Live-claim honesty | `tests/conformance/test_live_claim_honesty.py` (phrases in `hedron.live_claims`) |

Release-only scripts are **not** required for ordinary docs or bugfix PRs. See
[RELEASE.md](../docs/RELEASE.md) and [CONTRIBUTING.md](../docs/CONTRIBUTING.md).
