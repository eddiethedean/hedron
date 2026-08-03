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

The phase 0.6 closure index lives at
[release-gate-0.6.toml](release-gate-0.6.toml). `scripts/check_release_gate.py <version>`
validates package metadata and fails closed when an evidence ID is missing, duplicated,
`Verified` without a command, or `Deferred` without ownership/rationale/destination.

## Phase 0.6 closure IDs

| ID | State | Command |
|---|---|---|
| `HTMX-C06-001` | Verified | `uv run pytest tests/security/test_interaction_headers.py -q` |
| `HTMX-C06-002` | Verified | `uv run pytest tests/security/test_interaction_headers.py tests/unit/test_phase06.py -q` |
| `HTMX-C06-003` | Verified | `HEDRON_BROWSER=1 uv run pytest -m browser -q` |
| `SEC-C06-001` | Verified | `uv run pytest tests/security/test_interaction_headers.py -q` |
| `SEC-C06-002` | Verified | `uv run pytest tests/security/test_chart_svg_corpus.py -q` |
| `VIS-C06-001` | Verified | `uv run pytest tests/security/test_chart_svg_corpus.py -q` |
| `VIS-C06-002` | Deferred | Plotly/Vega full offline runtime pin (experimental host shims) |
| `DATA-C06-001` | Verified | `uv run pytest tests/unit/test_sqlalchemy_source.py -q` |

## Minimum retained bundle

Each 0.7+ release bundle contains test results, compatibility/capability matrices, package inventory,
browser results when applicable, security and accessibility reports, performance comparisons,
deployment smoke output, licenses, SBOM/provenance material when required by phase, and the exact
source revision and lockfile digest.
