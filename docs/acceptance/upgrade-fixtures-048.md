# Phase 0.48 upgrade and rollback fixtures

**Status:** Planned; Stage 0 contract refined by D-083 against Published in-tree `v0.47.0`<br>
**From:** Verified `v0.47.0`<br>
**To:** `v0.48.0`

Required fixtures:

1. An unchanged 0.47 PAGE application that never sets `htmx_extensions` still receives the
   pinned `sse` and `head-support` assets after HTMX core, keeps existing HTMX/OOB/
   `InteractionResult` behavior, and surfaces a bounded compatibility-injection diagnostic.
2. The same application passes `htmx_extensions=()` (or `ExtensionSet.empty()`) and loads
   zero HTMX extension bytes; core HTMX, forms, fragments, and polling remain unchanged.
3. An application declares `{"sse"}` only: head-support is absent, SSE assets and `hx-ext`
   activate, and `job_status_sse_response` plus polling fallback remain equivalent.
4. A registered head-support page merges admitted `AssetRef` values across boosted and
   full-document navigation; an undeclared fragment cannot introduce executable head
   content; rollback restores the previous head.
5. Explicit GET preload on a cacheable same-origin link maps to `HX-Preloaded` / the
   existing `decide_preload` path; POST, user-derived URLs, and undeclared inherited
   preload stay ordinary non-preloaded interactions.
6. Low-level `hx-ext="sse"` HDJ markup continues to require `ExtensionEvidence` with
   `extension_id="sse"` (`HED-JINJA-0030`); writing `hx-ext` alone still never installs.
7. Removing every 0.48 declaration, SseRegion, and preload authoring value restores the
   0.47 compatibility default and leaves no morph/preload assets, routes, or Supported
   morph claim.
8. Flask/Django/Posit/Workbench adapters with mount prefixes serve the same declared
   local assets or opt-out absence; no FastAPI types leak into portable models.
9. `hedron-chart` and `hedron-map` swap/dispose paths remain unchanged when morph is
   Deferred/excluded; if morph is admitted, the spike fixture covers both hosts plus
   `hedron-example`, forms, focus, OOB, and three engines.
10. Version skew, missing vendored extension files, digest mismatch, CSP denial, and
    unknown public ids fail closed with documented diagnostics and no silent CDN fetch.
