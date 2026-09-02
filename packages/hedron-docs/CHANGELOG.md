# Changelog

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
