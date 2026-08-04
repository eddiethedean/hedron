# Support

Hedron is an open-source MIT-licensed project. There is **no commercial SLA**, guaranteed
response time, or paid support contract.

## Where to ask

| Channel | Use for |
|---|---|
| [GitHub Issues](https://github.com/eddiethedean/hedron/issues) | Bugs, doc gaps, reproducible failures |
| [GitHub Discussions](https://github.com/eddiethedean/hedron/discussions) | Design questions (if enabled) |
| Pull requests | Fixes and documentation improvements |

Before filing an issue, check [FAQ](faq.md), [Troubleshooting](troubleshooting.md), and
[STATUS](../STATUS.md) for known Deferred rows.

## Security

Report vulnerabilities privately — see [SECURITY.md](../SECURITY.md). Do not file public
issues for undisclosed security problems.

## What “Beta” means for operators

Package maturity **Beta** means the public API is usable and tested, but breaking changes
may still land on the `0.x` line under the [compatibility policy](../COMPATIBILITY.md).
Pin versions in production, read [upgrade](upgrade.md) notes before bumping trains, and
treat Alpha packages (`hedron-charts`, `hedron-sample-kit`) as more volatile.

## Maintainer expectations

Issues without a minimal reproduction, version string (`hedron.__version__`), and expected
vs actual behavior may be closed. Feature requests should map to the [roadmap](../ROADMAP.md)
or an RFC discussion rather than informal “please add X” without context.
