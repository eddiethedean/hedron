# Scripts

Maintainer and contributor utilities for the Hedron monorepo. Prefer documenting new
scripts here when you add them.

## Everyday contributor

| Script | When to run |
|---|---|
| `ci_checks.sh` | **Shared CI suites** used by `.github/workflows/ci.yml` and `release.yml`. Local: `bash scripts/ci_checks.sh test\|workbench\|quality\|browser\|evidence\|packaging\|all` — `all` mirrors the full workflow. Independent checks inside a suite overlap. `--jobs N` or `HEDRON_CHECK_JOBS` caps concurrency (see `ci_checks.sh --help`) |
| `mkdocs.sh` | Docs preview / build wrapper (`./scripts/mkdocs.sh serve`) |
| `smoke_workbench_adapter_docker.sh` | License-independent Linux smoke for mounted Workbench adapter behavior |
| `generate_component_docs.py` | After changing the component docs manifest; `--check` in CI/PR |
| `generate_sim_demos.py` | After editing `docs/demos/*.py`; regenerates sim HTML and syncs Demo/Code tabs (`--check`) |
| `sync_demo_code_tabs.py` | Refresh guide Demo/Code tabs from `docs/demos/runnable/` (also run via `generate_sim_demos.py`) |
| `sync_status_roadmap.py` | After editing `docs/STATUS.md` (updates root `STATUS.md`; forbids extra roadmap files). CI: `--check` |
| `check_docs_train_ssot.py` | Fail on stale tip claims vs `docs/release.toml`, unsafe pins, or charts/sample-kit installs missing the published compatibility floors. CI: quality job |
| `check_package_docs_inventory.py` | Keep the package catalog, README maturity labels, PyPI classifiers, and package pages aligned with the living fleet inventory. CI: quality job |
| `check_documentation_ownership.py` | Require an owner and review cadence for every published Markdown page. CI: quality job |
| `check_api_docs_coverage.py` | Require every `hedron.__all__` and `hedron_charts.__all__` export in public API reference. CI: quality job |
| `check_package_readme_links.py` | Reject relative links that break when package READMEs render on PyPI. CI: quality job |
| `check_public_doc_links.py` | Reject missing public links and relative links into files excluded from MkDocs. CI: quality job |
| `check_changelog_structure.py` | Require one package changelog title, a current-version section, and non-empty release sections. CI: quality job |
| `check_external_links.py` | Check public HTTP links. Runs weekly in `docs-health.yml` to avoid network flakes on ordinary PRs |
| `check_recipe_code_sync.py` | Fail when a guide's recipe Code tab drifts from its marked runnable source. CI: quality job |

Documentation source ownership and review rules:
[Documentation standards](../docs/guides/documentation-standards.md).


## Release / gate (maintainers)

