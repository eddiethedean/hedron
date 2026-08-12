# Third-party conformance runtime author kit

Use this kit when implementing a Node, Java, or other evaluator that runs the
same immutable portable fixture corpus as `hedron-conformance`.

## Requirements

1. Load the published fixture JSON (same IDs as the Python bundled corpus).
2. Declare `contract_version` and `fixture_version` and validate them with the
   compatibility policy (`hedron_conformance.compat`).
3. For each fixture, emit a pass/fail result with the fixture `id` and capability.
4. On failure, emit an actionable diagnostic code (see intentional-failure examples
   from `hedron_conformance.author.intentional_failure_examples()`).

## Compatibility

- Same contract family + major as the runner (`hedron-portable-1`) is Accepted.
- Newer or unknown majors must **refuse** with `CONF-COMPAT-*` diagnostics.
- Do not guess mappings for unknown fixture capabilities.

## Non-goals

- Application production servers
- Full Hedron ports
- Silently skipping fixtures
