# Public 1.0 readiness (architectural review)

**Status:** Maintainer assessment of the living **0.62.x** train against an honest
public major. This is **not** a scheduled release plan.
[D-038](https://github.com/eddiethedean/hedron/blob/main/docs/DECISIONS.md)
still removes any calendar `1.0` terminus until a superseding RFC is Accepted.

**Verdict:** Do not call Hedron `1.0` today. Treat the product as **Beta with
enterprise-grade process**. The server-rendered CRUD/HTMX core is sound; blockers
are API surface honesty, package-graph purity, process/SSOT debt, and unfinished
adopter-critical DoD items (human AT sessions, durable ops clarity, identity
non-goals)—not missing CSRF or escaping.

## What is already strong

- Contextual HTML escaping and trust types (`TrustedHtml`, `SafeUrl`, `Secret`)
- CSRF + security profiles; HTMX eval/script defaults off; fail-closed fragment regions
- Locked beginner **stable** facade ([STABLE_FACADE](../api/STABLE_FACADE.md))
- Honest **`polling_only`** live disposition ([LIVE_DISPOSITION](../api/LIVE_DISPOSITION.md))
- Production gates for Explorer, weak secrets, and in-memory job/cache backends
- Phase **0.56** security control plane evidence
  ([RFC-0083](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0083-SECURITY-CONTROL-PLANE.md))

## Cross-cutting findings

| Category | Examples |
|---|---|
| Technical debt | Tip≠PyPI; undeclared optional edges; stale remediation narrative; root experimental shims |
| Over-engineering | Historical `verify_pkg_*` forever on PR quality; extras combinatorics; ROADMAP mega-ledger |
| Under-engineering | Human AT sessions Planned; production plugin discover-all default; symbol→tier mapping incomplete |
| Leaky abstractions | Root/`hedron_core` kitchen-sink exports; satellites importing FastAPI `hedron` |
| Scaling risks | Every phase adds permanent CI cost; soft FastAPI coupling spreads with each satellite |

## Before an honest 1.0 (must)

1. **Governance:** Accept an RFC that supersedes D-038; write a dated definition of done;
   decide LTS/SLA (even if “none—current train only”).
2. **API freeze boundary:** Shrink root/`hedron_core` public surfaces; enforce
   [symbol tiers](../api/SYMBOL_TIERS.md); promote only contracts you will protect across
   majors; remove experimental root aliases.
3. **Dependency purity:** Eliminate satellite→`hedron` imports (see
   `scripts/check_satellite_imports.py`); declare optional edges; freeze a Supported
   extras matrix; tip==PyPI discipline.
4. **Security contract:** Promote a locked security-plane/CSRF/trust subset to `stable`
   **or** exclude it from the 1.0 claim; production deny plugins by default; block
   experimental live mounts without explicit risk acceptance.
5. **Ops floor:** Durable jobs required in production profiles (already gated);
   decide cache stampede/single-flight story; keep **polling_only** as Supported live.
6. **AT honesty:** Complete human AT Verified cut **or** explicitly drop it from the DoD.
7. **Process prune:** Archive old packets; PR CI runs tip + recent only; generated
   remediation truth instead of stale issue tables.
8. **Package maturity:** Flagship + claimed adapters move Beta → Stable on PyPI for the
   **frozen inventory only**.

## Can wait until 2.0

- Graduating experimental SSE/WS/streaming with full browser + load + proxy proof
- Idiomorph / `MORPH-048`
- Real CodeMirror-backed CodeEditor
- Managed IdP / full auth product
- MCP mutations beyond experimental; multi-user notebooks
- External commercial SLA / multi-year LTS (if 1.0 ships without them)
- React-island / third-party WC ecosystem beyond the locked elements inventory
- Performance **marketing** SLOs (keep soft CI ceilings — see [PERFORMANCE_BUDGETS](../PERFORMANCE_BUDGETS.md))

## Should never be built

- Hedron as an IdP, ORM, or multi-tenant authorization engine
- A rerun-everything notebook runtime competing with Streamlit
- A required Node toolchain for ordinary apps
- Default-on Explorer or plugin autoload in production
- Promoting experimental live as Supported without ops evidence
- Freezing the entire current `hedron.__all__` / `hedron_core.__all__` as the 1.0 SDK
- Pulling every satellite onto the coordinated train
- Perpetual historical `verify_pkg_*` on every PR
- Claiming WCAG/SLA/“production 1.0 for every Beta symbol” from inventory labels alone
- Hidden trust sinks (auto-`TrustedHtml`, eval-on HTMX, ambient MCP mutations)

## Related

- [What's ready today](whats-ready.md)
- [Compatibility](../COMPATIBILITY.md)
- [Stability](../api/STABILITY.md)
- [Enterprise diligence](enterprise-diligence.md)
- [Production-quality maturity](https://github.com/eddiethedean/hedron/blob/main/docs/guides/production-quality.md)
