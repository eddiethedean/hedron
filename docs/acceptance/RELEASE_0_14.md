# Hedron `v0.14` portable runtimes and acceleration acceptance

Phase 0.14 delivers a published language-neutral conformance-test kit, experimental
Java and Node runtimes, optional Rust acceleration with pure-Python fallback, and HDJ
Jinja instrumentation (exact loop/macro budgets, contracted extension evidence,
scoped-style/validated-attribute helpers, broader contextual analysis, and portable
checker fixtures). Evidence is indexed by [`release-gate-0.14.toml`](release-gate-0.14.toml).
**Zero Deferred:** every 0.14-owned gate row must be Verified at cut. Prior-phase live
ops Deferred rows remain owned by `0.10.x` / `0.11.x`.

## Spec packet

- [x] ROADMAP §0.14 scope accepted; D-048 lifts D-018 under evidence gates.
- [x] Entry gate: 0.13 evidence remains closed; 0.14 gate TOML owns Verified rows only.

## Conformance kit and language-neutral spec

- [x] Versioned fixtures, goldens, negatives, normalization rules, and capability-level
  runner. *(`CONFORM-014`)*
- [x] Language-neutral component/fixture schema extracted from proven Python contracts.
  *(`SPEC-014`)*

## Experimental runtimes

- [x] Node runtime passes the published kit. *(`RUNTIME-NODE-014`)*
- [x] Java runtime passes the published kit. *(`RUNTIME-JAVA-014`)*

## Rust acceleration

- [x] Optional `hedron-native` acceleration for measured serializer escaping hot paths
  with reproducible wheels, source-build, pure-Python fallback, fuzz/parity, and
  material end-to-end benefit. *(`ACCEL-RUST-014`)*
- [x] Accelerator absence never changes public semantics, security policy, or
  deterministic output. *(`PARITY-014`)*

## HDJ instrumentation

- [x] Exact loop/macro budgets, contracted custom-extension evidence, scoped-style and
  validated-attribute helpers, broader contextual analysis, and portable checker
  fixtures with pure-Python fallback. *(`HDJ-DEF-014`)*

## Exit

- [x] Full regression suite. *(`REGRESS-014`)*
- [x] Packaging rehearsal. *(`PKG-014`)*

**Exit met** as coordinated `0.14.0` (`v0.14.0`) when every gate row is Verified.
