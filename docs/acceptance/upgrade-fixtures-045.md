# Phase 0.45 interaction ecosystem upgrade fixtures

**Status:** Planned<br>
**Planning baseline:** Published `v0.42.0`<br>
**Required predecessor/cut baseline:** Verified `v0.44.0`<br>
**Target:** `v0.45.0`

These fixtures lock the additive migration from typed interactions to whole-ecosystem catalog and
package projections.

## Unchanged predecessor applications

- Published 0.42 applications with routes/actions/forms/regions/interactions and no 0.43+ opt-in
  run unchanged.
- Verified 0.43 unmodeled handle applications retain fixed arity, structural binding, explicit
  forms, dynamic/observed effects, targets, and response goldens.
- Verified 0.44 modeled applications retain Pydantic validation, generated/overridden forms,
  declared effects, typed outcomes, class/function equivalence, and base/type authority.
- Reading no catalog, loading no provider, and emitting no required manifest changes no request or
  browser behavior.

## Catalog and manifest adoption ladder

1. Inspect the live read-only catalog in development.
2. Enable Explorer/CLI/OpenAPI/AppScenario catalog consumers.
3. Emit a development manifest from trusted build.
4. Add one optional package projection and verify provider disable/removal.
5. Enable a required production manifest and startup validation.
6. Add host/deployment/portable consumers.

At each step, runtime route/form/effect/outcome goldens remain identical.

## Fingerprint and version fixtures

- unchanged app/provider/config produces identical catalog/manifest/projection fingerprints;
- base descriptor change invalidates type/catalog/projection/manifest references transitively;
- type extension change invalidates catalog/projection/manifest but not the base runtime;
- provider config/version change invalidates only its projections and containing manifest;
- unknown optional projection remains inspectable and ignored by unsupported consumers;
- unknown required manifest/catalog version fails with upgrade/regeneration guidance;
- cross-app logical-id/fingerprint reuse fails before execution; and
- static-mode unknowns never become trusted dynamic facts.

## Package disposition fixtures

The whole-fleet inventory proves:

- native consumers read public immutable values only;
- projection adapters install/disable/uninstall cleanly;
- compatibility-only packages gain no Hedron semantic dependency;
- optional package absence cannot break base interactions;
- older compatible package versions report bounded limitations;
- Experimental capability remains labeled Experimental; and
- independently versioned satellites retain valid compatibility ranges.

## Host, authoring, remote, and deployment fixtures

- FastAPI/Flask/Django portable catalog goldens plus declared host differences;
- Jinja registered handles/forms versus existing explicit template paths;
- Explorer/CLI/OpenAPI/scenario outputs in trusted/static/manifest-only modes;
- MCP/Gradio registration without exposure, then explicit exposure with authz denial/success;
- sim/notebook/sample-kit/Node/Java portable subset and refusal cases;
- Posit Workbench/Connect/ordinary ASGI mount and external-base behavior; and
- corrupt/stale/missing manifest, read-only filesystem, multi-worker, rolling deploy, and atomic
  previous-artifact rollback.

## Rollback to 0.44

- Remove/ignore `interactions.json` and package projections.
- Disable catalog-only Explorer/CLI/Jinja/package features.
- Preserve 0.43 base descriptors, 0.44 type extensions, routes, forms, effects, outcomes, and
  package direct APIs.
- Verify no orphan provider caches, assets, routes, registry entries, startup requirements, or
  remote exposure remains.

## Evidence retained

- canonical manifest/catalog/projection goldens and JSON Schemas;
- descriptor/type/catalog/projection fingerprint transition matrix;
- whole-fleet disposition and clean-install reports;
- cross-host/tooling/portable/deployment/remote fixtures;
- redaction/adversarial/performance/browser evidence; and
- forward fixture proving a test-only 0.46 `FeatureBundle` can reference public catalog/projection
  seams without gaining execution authority or changing 0.45 behavior.

