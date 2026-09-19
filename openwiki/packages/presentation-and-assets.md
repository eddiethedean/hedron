---
type: reference
title: Presentation, Charts, Maps, and Assets
description: How presentation packages compile bounded specs into browser plans, accessible fallbacks, and policy-checked assets.
tags:
  - charts
  - maps
  - assets
  - accessibility
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T17:40:19.225Z
sources:
  - id: openwiki-source-b0527fa09268dca7f9912b57
    resource: repo://packages/hedron-charts/src/hedron_charts/compile.py
  - id: openwiki-source-3f4d9abeec9be1824aac3043
    resource: repo://packages/hedron-charts/src/hedron_charts/components.py
  - id: openwiki-source-5f22118de9d96ece52ba1862
    resource: repo://packages/hedron-charts/src/hedron_charts/element.py
  - id: openwiki-source-2b33f260c98e8f0e600045d7
    resource: repo://packages/hedron-charts/src/hedron_charts/optional_adapters.py
  - id: openwiki-source-526d4b6b7c36aa47b6ca4565
    resource: repo://packages/hedron-elements/src/hedron_elements/assets.py
  - id: openwiki-source-3af3ba07d3e92f5178158536
    resource: repo://packages/hedron-elements/src/hedron_elements/composition.py
  - id: openwiki-source-2abb435df43c01e7eecf8ae7
    resource: repo://packages/hedron-maps/src/hedron_maps/compile.py
  - id: openwiki-source-a6803035b307cc1917ed247e
    resource: repo://packages/hedron-maps/src/hedron_maps/element.py
  - id: openwiki-source-590678b5f203c87b816d8d02
    resource: repo://tests/security/test_chart_svg_corpus.py
  - id: openwiki-source-f0b6c07ca620cab28514d157
    resource: repo://tests/unit/test_charts_038_regress.py
  - id: openwiki-source-c114952d92fa063a69fba5c9
    resource: repo://tests/unit/test_elements_037_gesture_catalog.py
generated: { by: "codex", at: "2026-09-19T16:47:17.741Z" }
---

# Presentation, Charts, Maps, and Assets

Hedron's presentation packages keep Python authoring separate from browser
execution. A chart or map is first parsed into a typed, bounded plan. The
component then serializes that plan into a custom element payload, includes
server-rendered fallback content, and declares the static browser assets needed
to enhance it. This gives framework adapters one render contract while keeping
limits, accessibility, URL policy, and security decisions on the server.

## Charts

`hedron-charts.compile_chart()` parses a versioned `ChartSpec` and rejects
unknown fields, non-finite JSON, and prototype-pollution keys before validating
marks, scales, and transforms. It bounds rows, fields, transforms, facets,
marks, labels, payload bytes, and export dimensions. Transforms run before
domains and mark records are built, and sensitive row values pass through the
shared redaction authority before entering the plan.

The compiler infers missing scales from encodings, records warnings such as a
bar chart with a non-zero baseline, and chooses semantic SVG below the locked
2,500-mark threshold or Canvas when the author requests it or the mark count
reaches the threshold. The resulting `ChartPlan` carries deterministic spec
and data fingerprints, renderer choice, guides, theme tokens, interaction
definitions, limits, assets, and an accessibility plan with a summary and
optional table rows.

The first-party `Chart` component puts the plan in a `hedron-chart` element.
Its fallback includes a reviewed static SVG, a text summary, and either an
accessible table or bounded CSV text. The browser module can enhance that
payload, but a server-rendered page remains meaningful when JavaScript is
unavailable. Optional Matplotlib, Plotly, and Altair adapters compile through
the same accessibility and export boundary rather than bypassing it.

## Maps

`hedron-maps.compile_map()` is also a no-I/O compiler. It requires a useful
title and description for non-decorative maps, validates zoom and layer/source
limits, sanitizes GeoJSON and markers, and closes the resource graph for
basemap, tile, sprite, glyph, and style URLs. Remote origins must be HTTPS and
must satisfy `MapPolicy`; unsafe schemes, credentials, protocol-relative URLs,
unapproved origins, forbidden style keys, oversized styles/TileJSON, and
excessive coordinate or feature counts fail closed.

The resulting `MapPlan` pins the MapLibre browser engine and a CSP-oriented
worker/asset policy, records origins and attribution, and includes an
accessibility fallback with ordinary links and buttons. The first-party `Map`
component additionally checks tile templates against explicit allowlists and
traversal rules, serializes the plan into `hedron-map`, and carries the active
CSRF cookie/header names plus any registered interaction endpoints in the
element attributes.

## Browser composition and packaged assets

`hedron-elements` supplies typed browser composition edges and traces. Edges
validate stable identifiers, bound nesting depth and payload bytes, declare
server authorization and concurrency behavior, and choose a native/form/link/
fragment fallback. Browser traces contain correlation and diagnostic metadata,
not content-bearing payload or query fields, and are capped at 4 KiB. Packaged
asset lookup accepts only a single safe basename under the package's static
directory, so zip-import and filesystem paths cannot escape the distribution.

Chart SVG, map URL/style, component ABI, accessibility, and interaction tests
exercise these boundaries. See [Rendering and Component Model](../architecture/rendering-and-components.md)
for the shared component pipeline and [Requests and Interactions](../architecture/requests-and-interactions.md)
for how browser events re-enter the host request lifecycle.
