# Hedron 1.0 support policy (draft)

This document is an implementation artifact, not a release claim. The 1.0 cut remains blocked
until the release gate is verified.

- The stable 1.x promise applies to the enumerated `stable-inventory-100.toml` surface.
- Hedron `0.67.x` is the migration and rollback source for the 1.0 cut.
- Beta and Experimental interfaces retain their weaker maturity labels and are not implicitly
  promoted by the major version.
- A release is stopped before publication when a public removal lacks a complete warning and
  executable fixture. After publication, fixes move forward in `1.0.x`; removed aliases are not
  silently restored.
- Exact Python, dependency, adapter, satellite, browser, type-checker, CLI, template, and
  artifact support ranges are published with the verified compatibility BOM.
