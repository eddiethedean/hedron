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

## What package maturity means for operators

Only `hedron-core` and `hedron` are **Stable** packages in 1.0; independent satellites remain
Beta or tooling-grade. API-level `beta` and `experimental` classifications still apply within
the stable packages. Pin versions in production and read [upgrade](upgrade.md) notes
before bumping trains. Charts require `hedron-charts>=0.2.4,<0.3`. The sample kit requires
`hedron-sample-kit>=0.2.3,<0.3` — see [Compatibility](../COMPATIBILITY.md).

**Support window:** security fixes target the current repository train (`1.0.x`) while its
public upload is deferred. The public fallback is `hedron>=0.67.0,<0.68`. Previous minors receive best-effort triage as documented in
[SECURITY.md](../SECURITY.md) (no multi-year LTS). Version and pin SoT:
[Current release and support](current-release.md). Public-index notes:
[Installation](../getting-started/installation.md). Community GitHub support only;
[Ship a Hedron app](ship.md) for ops.

## Maintainer expectations

Issues without a minimal reproduction, version string (`hedron.__version__`), and expected
vs actual behavior may be closed. Feature requests should map to
[What’s next](whats-next.md) or an RFC discussion rather
than informal “please add X” without context.