| Script | Role |
|---|---|
| `check_release_gate.py` | Gate TOML vs claimed version (`0.10.1`, `0.11.0`, …) |
| `check_human_at_packet.py` | Phase **0.21** human AT protocol/schema/ledger packet (D-052). Without flags: engineering packet OK. Pass `--require-sessions` only when flipping SR/PARTICIPANT/ARTIFACT/REMEDIATE to Verified after real sessions. |
| `verify_pkg_21.py` | Phase **0.21** historical packet verify (human AT engineering cut) |
| `verify_pkg_22.py` | Phase **0.22** CSRF packet + focused security tests (`check_release_gate.py 0.22.0`) |
| `verify_pkg_23.py` | Phase **0.23** historical packet + facade/tier checks (`check_release_gate.py 0.23.0`) |
| `verify_pkg_24.py` | Phase **0.24** historical packet + live disposition (`check_release_gate.py 0.24.0`) |
| `verify_pkg_25.py` | Phase **0.25** historical packet + archetype / landmines (`check_release_gate.py 0.25.0`) |
| `verify_pkg_26.py` | Phase **0.26** living-train packet + production-grade graduation (`check_release_gate.py 0.26.0`) |
| `verify_pkg_27.py` | Phase **0.27** satellite graduation packet (`check_release_gate.py 0.27.0`) |
| `verify_pkg_28.py` | Phase **0.28** charts/native graduation packet (`check_release_gate.py 0.28.2`) |
| `verify_pkg_29.py` | Phase **0.29** Posit Workbench adapter packet |
| `verify_pkg_30.py` | Phase **0.30** standalone `fastapi-workbench` extraction packet |
| `verify_pkg_31.py` | Phase **0.31** tooling and portable-conformance packet |
| `verify_pkg_32.py` | Phase **0.32** production-grade MCP packet |
| `verify_pkg_33.py` | Phase **0.33** unified Posit deployment adapter packet |
| `verify_pkg_34.py` | Phase **0.34** production-grade Gradio packet |
| `verify_pkg_35.py` | Phase **0.35** whole-fleet closure packet |
| `verify_pkg_36.py` | Phase **0.36** Web Component ABI/lifecycle packet |
| `verify_pkg_37.py` | Phase **0.37** form/primitives packet (Published `v0.37.0`) |
| `verify_pkg_40.py` | Phase **0.40** authoring / React migration packet (Published `v0.40.0`) |
| `verify_pkg_41.py` | Phase **0.41** composition / state / navigation packet (Published `v0.41.0`) |
| `verify_pkg_43.py` | Phase **0.43** historical refreshable-views packet (Published `v0.43.0`) |
| `verify_pkg_44.py` | Phase **0.44** type-driven authoring packet (Published `v0.44.0`; omit `--allow-planned` after cut) |
| `verify_pkg_45.py` | Phase **0.45** typed interaction ecosystem packet (Published `v0.45.0`; omit `--allow-planned` after cut) |
| `verify_pkg_46.py` | Phase **0.46** package-native typed workflows packet (Published `v0.46.0`; historical after 0.47) |
| `verify_pkg_47.py` | Phase **0.47** first-class maps packet (Published in-tree `v0.47.0`; omit `--allow-planned` after cut) |
| `verify_pkg_48.py` | Phase **0.48** HTMX extension integration packet (Published in-tree `v0.48.0`; omit `--allow-planned` after cut) |
| `verify_pkg_49.py` | Phase **0.49** FastAPI/Pydantic Stage 0 packet (keep `--allow-planned`; D-084; no 0.49 runtime) |
| `verify_pkg_42.py` | Phase **0.42** production-grade Web Component platform packet (Published `v0.42.0`) |
| `check_*_042.py` | Phase 0.42 stable/compat/review/at/perf/supply/regress gate entry points |
| `verify_pkg_39.py` | Phase **0.39** rich data / OptimisticMutation packet (Published `v0.39.0`) |
| `verify_pkg_38.py` | Phase **0.38** high-fidelity charts packet (Published `v0.38.0` / `hedron-charts` `0.2.0`) |
| `check_*_038.py` | Phase 0.38 grammar/render/design/visual/interaction/a11y/perf/export/security/compat/docs/regression gate entry points |
| `check_contract_027.py` | Satellite production-grade inventory / install guards |
| `check_data_027.py` | `DATA-027` bounded data evidence |
| `check_flask_027.py` | `FLASK-027` host-only Flask evidence |
| `check_django_027.py` | `DJANGO-027` host-only Django evidence |
| `check_hdj_027.py` | `HDJ-027` versioned HDJ evidence |
| `check_extras_027.py` | `EXTRAS-027` curated extras + quarantine |
| `check_parity_027.py` | `PARITY-027` portable host parity + REVIEW-027 |
| `check_contract_026.py` | `CONTRACT-026` production-grade inventory |
| `check_core_026.py` | `CORE-026` upgrade fixtures |
| `check_fastapi_026.py` | `FASTAPI-026` ops smoke |
| `check_explorer_026.py` | `EXPLORER-026` secured Explorer evidence |
| `check_review_026.py` | `REVIEW-026` security review packet |
| `check_archetype_025.py` | `ARCHETYPE-025` production archetype SSOT |
| `check_budget_025.py` | `BUDGET-025` critical-path workloads |
| `check_extras_025.py` | `EXTRAS-025` quarantine XOR |
| `check_charts_025.py` | `CHARTS-025` Matplotlib-default + Plotly/Altair honesty |
| `check_supply_025.py` | `SUPPLY-025` RELEASE SBOM/evidence-bundle attach requirement |
| `rehearse_release.py` | Clean install rehearsal before tagging |
| `build_evidence_bundle.py` | Collect release evidence artifacts |
| `write_release_manifest.py` | Record SHA-256 digests and sizes for every release asset |
| `verify_release_manifest.py` | Verify local/downloaded assets against `release-manifest.json` |
| `check_published_quickstart.py` | Install an exact PyPI version, scaffold an app, and import it before GitHub Release creation |
| `verify_pkg_46.py` / `verify_pkg_45.py` / `verify_pkg_44.py` / `verify_pkg_43.py` / … / `verify_pkg_10.py` | Phase-tied package verify helpers (living tip cut: **`verify_pkg_48.py`**; `verify_pkg_49.py --allow-planned` is the 0.49 Stage 0 packet; `verify_pkg_47.py` remains the historical 0.47 packet) |
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
