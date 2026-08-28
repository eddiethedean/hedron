# Public 1.0 readiness (architectural review)

**Status:** **Published `v1.0.0`.** All 17 release gates and the immutable
`v0.67.0` compatibility bridge pass.
[D-114–D-117](https://github.com/eddiethedean/hedron/blob/main/docs/DECISIONS.md) supersede
D-038's no-1.0 terminus while retaining its evidence-based maturity rules.

**Verdict:** The repository and published artifacts satisfy the 1.0 review. The complete 0.67 public/task/artifact
inventory, warning reconciliation, enumerated stable surface, dual-version corpus, exact matrix,
support window, reproducible artifacts, and regression evidence are retained in the acceptance
packet.

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
| Under-engineering | Human AT sessions remain outstanding; some advanced symbol→tier documentation remains intentionally narrow |
| Leaky abstractions | Root/`hedron_core` kitchen-sink exports; satellites importing FastAPI `hedron` |
| Scaling risks | Every phase adds permanent CI cost; soft FastAPI coupling spreads with each satellite |

## 1.0 release checklist (complete)

1. **Governance — refined:** RFC-0096 and D-114–D-117 supersede D-038, define the evidence-driven
   cut, and explicitly make no commercial SLA or multi-year LTS claim.
2. **API freeze boundary — verified:** Shrink root/`hedron_core` public surfaces; enforce
   [symbol tiers](../api/SYMBOL_TIERS.md); promote only contracts you will protect across
   majors; remove experimental root aliases.
3. **Dependency purity — release gate:** Eliminate satellite→`hedron` imports (see
   `scripts/check_satellite_imports.py`); declare optional edges; freeze a Supported
   extras matrix; tip==PyPI discipline.
4. **Security contract — release gate:** Promote a locked security-plane/CSRF/trust subset to `stable`
   **or** exclude it from the 1.0 claim; production deny plugins by default; block
   experimental live mounts without explicit risk acceptance.
5. **Ops floor — release gate:** Durable jobs required in production profiles (already gated);
   decide cache stampede/single-flight story; keep **polling_only** as Supported live.
6. **AT honesty — resolved boundary:** Human AT does not block the cut and 1.0 makes no human-AT,
   WCAG-conformance, certification, or legal-compliance claim; automated/keyboard/focus evidence
   still gates the canonical widgets.
7. **Process prune — release gate:** Archive old packets; PR CI runs tip + recent only; generated
   remediation truth instead of stale issue tables.
8. **Package maturity — complete:** Flagship + claimed adapters are Stable in package metadata for
   the frozen inventory, and `v1.0.0` is published on PyPI.

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
- [1.0 implementation and cut plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/HEDRON_1_0.md)
- [1.0 acceptance plan](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_1_0.md)
