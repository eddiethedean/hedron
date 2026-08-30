# What's new in 0.52

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and published 1.0 status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

Historical **0.52.0** in-tree Published cut (tag/PyPI may still be deferred relative to later trains). Tracking [#522](https://github.com/eddiethedean/hedron/issues/522).

## 0.52.0

Cross-language conformance authority and HedronPosit deployment lifecycle
(RFC-0079 / D-089 / D-090):

### Conformance authority

- `hedron-conformance` is the versioned compatibility authority for the declared
  portable subset extending `hedron-portable-1`.
- Profile registry, fixture compiler, negative/boundary vectors, differential and
  platform evidence, signed reports, and CI/SARIF provenance.
- Independently installable Node/Java evaluators (`hedron-runtime-node` /
  `hedron-runtime-java` `0.52.0`) consume the portable subset only — not full
  FastAPI/browser Hedron ports.
- External author kit runs declared capabilities without a monorepo import.

### Posit lifecycle companions (#508–#513)

- Cookie registry + set/delete lifecycle (`CookieRegistry`) — apps stop owning
  mount cookie path math.
- Request-bound `PositContext` / `posit_for(request)` for links, redirects, cookies.
- Opt-in `hands_off` URL/redirect adaptation (validated same-app paths only).
- Deployment-matrix fixtures and `hedron-posit check --matrix`.
- Proactive Posit diagnostics with stable codes (never log cookie values).
- Named-route query/fragment/durable parity across href/redirect/browser_url/
  durable_url families.

Supported Connect authenticated-header cookie bridge remains `drop_supported`.
