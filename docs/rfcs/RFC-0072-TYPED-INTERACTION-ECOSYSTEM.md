# RFC-0072: Typed interaction ecosystem convergence

**Status:** Accepted<br>
**Target phase:** 0.45 (`v0.45.0`)<br>
**Decision:** D-074<br>
**Planning baseline:** Published `v0.42.0`<br>
**Required predecessor/cut baseline:** Verified `v0.44.0`<br>
**Extends:** RFC-0007, RFC-0014, RFC-0015, RFC-0016, RFC-0019, RFC-0024, RFC-0031,
RFC-0043, RFC-0049, RFC-0060, RFC-0064, RFC-0066, RFC-0070, and RFC-0071<br>
**Forward extension:** RFC-0073 / D-075 (phase 0.46 package-native typed workflows)

## Summary

Phase 0.45 makes the phase 0.43 interaction handles and phase 0.44 type extensions a coherent
whole-ecosystem contract. A registered view or command has one authoritative base descriptor, at
most one fingerprint-bound type extension, and one read-only application catalog entry. First-party
packages consume or project that entry instead of independently inspecting callables, annotations,
routes, forms, effects, or outcomes.

The beginner authoring model does not change. Application authors keep using views, commands,
forms, refreshes, updates, and explicit package APIs. The new catalog and manifest are primarily
integration, build, tooling, conformance, and package-author surfaces.

Phase 0.45 introduces no third schema authority. The catalog is an index over 0.43 descriptors and
0.44 `TypeSchema` extensions. Package projections are namespaced, bounded metadata referencing
their fingerprints. Routing, binding, validation, output authorization, and effect execution stay
on their existing owners.

## Motivation

After 0.44, the flagship can describe a typed interaction completely, but the wider package fleet
could still drift if every adapter or tool reconstructs that description differently. Typical
failure modes would include:

- Jinja or package controls copying route URLs and target ids;
- Explorer, OpenAPI, MCP, and conformance tools deriving different schemas;
- Flask and Django approximating FastAPI behavior without declaring their limitations;
- data, chart, element, and extras packages attaching metadata without a shared namespace or
  invalidation rule;
- build artifacts becoming stale when a handle descriptor or type extension changes;
- deployment tools losing mount-aware interaction URLs; and
- third-party packages having no safe way to add inspection metadata without gaining runtime
  authority.

The ecosystem needs one convergence phase before package-native workflow features are added.

## Goals

- Provide a framework-neutral, read-only `InteractionCatalog` whose entries reference the
  authoritative 0.43 descriptor and optional 0.44 `TypeSchema` fingerprints.
- Provide a versioned, deterministic, redacted `InteractionManifest` for trusted build output,
  deployment checks, static tooling, and portable conformance.
- Define one bounded `PackageProjection` protocol with namespaced metadata, capability labels,
  version checks, size limits, and invalidation rules.
- Assign every first-party package one machine-readable integration disposition:
  `native_consumer`, `projection_adapter`, `compatibility_only`, or `not_applicable`.
- Make FastAPI, Flask, and Django report the same portable interaction facts and honest
  host-specific exceptions.
- Give Explorer, CLI, OpenAPI, Jinja, `AppScenario`, conformance, simulation, notebooks, deployment,
  and package tooling one source of interaction truth.
- Support explicit deny-by-default MCP and Gradio projections without making registration equal
  exposure.
- Preserve optional dependency direction, clean-wheel imports, rollback to 0.44, and existing
  application behavior.
- Freeze the public integration seams required by phase 0.46 without implementing its package
  feature bundles or workflow factories early.

## Non-goals

- A new route registry, renderer, form engine, validation engine, response converter, target
  policy, effect engine, dependency solver, or reactive graph.
- Changing 0.43 generic arity or descriptor authority, or changing 0.44 marker/model semantics.
- Making catalog or manifest data authoritative over live route, security, validation, or output
  policy.
- Automatically exposing registered views or commands through MCP, Gradio, HTTP, plugins, or
  deployment tools.
- Generating package-native CRUD, linked charts, workflow workbenches, or remote-model experiences;
  those are phase 0.46.
- Loading application code, plugins, annotations, or dependencies during static/no-execution
  inspection.
- Moving optional package dependencies into `hedron-core`, requiring Node, or making custom
  elements/live transports mandatory.
- Promoting Experimental features, changing package maturity, closing `SR-021`, or scheduling
  `1.0` merely because a package has a catalog disposition.

## Terminology

| Term | Meaning |
|---|---|
| **Catalog entry** | Read-only index entry referencing one 0.43 base descriptor, its fingerprint, and an optional matching 0.44 type extension. |
| **Interaction catalog** | Sealed application-level collection of catalog entries and package projections; it owns no execution semantics. |
| **Interaction manifest** | Deterministic redacted serialization of a sealed catalog for build, tooling, deployment, and conformance consumers. |
| **Package projection** | Namespaced, versioned, bounded metadata attached by a package to an existing catalog entry or application catalog. |
| **Disposition** | Machine-readable statement that a package is a native consumer, projection adapter, compatibility-only participant, or not applicable. |
| **Trusted dynamic mode** | Explicit mode allowed to import the configured application and seal its live registry. |
| **Static mode** | No-import/no-execution mode that reports only facts derivable from source or an existing manifest and labels unknown facts. |

