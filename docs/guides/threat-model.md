# Threat model (0.11 baseline)

**Status:** Maintained for the published **0.11** train  
**Owner:** hedron  
**Evidence:** security acceptance on the current train; live-transport caveats on
[What's ready](whats-ready.md)

## Assets

- Authenticated HTML pages and HTMX fragments
- Session cookies and CSRF tokens
- Component registry metadata and Explorer (dev-only)
- Build, CSS, asset, and Jinja template manifests and digests
- Job status payloads and cache entries (including Celery/RQ bridges)
- Bundled browser assets (HTMX, disclose)
- Django forms bridge outputs and bounded QuerySet DataSource pages
- Adapter live helpers (Flask/Django polling; FastAPI SSE/WS)

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
| Job backends | Authorization/tenant scope on submit and status; authorize poll and SSE the same way |
| Celery / RQ bridges | Same authz as in-process backends; workers must not widen tenant scope |
| Django forms bridge | Host CSRF + validated form data; widgets do not bypass escaping |
| QuerySet DataSource | App supplies an **authorized** base QuerySet; Hedron does not infer row-level ACL |
| Adapter live helpers | Prefer polling; treat SSE/WS as FastAPI-flagship observation with incomplete ops proof |
| HDJ source | Trusted application/package code; dynamic values remain contextual data; hostile authors unsupported |
| Identity / IdP | Out of Hedron scope — host owns OIDC/SSO/sessions |

## Adversaries and controls

| Scenario | Primary controls |
|---|---|
| XSS via props/children | Contextual escaping; no inline executable attrs by default |
| HDJ source/policy mismatch | Capability inventory + SecurityPolicy/CSP comparison; never silently enable inline/eval/remote execution |
| Open redirects / HTMX URL headers | `SafeUrl` / local-path policy; approved header allowlist |
| CSRF on unsafe methods | Double-submit cookie (FastAPI/Flask) or Django CSRF middleware; header or form field |
| Cache poisoning / confusion | Cache policy + `Vary` on HTMX dimensions; private defaults when authenticated |
| Unauthorized fragment/OOB | Region allowlist; 403 |
| Cross-tenant data via cache/jobs/fragments | Application tenancy — see [multi-tenant](multi-tenant.md) |
| Plugin / Explorer abuse | Prod Explorer off; capability/version checks; SARIF without secrets |
| Supply-chain browser asset swap | Exact pin + SHA-256 digest audit (`scripts/asset_audit.py`) |
| Dependency CVE | Lockfile + `scripts/generate_sbom.py` + release vuln audit |

## Out of scope (application-owned)

Identity providers, ORM authorization, durable job workers beyond `JobBackend`, business
validation, multi-tenant isolation, and containment of hostile template authors remain
application responsibilities. Anyone able to change HDJ source has application-code
authority.

## Review cadence

Re-review on every minor capability release. Record findings in the release
evidence bundle ([Evidence pack](evidence-pack.md)).
