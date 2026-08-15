# Phase 0.46 package workflow upgrade fixtures

**Status:** Planned<br>
**Planning baseline:** Published `v0.42.0`<br>
**Required predecessor/cut baseline:** Verified `v0.45.0`<br>
**Target:** `v0.46.0`

These fixtures prove package-native features are optional compositions over the Verified 0.45
ecosystem, not a new runtime or irreversible application format.

## Unchanged predecessor applications

- Published 0.42 and Verified 0.43–0.45 applications run unchanged with no bundle inclusion.
- Existing direct DataTable/DataEditor, ChartSpec/chart component, element, extras, MCP, Gradio,
  Jinja, Explorer, notebook, sim, adapter, and deployment APIs retain their behavior.
- Descriptor/type/catalog/projection/manifest fingerprints remain authoritative and unchanged by
  mere installation of 0.46-capable packages.
- Packages absent or installed without feature registration add no routes, assets, projections, or
  request-path cost.

## Incremental adoption fixtures

1. Include a sample feature bundle with one view/command/scenario/projection.
2. Adopt `DataWorkspace` list/detail with mutation disabled.
3. Add create/edit policies and explicit outcome/form overrides.
4. Add a typed chart selection linked through an explicit command/effect.
5. Enable one Supported enhanced element mapping with native fallback.
6. Enable Explorer/Jinja/notebook/sim workbench consumers.
7. Explicitly expose one read-only MCP resource, then one confirmed mutation tool.
8. Add one allowlisted Gradio remote workflow with local models and mocked/real-service evidence.

Each step can be removed independently and compares against equivalent explicit 0.45 code.

## Atomic inclusion and ejection fixtures

- duplicate route/id/component/asset/projection and missing capability fail before any mutation;
- cyclic/deep/skewed bundle dependencies fail deterministically;
- provider exception/cancellation leaves no partial artifact/cache/background resource;
- eject produces reviewable explicit configuration/handles/components/scenarios without secrets or
  overwritten user files; and
- disable/uninstall/rollback removes every bundle-owned artifact while retaining unrelated
  catalog/package state.

## Data, chart, and element fixtures

- explicit authorized sync/async source and mutation policy versus missing/denied policy;
- list/detail/create/edit query/form/outcome/conflict/optimistic/override/no-JS paths;
- delete/bulk/nested/unsupported shapes refused unless supplied as explicit app commands;
- chart selection/filter/drill-down/export event validation, cycle/fan-out/rate/payload/race bounds;
- keyboard/tabular chart alternatives and full-fragment fallback; and
- native/enhanced/failed-upgrade/CSP/no-JS control encoding, errors, focus, async state, swap cleanup.

## Remote and workbench fixtures

- bundle/catalog presence with zero MCP/Gradio exposure;
- explicit remote policy authz denial/success, confirmation, bounds, output/effect mapping, audit;
- Gradio endpoint/schema drift, outage, timeout, cancel, file cleanup, partial/progress/job state;
- Explorer outcome/effect/cost/limitation views and safe generated Python/tests;
- Jinja registered feature rendering, notebook loopback, sim offline subset/refusal; and
- static tooling performs no bundle/provider/remote execution.

## Host, package, and deployment fixtures

- FastAPI/Flask/Django portable feature equivalence and declared limitations;
- ordinary ASGI/WSGI plus Posit Workbench/Connect mount/assets/catalog behavior;
- clean wheels with each optional package absent/present/skewed;
- independently versioned package compatibility and maturity labels; and
- rolling deployment with old/new app/package/manifest combinations that are documented compatible.

## Rollback to 0.45

- Remove bundle inclusions and remote exposure registrations.
- Use ejected or pre-existing explicit views/commands/components/package APIs.
- Preserve the 0.45 catalog/manifest/projections and all 0.43/0.44 runtime/type behavior.
- Verify no bundle-owned routes/assets/components/scenarios/projections/caches/jobs/listeners/history
  or remote operations remain.

## Evidence retained

- bundle/config/artifact/fingerprint/ejection goldens;
- explicit-versus-bundle behavior and performance matrix;
- data/chart/element/remote/workbench/scenario/adapter fixtures;
- security/a11y/browser/fuzz/real-service/deployment reports;
- whole-fleet clean-install/version/rollback inventory; and
- full rollback goldens from 0.46 to 0.45.

