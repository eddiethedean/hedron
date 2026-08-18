# Support

Hedron is an open-source MIT-licensed project. There is **no commercial SLA**, guaranteed
response time, or paid support contract.

## Where to ask

| Channel | Use for |
|---|---|
| [GitHub Issues](https://github.com/eddiethedean/hedron/issues) | Bugs, doc gaps, reproducible failures |
| Pull requests | Fixes and documentation improvements |

Before filing an issue, check [FAQ](faq.md), [Troubleshooting](troubleshooting.md),
[Error codes](error-codes.md), and [Production readiness](production-readiness.md).
Known Deferred rows: [What's ready](whats-ready.md).

## Security

Report vulnerabilities privately — see [SECURITY.md](../SECURITY.md). Do not file public
issues for undisclosed security problems.

## What “Beta” means for operators

Package maturity **Beta** means the public API is usable and tested, but breaking changes
may still land on the `0.x` line under the [compatibility policy](../COMPATIBILITY.md).
Pin versions in production, read [upgrade](upgrade.md) notes before bumping trains, and
treat the Beta `hedron-elements` Supported inventory as still more volatile than CRUD
pages. Charts and the sample kit require the compatible
`>=0.2.0,<0.3` satellite floor — see [Compatibility](../COMPATIBILITY.md).

**Support window:** security fixes target the current published train (`0.49.x`). The
previous `0.48.x` train receives best-effort security triage through approximately
**2027-08-17**. Git tag / PyPI for `v0.49.1` are **deferred**; install from PyPI is
still **`0.48.0`**.
There is no multi-year LTS — see [SECURITY.md](../SECURITY.md).
Community GitHub support only;
[Ship a Hedron app](ship.md) for ops.

## Maintainer expectations

Issues without a minimal reproduction, version string (`hedron.__version__`), and expected
vs actual behavior may be closed. Feature requests should map to
[What’s next](whats-next.md) or an RFC discussion rather
than informal “please add X” without context.
