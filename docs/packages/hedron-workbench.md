# hedron-workbench

Compatibility Posit Workbench / RStudio Server deployment adapter.

**Package maturity:** Stable · **Repository release candidate:** `v1.0.0` (Git tag/PyPI upload deferred) · **Latest PyPI release:** `v0.66.2` · public pin `>=0.66.2,<0.67` until publication

**Final release notice:** `0.60.2` is the final published compatibility release of
`hedron-workbench`. It remains a compatibility shim for existing applications;
new applications should use `hedron-posit` and `HedronPosit`. No further
`hedron-workbench` feature releases are planned.

Prefer [`hedron-posit`](hedron-posit.md) / `HedronPosit` for new applications.
This package retains `HedronWorkbench` as a thin subclass (supported on the current
1.0 train; no 0.33 deprecation warning).

Installing or importing the package does **not** wrap your application.
`RS_SERVER_URL` is discovery-only and never grants trust.

Guide: [Posit deployments](../guides/posit.md) · [Posit Workbench](../guides/posit-workbench.md) ·
RFC: [RFC-0066](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0066-HEDRON-POSIT.md)

## Public API

| Symbol | Role |
|---|---|
| `HedronWorkbench` | Compatibility subclass of `HedronPosit` |
| Re-exports | Workbench / Connect helpers from `hedron_posit` |
| `hedron-workbench run` / `check` / `doctor` | Workbench-branded CLI delegating to `hedron-posit` |

Dependency: `hedron-workbench -> hedron-posit` (no reverse import).
