# Runtime evaluator template

```text
1. Resolve fixture corpus path (packaged asset or HEDRON_CONFORMANCE_FIXTURES).
2. Parse JSON array of fixtures.
3. For each fixture:
   a. check_contract_version(fixture.contract_version)
   b. check_fixture_version(fixture.fixture_version)
   c. dispatch on fixture.capability
   d. compare normalized output to fixture.expected
4. Exit 0 only when every fixture passes.
5. Print JSON summary with {id, ok, diagnostic_code?} rows.
```

Reference: Python `hedron_conformance.reference.run_reference` and CLI
`hedron-conformance run --json`.
