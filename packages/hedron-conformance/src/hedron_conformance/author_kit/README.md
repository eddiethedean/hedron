# Third-party conformance runtime author kit (AUTHOR-052 / kit 0.52)

Use this kit when implementing a Node, Java, or other evaluator that runs the
same immutable portable fixture corpus as `hedron-conformance`.

**Author kit version:** `0.52.0` (extends seed `hedron-portable-1`; does not
replace `CONTRACT_VERSION` without negotiation).

Third parties declare supported `Capability` values in their own package
manifest — **without importing the Hedron monorepo**. Copy the capability
labels from the published fixture schema / this kit; do not vendor private
workspace paths.

## Requirements

1. Load the published fixture JSON (same IDs as the Python bundled corpus).
2. Declare `contract_version` and `fixture_version` and validate them with the
   compatibility policy (`hedron_conformance.compat` / `negotiate_protocol`).
3. Declare which `Capability` labels your runtime implements (escaping,
   identity, diagnostics, artifact-version, rendering, accessibility,
   adversarial) in your package metadata — no monorepo import required.
4. For each fixture, emit a pass/fail result with the fixture `id` and capability.
5. On failure, emit an actionable diagnostic code (see intentional-failure examples
   from `hedron_conformance.author.intentional_failure_examples()`).

## Compatibility

- Same contract family + major as the runner (`hedron-portable-1`) is Accepted.
- Newer or unknown majors must **refuse** with `CONF-COMPAT-*` diagnostics.
- Do not guess mappings for unknown fixture capabilities.
- Profile admission (`core-render`, `interaction`, `manifest`, `element`,
  `package`) selects capability subsets; subdirectory corpora stay opt-in.

## Non-goals

- Application production servers
- Full Hedron ports
- Silently skipping fixtures
- Importing monorepo-private modules for Capability labels
