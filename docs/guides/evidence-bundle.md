---
description: Locate the release, provenance, compatibility, security, and acceptance evidence for 1.0.
---

# 1.0 evidence bundle

Use this page to establish what was published, how it was built, what was verified, and which
responsibilities remain with the adopting organization.

## Release identity

| Evidence | Source |
|---|---|
| Hedron package and files | Published `1.0.1` |
| Edron package and files | Published `1.0.1` |
| Source tag, wheels, checksums, and attached evidence | Published from immutable `v1.0.1` tag |
| Current install and support facts | [Current release](current-release.md) |

The GitHub release attaches `release-manifest.json`, built distributions, generated evidence,
and supply-chain artifacts. GitHub Actions records build provenance for the uploaded subjects.
Verify hashes against the release manifest before promoting artifacts into an internal index.

## Engineering evidence

| Question | Evidence |
|---|---|
| What is compatibility-protected? | [Stability classifications](../api/STABILITY.md) |
| What combinations are tested? | [Compatibility matrix](../COMPATIBILITY.md) |
| Which capabilities are Supported? | [Readiness evidence](whats-ready-evidence.md) |
| What passed the 1.0 gate? | [1.0 acceptance packet](https://github.com/eddiethedean/hedron/blob/v1.0/docs/acceptance/RELEASE_1_0.md) |
| What are the architecture and trust boundaries? | [Architecture](../ARCHITECTURE.md) · [Threat model](threat-model.md) |
| How are vulnerabilities handled? | [Security policy](../SECURITY.md) |
| What must the application/platform own? | [Enterprise diligence](enterprise-diligence.md) |

## Procurement caveats

Hedron and Edron are MIT-licensed community projects. There is no commercial SLA, managed
hosting, identity provider, database, durable queue, or compliance certification. SBOM,
provenance, checksums, and automated test evidence support an organization's own diligence;
they do not replace dependency review, threat modeling, access control, backup, incident
response, or legal review.

## Reproduce the documentation checks

```bash
uv sync --group docs
bash scripts/ci_checks.sh docs
uv run python scripts/check_100.py --gate ENTRY-100 --verify
```

The release workflow also installs the published artifact into a clean environment and imports
the generated scaffold before creating the GitHub release.
