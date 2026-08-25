# Security control plane APIs (0.56)

Phase 0.56 adds opt-in `beta` security control-plane contracts under
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
- `hedron.security_plane.SignedIntent` / `SecurityKeyring` — signed intent helpers
- `hedron.security_plane.SecurityEvent` — structured security events
- Conformance: `hedron_conformance` security profile (`hedron-security-1`)
- CLI: `hedron security-check`

Compatibility: existing `SafeUrl`, `TrustedHtml`, `Secret`, CSRF, and 0.55
replay/capability/upload APIs retain documented paths and delegate to shared
authorities where applicable.

Pin and maturity follow the living **0.64.x** train; new symbols are `beta` for
their first release.

## Example

```python
from hedron import Hedron
from hedron.security_plane import RequestBudget, RequestBudgetLimits, SecurityContext

app = Hedron(title="Admin", security="standard", session_secret="replace-me", explorer="off")


@app.screen("/", title="Home")
def home():
    # Opt-in building blocks for policy composition / diagnostics.
    ctx = SecurityContext(application_id="admin", profile_name="standard")
    budget = RequestBudget(limits=RequestBudgetLimits(body_bytes=1_000_000))
    _ = (ctx, budget)
    return "Security plane imports are available for policy composition."
```

Prefer the [security guide](../guides/security.md) for CSRF profiles and headers.
Control-plane symbols are `beta` — pin the train and read the RFC before relying on them.
