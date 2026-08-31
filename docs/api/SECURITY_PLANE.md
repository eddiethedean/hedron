# Security control plane APIs

Available as `beta` contracts on 1.0; introduced in phase 0.56 under
`hedron_core.security_plane` (re-exported as `hedron.security_plane` for FastAPI
apps). See
[RFC-0083](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0083-SECURITY-CONTROL-PLANE.md).

## Public entry points

- `hedron.security_plane.SecurityContext` — request/subject security context
- `hedron.security_plane.RequestBudget` / `RequestBudgetLimits` — nested resource ledger
- `hedron.security_plane.SecurityPolicy` / `SecurityProfile` — composition + presets
- `hedron.security_plane.SensitiveLabel` / `SensitiveValue` — sensitivity labeling
- `hedron.security_plane.compile_trust` / `TrustPurpose` — trust compilation
- `hedron.security_plane.EgressPolicy` / `EgressDecision` — outbound allow/deny
- `hedron.security_plane.fetch_with_policy` / `StdlibEgressTransport` —
  connection-bound HTTP fetches
- `hedron.security_plane.SignedIntent` / `SecurityKeyring` — signed intent helpers
- `hedron.security_plane.SecurityEvent` — structured security events
- Conformance: `hedron_conformance` security profile (`hedron-security-1`)
- CLI: `hedron security-check`

Compatibility: existing `SafeUrl`, `TrustedHtml`, `Secret`, CSRF, and 0.55
replay/capability/upload APIs retain documented paths and delegate to shared
authorities where applicable.

Pin and maturity follow the current **1.0.x** train; new symbols are `beta` for
their first release.

## Example

```python
from hedron import Hedron, Page
from hedron.security_plane import RequestBudget, RequestBudgetLimits, SecurityContext

app = Hedron(title="Admin", security="standard", session_secret="replace-me", explorer="off")


@app.page("/")
def home():
    # Opt-in building blocks for policy composition / diagnostics.
    ctx = SecurityContext(application_id="admin", profile_name="standard")
    budget = RequestBudget(limits=RequestBudgetLimits(body_bytes=1_000_000))
    _ = (ctx, budget)
    return Page("Security plane imports are available for policy composition.", title="Home")
```

Prefer the [security guide](../guides/security.md) for CSRF profiles and headers.
Control-plane symbols are `beta` — pin the train and read the RFC before relying on them.

## Outbound HTTP

`fetch_with_policy` is the server-fetch authority. It re-resolves and revalidates
every redirect, verifies the connected peer, owns retry/redirect accounting, and
enforces encoded/decompressed response limits. The concrete transport never
follows redirects or decompresses responses on its own.

```python
from hedron.security_plane import EgressPolicy, StdlibEgressTransport, fetch_with_policy

policy = EgressPolicy(
    allowed_schemes=frozenset({"https"}),
    allowed_hosts=frozenset({"api.example.com"}),
    allowed_origins=frozenset({"https://api.example.com"}),
    allowed_ports=frozenset({443}),
    expected_content_types=frozenset({"application/json"}),
    response_budget_bytes=1_000_000,
    decompressed_budget_bytes=2_000_000,
)
body = fetch_with_policy(
    "https://api.example.com/v1/status",
    policy=policy,
    transport=StdlibEgressTransport(),
)
```

An injected `EgressTransport` receives only a completed decision and must report
the observed peer. It cannot bypass URL, redirect, peer, content, deadline, or
budget evaluation. `assert_ssrf_safe` remains a compatibility preflight helper;
validating a URL and then opening it with another client is not safe against DNS
rebinding.
