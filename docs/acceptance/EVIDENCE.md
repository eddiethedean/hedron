# Release evidence policy

Beginning with the phase 0.6 closure gate, prose checkboxes summarize status but do not prove a
requirement complete. Every completed release-gating requirement has a stable ID and an evidence
record containing:

- the owning RFC and public/implementation contract;
- the exact local command and CI job that exercise it;
- the supported framework, server, Python, platform, and browser dimensions;
- an immutable artifact, report, or test-result URL retained with the release; and
- an owner plus any approved deferment, waiver, expiry, and remediation issue.

## Evidence states

| State | Meaning |
|---|---|
| Planned | Requirement is accepted but implementation evidence is not expected yet. |
| Implemented | Code exists; release evidence is incomplete. |
| Verified | Required command and matrix are green with a retained artifact. |
| Deferred | Owning RFC, rationale, destination phase, and public stability impact are recorded. |
| Blocked | A named dependency prevents verification; the release gate remains open. |

`Verified` is the only state that satisfies a release gate. A waiver cannot hide a critical/high
security issue, a release-blocking accessibility defect, or an untested supported compatibility
claim.

## Machine-readable manifest

Before `v0.7.0`, the repository will add a versioned release-gate manifest consumed by
`scripts/check_release_gate.py`. It records required evidence IDs and expected CI artifact names for
each train. The checker fails closed when an ID is missing, duplicated, deferred without ownership,
or marked complete without its artifact. Human-readable acceptance pages remain the explanation;
the manifest is the enforceable index.

## Minimum retained bundle

Each 0.7+ release bundle contains test results, compatibility/capability matrices, package inventory,
browser results when applicable, security and accessibility reports, performance comparisons,
deployment smoke output, licenses, SBOM/provenance material when required by phase, and the exact
source revision and lockfile digest.
