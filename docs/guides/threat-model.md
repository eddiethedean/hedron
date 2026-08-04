# Threat model (0.10 baseline)

**Status:** Maintained for the published **0.10** train (updated from the 0.8 compatibility baseline)
**Owner:** hedron  
**Evidence:** `SEC-08-001`, live-transport acceptance in RFC-0032 / RELEASE_0_10

## Assets

- Authenticated HTML pages and HTMX fragments
- Session cookies and CSRF tokens
- Component registry metadata and Explorer (dev-only)
- Build, CSS, asset, and Jinja template manifests and digests
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
| Job backends | Authorization/tenant scope on submit and status; SSE (`job_status_sse_response`) and polling are both Supported on FastAPI — authorize every status channel the same way |
| HDJ source | Trusted application/package code; dynamic values remain contextual data; hostile authors unsupported |

## Adversaries and controls

| Scenario | Primary controls |
|---|---|
| XSS via props/children | Contextual escaping; no inline executable attrs by default |
| HDJ source/policy mismatch | Capability inventory + SecurityPolicy/CSP comparison; never silently enable inline/eval/remote execution |
| Open redirects / HTMX URL headers | `SafeUrl` / local-path policy; approved header allowlist |
| CSRF on unsafe methods | Double-submit cookie; header or form field |
| Cache poisoning / confusion | Cache policy + `Vary` on HTMX dimensions; private defaults when authenticated |
| Unauthorized fragment/OOB | Region allowlist; 403 |
| Plugin / Explorer abuse | Prod Explorer off; capability/version checks; SARIF without secrets |
| Supply-chain browser asset swap | Exact pin + SHA-256 digest audit (`scripts/asset_audit.py`) |
| Dependency CVE | Lockfile + `scripts/generate_sbom.py` + release vuln audit |

## Out of scope (application-owned)

Identity providers, ORM authorization, durable job workers beyond `JobBackend`, business
validation, and containment of hostile template authors remain application responsibilities (see
product non-goals). Anyone able to change HDJ source has application-code authority.

## Review cadence

Re-review on every minor capability release. Record findings in the release
evidence bundle.
