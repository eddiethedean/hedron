# hedron-workbench

Compatibility Posit Workbench / RStudio Server deployment adapter.

**Package maturity:** Beta (`0.50.x`) · extra `hedron[workbench]` · pin `>=0.50.1,<0.51`

Prefer [`hedron-posit`](hedron-posit.md) / `HedronPosit` for new applications.
This package retains `HedronWorkbench` as a thin subclass (supported on the current
0.50 train; no 0.33 deprecation warning).

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
