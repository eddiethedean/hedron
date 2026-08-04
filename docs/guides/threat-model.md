# Threat model (0.8 freeze)

**Status:** Maintained for phase 0.8 / `v1.0.0` acceptance  
**Owner:** hedron  
**Evidence:** `SEC-08-001`

## Assets

- Authenticated HTML pages and HTMX fragments
- Session cookies and CSRF tokens
- Component registry metadata and Explorer (dev-only)
- Compiled HDN/CSS/asset manifests and digests
- Job status payloads and cache entries
- Bundled browser assets (HTMX, disclose)

## Trust boundaries

| Boundary | Trust rule |
|---|---|
| Untrusted request input | Never becomes TrustedHtml; strings escape by context |
| `TrustedHtml` / `SafeUrl` | Explicit construction only; purpose-checked at render/redirect |
| Addressable components | Reachable only after explicit registration / `include_component` |
| Fragment regions / OOB | Declared allowlists; unauthorized `HX-Target` → 403 |
| Explorer | Production default off; must not expose secrets |
| Plugins | Entry-point load; incompatible majors rejected; no implicit trust elevation |
| Cache / intermediaries | Pages, fragments, and target variants must `Vary` correctly; private authenticated defaults |
| History snapshots | Sensitive pages opt out; cached snapshots must not disclose private content |
| Job backends | Authorization/tenant scope on submit and status; polling not SSE |

## Adversaries and controls

| Scenario | Primary controls |
|---|---|
| XSS via props/children | Contextual escaping; no inline executable attrs by default |
| Open redirects / HTMX URL headers | `SafeUrl` / local-path policy; approved header allowlist |
| CSRF on unsafe methods | Double-submit cookie; header or form field |
| Cache poisoning / confusion | Cache policy + `Vary` on HTMX dimensions; private defaults when authenticated |
| Unauthorized fragment/OOB | Region allowlist; 403 |
| Plugin / Explorer abuse | Prod Explorer off; capability/version checks; SARIF without secrets |
| Supply-chain browser asset swap | Exact pin + SHA-256 digest audit (`scripts/asset_audit.py`) |
| Dependency CVE | Lockfile + `scripts/generate_sbom.py` + release vuln audit |

## Out of scope (application-owned)

Identity providers, ORM authorization, durable job workers beyond `JobBackend`, and
business validation remain application responsibilities (see product non-goals).

## Review cadence

Re-review on every minor release and before each `1.0.0rcN`. Record findings in the release
evidence bundle.
