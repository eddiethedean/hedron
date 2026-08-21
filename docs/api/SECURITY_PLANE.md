# Security control plane APIs (0.56)

Phase 0.56 adds opt-in `beta` security control-plane contracts under
`hedron_core.security_plane` (re-exported as `hedron.security_plane` for FastAPI
apps). See
[RFC-0083](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0083-SECURITY-CONTROL-PLANE.md).

## Public entry points

- `hedron_core.security_policy.SecurityPolicy` / `SecurityProfile` (composition + presets)
- `hedron_core.security_plane.SecurityContext`
- `hedron_core.security_plane.SensitiveLabel` / `SensitiveValue`
- `hedron_core.security_plane.compile_trust` / `TrustPurpose`
- `hedron_core.security_plane.EgressPolicy` / `EgressDecision`
- `hedron_core.security_plane.RequestBudget`
- `hedron_core.security_plane.SignedIntent` / `SecurityKeyring`
- `hedron_core.security_plane.SecurityEvent`
- Conformance: `hedron_conformance` security profile (`hedron-security-1`)
- CLI: `hedron security-check`

Compatibility: existing `SafeUrl`, `TrustedHtml`, `Secret`, CSRF, and 0.55
replay/capability/upload APIs retain documented paths and delegate to shared
authorities where applicable.

Pin and maturity follow the living train; new symbols are `beta` for the first
0.57 release.