## Authority hierarchy

The hierarchy is fixed:

1. Phase 0.43 base descriptors own route, method, identity, app ownership, host, target, fallback,
   limits, response conversion, and output authorization.
2. Phase 0.44 `TypeSchema` extensions own opted-in boundary provenance, redaction metadata,
   validation/control descriptions, declared effect constraints, and typed outcome descriptions.
3. Phase 0.45 catalog entries index those artifacts by version and fingerprint.
4. Package projections add namespaced consumer metadata and capability limitations only.

If a catalog, manifest, or projection disagrees with a live authoritative artifact, it is stale.
Development tooling reports and rebuilds it; production or security-sensitive consumers fail
closed. No consumer may merge conflicting facts by preference or recency.

## Catalog lifecycle

Registration remains mutable only during the existing application/plugin registration window.
The catalog then seals with the application registry. A sealed catalog is immutable, deterministic
for equivalent registrations, and safe for concurrent readers.

Each entry records at least:

- stable logical id and kind (`view` or `command`);
- base descriptor version and fingerprint;
- optional type-extension version and fingerprint;
- owning application/registry fingerprint;
- redacted route/method/host/target/fallback capability facts allowed by the base descriptor;
- declared versus dynamic effect-state label;
- package projection keys, versions, fingerprints, capability labels, and limitations; and
- provenance suitable for diagnostics without absolute paths or secret values in public output.

The catalog contains no callbacks, dependency values, request/model instances, credentials,
session data, current field values, arbitrary HTML, or executable expressions.

## Manifest contract

`InteractionManifest` is a canonical serialization of the sealed catalog. It uses a distinct
format version from application/package versions and contains a whole-document fingerprint plus
entry and projection fingerprints. Ordering, canonical JSON, bounds, and forward/backward
compatibility rules are explicit.

Trusted `hedron build` may import the configured application through the documented build entry
point and emit the manifest atomically beside existing build artifacts. Static CLI inspection may
read source or an existing manifest but must not import the target project. The two modes report
their provenance and may not be presented as equivalent when facts are unknown.

Production startup validates a configured manifest against the sealed live catalog when the
manifest is required. Missing or mismatched security-sensitive entries fail before serving.
Optional development manifests may be rebuilt atomically.

## Package projection protocol

A package projection has:

- a reverse-DNS or Hedron-reserved namespace;
- schema version, package identity/version, and provider fingerprint;
- referenced application/catalog/entry fingerprints;
- a declared capability class and limitations;
- bounded JSON-compatible redacted data; and
- an explicit compatibility and cache-invalidation policy.

Projection providers run only in trusted registration/build mode. Static analysis never loads
them. A projection cannot add routes, invoke handlers, weaken CSRF/auth/output policy, change form
validation, execute effects, inject browser code, or expose a handle remotely. Applications can
disable a projection provider without changing the underlying interaction.

## Required ecosystem dispositions

| Package or runtime | Initial disposition | Phase 0.45 obligation |
|---|---|---|
| `hedron-core` | `native_consumer` | Own portable catalog/manifest/projection value types, canonicalization, redaction, limits, and compatibility. |
| `hedron` | `native_consumer` | Compile and seal the catalog; emit build artifacts; expose read-only inspection; integrate FastAPI, CLI, OpenAPI, and scenarios. |
| `hedron-flask`, `hedron-django` | `projection_adapter` | Project the portable subset and machine-readable host exceptions without emulating FastAPI dependency injection. |
| `hedron-explorer` | `native_consumer` | Inspect catalog entries, package provenance, declared/dynamic effects, forms/outcomes, drift, and limitations. |
| `hedron-jinja` | `projection_adapter` | Resolve registered handles/forms from the catalog without copied URLs, ids, or annotation evaluation in templates. |
| `hedron-data`, `hedron-charts`, `hedron-elements`, `hedron-extras` | `projection_adapter` | Attach bounded inspection/control metadata and prove current surfaces can consume handles; package-native workflow features wait for 0.46. |
| `hedron-mcp`, `hedron-gradio` | `projection_adapter` | Support explicit allowlisted projections with separate exposure/egress/auth policy; registration alone exposes nothing. |
| `hedron-conformance` | `native_consumer` | Publish portable catalog, manifest, projection, binding, form, effect, and outcome fixtures. |
| `hedron-sim`, `hedron-notebook` | `projection_adapter` | Preview the supported catalog subset with honest offline/localhost limitations. |
| `hedron-sample-kit` | `projection_adapter` | Demonstrate a third-party-shaped namespaced provider with no privileged access. |
| `hedron-posit`, `hedron-workbench` | `projection_adapter` | Preserve mount-aware URLs/fingerprints and add deployment diagnostics. |
| `fastapi-workbench` | `compatibility_only` | Plain-FastAPI behavior stays generic; smoke the Hedron specialization without importing Hedron. |
| `hedron-native` | `compatibility_only` | Pure-Python semantics remain canonical; any optional canonicalization acceleration proves byte parity. |
| Node/Java conformance evaluators | `compatibility_only` | Validate portable fixture/manifest formats without becoming Hedron application servers. |

