---
description: Publication, artifact, compatibility, and acceptance evidence for Hedron 1.2.0.
---

# 1.2.0 publication evidence

This page summarizes the retained evidence for the current published Python release. The
authoritative artifact hashes live in the [publication record](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/evidence-120/PUBLICATION.md).

## Release identity

| Evidence | Source |
|---|---|
| Hedron | [PyPI 1.2.0](https://pypi.org/project/hedron/1.2.0/) |
| Edron | [PyPI 1.2.0](https://pypi.org/project/edron/1.2.0/) |
| All coordinated Python distributions | 44 of 44 wheel and source archive names and SHA-256 digests match the retained publication ledger |
| Package source revision | `92e369a26aaa771ee5b5d4a8264dfd758a71a533` |
| Evidence-only follow-up tag | `release-20261027-01` points to `fced98f466478dd9e1c31a8e13f3b1bae7ce4fc3`; the package source commit is its parent |
| Current install and support facts | [Current release](current-release.md) |

The verification record does not assert a hosted GitHub Release entry. The separately owned
`hedron-native==0.1.4` PyPI publication remains unconfirmed and is outside the coordinated
22-distribution Python artifact set.

## Engineering and compatibility evidence

| Question | Evidence |
|---|---|
| What is compatibility-protected? | [Stability classifications](../api/STABILITY.md) |
| Which Python versions are supported? | [Compatibility matrix](../COMPATIBILITY.md) |
| Which capabilities are Supported? | [Readiness evidence](whats-ready-evidence.md) |
| What changed in 1.2? | [What’s new in 1.2](whats-new-1.2.md) |
| What are the architecture and trust boundaries? | [Architecture](../ARCHITECTURE.md) · [Threat model](threat-model.md) |
| How are vulnerabilities handled? | [Security policy](../SECURITY.md) |
| What must the adopting organization own? | [Enterprise diligence](enterprise-diligence.md) |

The older 1.1.3 publication evidence is retained in the [historical evidence bundle](evidence-bundle-1.1.md).

## Procurement caveats

Hedron and Edron are MIT-licensed community projects. There is no commercial SLA, managed
hosting, identity provider, database, durable queue, or compliance certification. Checksums and
automated test evidence support an organization's own diligence; they do not replace dependency
review, threat modeling, access control, backup, incident response, or legal review.
