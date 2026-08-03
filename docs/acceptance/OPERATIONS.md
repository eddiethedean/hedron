# Production operations acceptance

These requirements own roadmap gate 0.7B and the deployment portion of phase 0.8. Evidence follows
[the release evidence policy](EVIDENCE.md).

| ID | Requirement | Required evidence | State |
|---|---|---|---|
| OPS-001 | Production startup consumes deterministic validated manifests and performs no required runtime compilation or network fetch. | Offline clean-install/container test with manifest and lockfile digests. | Planned |
| OPS-002 | The FastAPI reference application works with multiple workers behind a prefixed reverse proxy and external static host. | Container topology smoke covering forwarded scheme/host, `root_path`, URLs, assets, CSRF, and cache headers. | Planned |
| OPS-003 | Correctness-critical state is external or reconstructible across workers. | Restart/worker-replacement test using external cache/job conformance implementations. | Planned |
| OPS-004 | Liveness differs from readiness; optional dependency degradation is visible without leaking secrets. | Health/readiness failure matrix and redacted output. | Planned |
| OPS-005 | Startup, shutdown, plugin resources, background tasks, caches, and jobs have deterministic graceful-shutdown ordering. | Repeated termination tests with no leaked resources or accepted-work loss outside documented policy. | Planned |
| OPS-006 | Configuration and proxy trust are explicit and fail closed when unsafe or inconsistent. | Negative configuration/proxy corpus. | Planned |
| OPS-007 | Recovery, rollback, backup/retention ownership, and artifact provenance are documented and rehearsed. | Deployment rollback from published candidate artifacts. | Planned |

## Exit

The production topology is reproducible from published artifacts, survives worker replacement and
dependency degradation according to policy, and produces a retained deployment evidence bundle.
