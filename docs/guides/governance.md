# Governance

Hedron uses maintainer-led, public decision making. The goal is predictable
stewardship: users should know who can merge a change, how public contracts change,
and what happens if a maintainer becomes unavailable.

## Roles

| Role | Responsibilities | How the role changes |
|---|---|---|
| Contributor | Issues, documentation, tests, and pull requests | Anyone participating under the Code of Conduct |
| Reviewer | Reviews an area they understand and may be requested by a maintainer | Earned through sustained, accurate contributions |
| Maintainer | Triage, merge authority, releases, security response, and governance | Added or removed by consensus of active maintainers |
| Lead maintainer | Resolves deadlocks and owns credentials that cannot be shared | Named in the repository's GitHub settings |

Current maintainers are the people listed as maintainers for the
[`hedron` package on PyPI](https://pypi.org/project/hedron/) and repository
administrators on GitHub. Security reports use the private process in the
[security policy](../SECURITY.md), not public governance discussion.

## How decisions are made

Small, reversible changes are decided in pull-request review. Public API changes,
security-default changes, removals, and other hard-to-reverse decisions require an
[RFC](https://github.com/eddiethedean/hedron/tree/main/docs/rfcs) and a recorded
[decision](https://github.com/eddiethedean/hedron/blob/main/docs/DECISIONS.md).

Maintainers seek consensus. If reasonable objections remain after the alternatives,
compatibility cost, and evidence are recorded, the lead maintainer decides and records
the reason. A decision can be revisited through a new RFC; it is not silently reversed.

## Maintainer changes and succession

A contributor may be nominated after demonstrating sound judgment across multiple
changes. Existing active maintainers approve the nomination by consensus. Maintainers
who expect to be unavailable should transfer release, package-index, documentation,
and security-channel access before stepping down.

If no maintainer responds to ordinary project activity for 60 days, established
reviewers should open a public succession issue. If the security channel is also
unresponsive, contact the hosting providers through their account-recovery processes.
The project must never be transferred, renamed, or republished under a new package
identity without a public decision record.

## Releases and support

Only a maintainer may publish a release. Trusted publishing, immutable tags, CI gates,
and attached evidence are the expected release path. Supported versions and response
expectations are defined in the [support policy](support.md). The detailed cut procedure
lives in the [maintainer handbook](maintainer-handbook.md).

## Project assets

The repository, package-index projects, documentation project, domain names, and
security-reporting channel are project assets. Access should be held by at least two
active maintainers whenever the service permits it. Credentials are never committed to
the repository.

