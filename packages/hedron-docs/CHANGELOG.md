# Changelog

## [0.5.0]

- W5: replaced the proving app's bespoke chrome with Hedron AppShell, Brand, and SkipLink.
- Added responsive no-JavaScript mobile navigation, accessible current-page state, release banners,
  and a persisted light/dark/system color-mode control.
- Rendered 404 responses through the same compile-safe shell and corrected document head markup.

## [0.4.0]

- W4: versioned content manifest, normalized navigation, validated internal links, and manifest-only routing.

## [0.3.0]

- Lowered all W3 content constructs through native Hedron primitives with no opaque document body.
- Added stable heading aliases, fragment-target anchors, responsive code/table containers, language
  labels, and native clipboard-copy controls without inline scripts.
- Added package-owned docs CSS served as an immutable, CSP-safe asset.
- Promoted the configuration and manifest contracts to schema 3; this is an intentional clean break
  from the 0.2 compiler line.

## [0.2.0]

- Replaced HTML round-tripping with direct token-to-AST lowering and stable source spans.
- Added explicit footnote, definition-list, details, API-directive, and demo-directive nodes.
- Added source, nesting, node, table-cell, code-block, and directive budgets.
- Versioned the native configuration schema and added bounded navigation import from MkDocs.
- Expanded diagnostics with stable titles, explanations, ranges, and remediations.

## [0.1.0]

- Initial experimental Markdown-to-Hedron compiler, deterministic manifest, CLI, search, and app
  factory.
- Added ordered inline lowering, unique heading anchors, jailed source discovery, compile-time URL
  validation, fingerprinted manifest assets, valid sitemap/canonical metadata, and a deployable
  proving application.
