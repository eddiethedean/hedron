# Conformance authority (`v0.52`)

**Status:** Stage 1 Implemented / Verified. Living tip `v0.54.0`
(in-tree Published; tag/PyPI deferred). D-090 Stage 0 contract preserved
(`hedron-portable-1`).<br>
**Tracking:** [#522](https://github.com/eddiethedean/hedron/issues/522)<br>
**Related:** [#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513)<br>
**Decision/RFC:** D-089, refined by D-090 /
[RFC-0079](../rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md)<br>
**Planning baseline:** Published in-tree `v0.51.2`<br>
**Target:** Hedron `v0.52.0` (in-tree cut; do not tag yet)

## Consume shipped, do not fork

- `CONTRACT_VERSION = "hedron-portable-1"` / `FIXTURE_VERSION`
- `Capability` enum and `load_bundled_fixtures()`
- CLI `run` / `list` / `schema` / `compat`
- Default corpus `fixtures/*.json`; subdirectory corpora stay opt-in
- `hedron-runtime-node` / `hedron-runtime-java` tooling-grade until
  `RUNTIME-052` / `PKG-052`
- Do **not** reopen `polling_only`, `MORPH-048`, Explorer 0.50, 0.51 extras,
  0.53, 0.54, or `SR-021`

## Stage 1 Workstream A seams

- Profile registry (`load_profile_registry`, `admit_fixtures`, suite digests)
- Fixture compiler (`compile_suite` → `CompileReport`)
- Result envelopes + JUnit/SARIF (`build_result_envelope`, `to_junit`, `to_sarif`)
- Sandbox helpers (`validate_suite_path`, `SandboxPolicy`)
- Protocol negotiation matrix (`negotiate_protocol`, current/previous)
- Author kit `0.52.0` Capability declaration without monorepo import

## Architecture

```text
hedron-conformance     authority manifest, profiles, fixtures, author kit
       │
       ├── Python kit (hedron-portable-1 seed)
       ├── Node evaluator (independent install target)
       └── Java evaluator (independent install target)
Explorer / hedron check   report ingestion (CI-052)
```

1. Profiles extend `hedron-portable-1`; negotiation owns forward-unknown.
2. Fixture compiler rejects bad suites before any runtime runs.
3. Node/Java are reference consumers of the portable subset only.
4. Posit lifecycle is a sibling workstream — see
   [POSIT_LIFECYCLE_052](POSIT_LIFECYCLE_052.md).