No package is required to invent a meaningless public API. Every package must, however, have an
owned disposition, dependency-direction check, and acceptance evidence.

## Developer experience

The planned expert/tooling surface includes:

- `app.interactions` as a read-only catalog view after registration;
- `hedron inspect interactions` with human and versioned JSON output;
- `hedron build` emission of the sealed interaction manifest;
- Explorer application and per-entry interaction panels;
- catalog-aware `AppScenario` lookup and assertions;
- explicit Jinja helpers accepting handles or logical ids, never raw untrusted catalog data; and
- diagnostics for stale fingerprints, unavailable providers, unsupported host capabilities,
  unsafe exposure attempts, and static-mode unknowns.

These names are controlled by the public API contract and may be refined before implementation,
but consumer semantics may not diverge.

## Security and privacy

- The catalog is not an authorization boundary and possession of an id or manifest grants no
  capability.
- Public or production manifests default to the minimum redacted fact set. Development-only source
  metadata is separate and never copied into production artifacts accidentally.
- Projection metadata is untrusted package input and is schema-, depth-, count-, and byte-bounded.
- MCP/Gradio exposure requires a separate explicit policy object and repeats live application
  authorization at invocation.
- Sensitive type fields, defaults, examples, identities, dependency values, credentials, remote
  URLs, and request values do not appear in manifests, diagnostics, snapshots, or traces.
- Manifest signatures are not invented as an authorization mechanism; integrity comes from the
  trusted build/deployment pipeline and verified fingerprints.

## Accessibility and browser behavior

Phase 0.45 adds no new control inventory. Catalog-derived controls and previews must preserve the
0.44 native-form semantics, no-JavaScript paths, error association, focus, announcements, reduced
motion, and existing human-AT claim boundaries. Package projections may describe accessibility
obligations and evidence but cannot claim conformance automatically.

## Compatibility, migration, and rollback

0.45 is additive. Applications that never inspect the catalog behave as in Verified 0.44.
Existing plugin, route, form, region, action, and package APIs remain available. A missing optional
projection provider cannot break the underlying view or command.

Migration is incremental: enable catalog inspection, then package projections, then sealed build
manifests. Rollback removes 0.45 manifests/projections and returns consumers to their 0.44 paths;
base descriptors and type extensions remain valid. Independently versioned satellites publish
explicit compatibility ranges rather than being forced onto a synthetic shared version.

## Resolved questions (D-074)

1. **Is the catalog a new source of runtime truth?** No. It indexes existing authoritative
   descriptor and type-extension artifacts.
2. **Can packages add arbitrary metadata?** No. Projections are namespaced, versioned, bounded,
   redacted, JSON-compatible, and fingerprint-bound.
3. **Does registration expose an MCP tool or Gradio operation?** No. Exposure remains separate,
   explicit, deny-by-default policy.
4. **Must static tooling import the application?** No. Static mode remains no-import/no-execution
   and labels unknown facts.
5. **Does every package need runtime code changes?** No. Every package needs an explicit disposition
   and evidence; compatibility-only and not-applicable are valid.
6. **May 0.45 add package-native workflow factories?** No. It freezes the integration substrate for
   0.46 without pre-implementing those features.
7. **Can a projection change a route, form, effect, or outcome?** No. It can only describe how a
   package consumes the existing contract.
8. **What is the cut baseline?** Verified `v0.44.0`; Published `v0.42.0` remains the planning
   baseline until predecessor phases are implemented and cut.

## Acceptance criteria

- One sealed catalog indexes every registered 0.43/0.44 interaction without duplicating authority.
- One deterministic redacted manifest is consumed by build, tooling, conformance, and deployment
  checks with version/fingerprint mismatch evidence.
- Every first-party package/runtime has an owned machine-readable disposition and passing evidence.
- FastAPI, Flask, and Django agree on the portable facts and expose honest limitations.
- Explorer, CLI, OpenAPI, Jinja, scenarios, conformance, simulation, notebook, and deployment
  projections consume the same catalog contract.
- MCP and Gradio remain deny-by-default and cannot infer exposure from registration.
- Unchanged 0.42–0.44 applications and rollback fixtures pass.
- Every `release-gate-0.45.toml` row is Verified with zero Deferred before `v0.45.0` is cut.

