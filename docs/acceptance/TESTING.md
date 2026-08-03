# Testing acceptance

## Helpers *(phase 0.4)*

- [x] Public `hedron.testing` helpers cover render assertions, fragment clients, dependency overrides, and named examples.
- [x] Snapshot normalizers document allowed nondeterminism and do not hide escaping or ordering bugs.
- [x] Adapter-conformance skeleton exists for FastAPI (Flask/Django deferred to 0.7).
- [x] Optional `hedron[browser]` exposes Playwright and axe-style hooks without requiring them for core CI.

## Exit

Reference and sample packages exercise public helpers rather than private test utilities.

## Phase 0.7+ evidence

- [ ] Portable adapter semantics run through one shared suite and every capability claim has a native
  framework/server test.
- [ ] Flask and Django clean environments exclude FastAPI and exercise native reference slices.
- [ ] Real browser jobs are active rather than permanently skipped for shipped browser assets.
- [ ] Release-gate manifests map stable acceptance IDs to commands, CI jobs, matrix dimensions, and
  retained artifacts under [EVIDENCE.md](EVIDENCE.md).
- [ ] Published `1.0.0rcN` artifacts, not repository imports, pass clean install, upgrade,
  deployment, rollback, offline, and complete acceptance rehearsals.
