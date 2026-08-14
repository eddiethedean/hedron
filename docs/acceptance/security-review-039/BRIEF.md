# Security review brief — phase 0.39 rich data and OptimisticMutation

**Cut target:** Hedron `v0.39.0`  
**Owning RFC / decision:** RFC-0060 / D-067  
**Tracking:** [#94](https://github.com/eddiethedean/hedron/issues/94)  
**Baseline:** Published `v0.38.0`  
**Primary gates:** `DATA-039`, `OPTIMISTIC-039`, `CHARTLINK-039`, `RICH-039`, `WORKER-039`,
`PERF-039`, `A11Y-039`, `REGRESS-039`, `PKG-039`  
**Medium/low packet:** the 27 issues listed under #94 / ROADMAP are `REGRESS-039`-owned (issue
bodies remain normative). Security-relevant members include spreadsheet formula policy, path
traversal, media range buffering, and DataEditor conflict/retry revision handling.

## Review scope

- DataTable/DataEditor ABI: edit/selection events, virtualization buffers, validation messages,
  saved-view persistence, SSR fallback, authorization boundaries, and disconnect teardown.
- Typed `OptimisticMutation`: base revision, idempotency keys, patch/refetch payloads,
  proposed/submitted/confirmed states, rollback, conflict, reconnect, and deny-by-default risk
  exclusions (auth changes, irreversible destruction, payments, secrets, file publication,
  cross-tenant moves).
- Chart cross-filter / composition that consumes Published `hedron-chart` without treating browser
  selection as authorization.
- Map/media/code-editor/specialty hosts: XSS sinks, URL/asset policy, Experimental exception
  honesty, and owned destinations.
- Workers, WASM, object URLs, media streams, observers, third-party runtimes, remote origins,
  payload sizes, cancellation, and disconnect cleanup.
- Spreadsheet import/export formula injection, decompression bombs, control characters, and
  redaction false-positives owned by the 0.39 remediation packet.
- Strict CSP and Trusted Types without callback/eval/inline-script escape hatches for Supported
  surfaces.

## Required adversarial cases

1. Stale optimistic revisions, forged idempotency keys, double-submit, conflict retry with an old
   base revision, and reconnect races that resurrect discarded edits.
2. XSS through cell values, validation messages, saved-view labels, map/media captions, editor
   content, and chart-link annotations.
3. Worker/WASM/stream/object-URL leaks across HTMX swaps, history restore, and rapid disconnect.
4. Treating client selection, pending optimistic state, or chart brush ranges as authorization.
5. Path traversal / relative model URLs, formula injection with invisible Unicode, and unbounded
   media range buffering (#194 / #191 / #221 class).

## Out of scope

- Full Supported human AT matrix (`SR-021` / #86).
- Creating a second interactive chart renderer or re-opening 0.38 chart security gates.
- Production-grade graduation of the whole Web Component platform (phase 0.42).
- Application business-rule correctness beyond the typed optimistic and authz contracts.

## Required cut artifacts

- `REDACTED_REPORT.md` with findings, severity, affected gates, remediation, and residual risk.
- `DISPOSITION.toml` proving no unresolved critical/high finding.
- SBOM/provenance references for any newly shipped browser assets.
- Adversarial suite output and retained browser lifecycle/optimism artifacts.

## Stage 0 status

Brief only. It is not security evidence and does not authorize a Supported claim.
