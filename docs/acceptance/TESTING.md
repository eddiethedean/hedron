# Testing acceptance

## Helpers *(phase 0.4)*

- [x] Public `hedron.testing` helpers cover render assertions, fragment clients, dependency overrides, and named examples.
- [x] Snapshot normalizers document allowed nondeterminism and do not hide escaping or ordering bugs.
- [x] Adapter-conformance skeleton exists for FastAPI (Flask/Django deferred to 0.7).
- [x] Optional `hedron[browser]` exposes Playwright and axe-style hooks without requiring them for core CI.

## Exit

Reference and sample packages exercise public helpers rather than private test utilities.
