# Security review brief — phase 0.38 high-fidelity charts

**Cut targets:** Hedron `v0.38.0`; `hedron-charts` `0.2.0`  
**Owning RFC / decision:** RFC-0069 / D-066  
**Primary gates:** `GRAMMAR-038`, `RENDER-038`, `INTERACT-038`, `EXPORT-038`, `SECURITY-038`,
`PKG-038`

## Review scope

- `ChartSpec` parsing, JSON/schema versioning, field resolution, safe transform operator catalog,
  recursion, prototype-pollution keys, deterministic normalization, and diagnostic redaction.
- Row/field/string/transform/facet/mark/label/payload/event/export/worker allocation bounds,
  including rejection timing before expensive DOM/Canvas work.
- D3 module selection and build pipeline, lockfile, generated bundle/source maps, dependency
  confusion, tamper detection, reproducibility, licenses, SBOM, and provenance.
- SVG/Canvas paint, text/tooltip/annotation escaping, URL/data/asset policy, active SVG, CSS tokens,
  locale/timezone strings, export metadata, and print paths.
- `hedron-chart` custom-element registration/version skew, structured data, lifecycle, HTMX swaps,
  history, ResizeObserver/IntersectionObserver, timers/listeners/workers/object URLs, and failure
  fallback.
- Typed chart events, stable datum identities, event coalescing, cross-filter/drill actions,
  authz/CSRF boundaries, late responses, and diagnostics/telemetry redaction.
- SVG/PNG/CSV/JSON export authorization, formula injection, dimensions/memory bombs, remote fetches,
  secret fields, tenant boundaries, and cache variation.
- Strict CSP and Trusted Types without callback/eval/inline-script escape hatches.

## Required adversarial cases

1. `__proto__`, `constructor`, deeply nested specs, circular-like references, huge numeric domains,
   invalid Unicode/bidi text, NaN/infinity, timezone ambiguity, and transform explosions.
2. Script/event-handler/foreignObject/URL/CSS injection through labels, annotations, tooltips,
   themes, exports, schema metadata, and vendor migration inputs.
3. Excessive marks/facets/labels/exports, rapid pointer events, resize loops, repeated swaps,
   disconnect during render/export, stale async callbacks, and worker cancellation.
4. Forged selection/drill payloads, stale row identities, cross-tenant cached plans/exports, CSRF
   omission, and treating browser selection as authorization.
5. Stale/new asset mixtures, duplicate custom-element definitions, modified runtime bundles,
   missing source maps/licenses, offline installs, and rollback cache behavior.

## Out of scope

- General D3 user code or raw JavaScript callbacks: these are prohibited, not reviewed as a public
  extension surface.
- Vendor adapter internals beyond the boundary required to keep them explicit Experimental paths.
- Maps, arbitrary network/hierarchy/3D/WebGL engines unless separately proposed and gated.
- Production-grade graduation of the whole Web Component platform (phase 0.42).
- Application data authorization, business rules, or correctness of author-written analytical
  conclusions.

## Required cut artifacts

- `REDACTED_REPORT.md` with findings, severity, affected gates, remediation, and residual risk.
- `DISPOSITION.toml` proving no unresolved critical/high finding.
- dependency/build review, reproducible bundle report, license/SBOM/provenance references.
- fuzz/property/adversarial suite output and retained browser lifecycle/export artifacts.

## Stage 0 status

Brief only. It is not security evidence and does not authorize a Supported claim.
