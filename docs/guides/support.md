# Support

Hedron is an open-source MIT-licensed project. There is **no commercial SLA**, guaranteed
response time, or paid support contract.

## Where to ask

| Channel | Use for |
|---|---|
| [GitHub Issues](https://github.com/eddiethedean/hedron/issues) | Bugs, doc gaps, reproducible failures |
| Pull requests | Fixes and documentation improvements |

Before filing an issue, check [FAQ](faq.md), [Troubleshooting](troubleshooting.md),
[Error codes](error-codes.md), and [Ship a Hedron app](ship.md).
Known Deferred rows: [What's ready — evidence](whats-ready-evidence.md).

## Security

Report vulnerabilities privately — see [SECURITY.md](../SECURITY.md). Do not file public
issues for undisclosed security problems.

## What “Beta” means for operators

Package maturity **Beta** means the public API is usable and tested, but breaking changes
may still land on the `0.x` line under the [compatibility policy](../COMPATIBILITY.md).
Pin versions in production, read [upgrade](upgrade.md) notes before bumping trains, and
treat the Beta `hedron-elements` Supported inventory as still more volatile than CRUD
pages. Charts require `hedron-charts>=0.2.1,<0.3`. The sample kit requires
`hedron-sample-kit>=0.2.1,<0.3` — see [Compatibility](../COMPATIBILITY.md).

**Support window:** security fixes target the current published train (`0.66.x`).
Previous minors receive best-effort triage as documented in
[SECURITY.md](../SECURITY.md) (no multi-year LTS). Version and pin SoT:
[Current release and support](current-release.md). Public-index notes:
[Installation](../getting-started/installation.md). Community GitHub support only;
[Ship a Hedron app](ship.md) for ops.

## Maintainer expectations

Issues without a minimal reproduction, version string (`hedron.__version__`), and expected
vs actual behavior may be closed. Feature requests should map to
[What’s next](whats-next.md) or an RFC discussion rather
than informal “please add X” without context.
