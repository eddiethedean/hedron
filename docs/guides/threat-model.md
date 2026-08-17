# Threat model

**Status:** Maintained for the current **0.48.x** train (**Published**; last published
PyPI/git = `v0.48.0`; baseline established in 0.11 and extended through the 0.36
Web Component ABI/lifecycle surface)

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
- Model-demo / inference inputs, predictions, and feedback records
- Optional MCP tool projections and Gradio client adapters (deny-by-default)
- Optional notebook preview sessions (localhost-oriented)

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
| Inference / model demos | Fail-closed: explicit actions, exposure policy, and consent before feedback retention |
| `InferencePolicy` queues | In-process queues are **dev-only**; production needs app-owned scheduling/backends |
| `InteractionRecorder` | Records only endpoints declared public; redacts credentials; never expands authority |
| MCP projection (`hedron[mcp]`) | Deny-by-default tool exposure; apps must opt in each capability |
| Gradio adapter (`hedron[gradio]`) | Beta allowlisted client interop; arbitrary destinations and UI embedding remain excluded |
| Notebook preview (`hedron[notebook]`) | Localhost-oriented; not a Supported production multi-tenant surface |

## Adversaries and controls

| Scenario | Primary controls |
|---|---|
| XSS via props/children | Contextual escaping; no inline executable attrs by default |
| HDJ source/policy mismatch | Capability inventory + SecurityPolicy/CSP comparison; never silently enable inline/eval/remote execution |
| Open redirects / HTMX URL headers | `SafeUrl` / local-path policy; approved header allowlist |
| CSRF on unsafe methods | Double-submit cookie (FastAPI/Flask) or Django CSRF middleware; header or form field |
| Cache poisoning / confusion | Cache policy + `Vary` on HTMX dimensions; private defaults when authenticated |
| Unauthorized fragment/OOB | Fail-closed region allowlist (`authorize_htmx_target`); 403 unless opt-out |
| Unscoped job HTTP status/SSE | Fail-closed (`job_authorized_http`); jobs must carry auth/tenant scope |
| Cross-tenant data via cache/jobs/fragments | Application tenancy — see [multi-tenant](multi-tenant.md) |
| Plugin / Explorer abuse | Prod Explorer off; capability/version checks; SARIF without secrets |
| Supply-chain browser asset swap | Exact pin + SHA-256 digest audit (`scripts/asset_audit.py`) |
| Dependency CVE | Lockfile + `scripts/generate_sbom.py` + release vuln audit |
| Inference data leakage / unauthorized demo actions | Explicit `ActionRegistry` / exposure; fail-closed `InferencePolicy`; no silent tool expansion |
| Feedback without consent | `PredictionFeedback` requires documented consent before retention |
| Recorder expanding endpoint authority | Public-endpoint allowlist + redaction (`InteractionRecorder`) |
| MCP / Gradio accidental exposure | Deny-by-default extras; pin packages; keep Gradio and MCP mutations off production defaults |
| Notebook preview cross-user access | Treat as local/dev; do not expose without app authz |

## Out of scope (application-owned)

Identity providers, ORM authorization, durable job workers beyond `JobBackend`, business
validation, multi-tenant isolation, model-weight / training-data governance, and
containment of hostile template authors remain application responsibilities. Anyone able
to change HDJ source has application-code authority.

## Related

- [Security guide](security.md) · [Enterprise diligence](enterprise-diligence.md)
- [Model demos](model-demos.md) · [Jobs](../api/JOBS.md) · [What's ready](whats-ready.md)

## Review cadence

Re-review on every minor capability release. Record findings in the release
evidence bundle ([Evidence pack](evidence-pack.md)).
