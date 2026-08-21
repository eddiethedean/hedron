# Implementation notes: phase 0.56 security control plane

**Decision/RFC:** D-097, refined by D-098 /
[RFC-0083](../rfcs/RFC-0083-SECURITY-CONTROL-PLANE.md)<br>
**Shared schema:** `hedron_core.security_plane`

## Consume shipped, do not fork (D-098)

Extend `SecurityPolicy`, `SafeUrl`/`TrustedHtml`/`Secret`, CSRF, 0.55
capabilities/replay/upload/CSP, and package egress validators. Do not introduce
parallel preset namespaces or duplicate validators.

## Stage 1 module map

| Module | Responsibility |
|---|---|
| `hedron_core.security_plane` | Public re-exports for control-plane types |
| `hedron_core.security_context` | Immutable `SecurityContext` |
| `hedron_core.sensitive` | `SensitiveLabel` / declassification |
| `hedron_core.trust` | Purpose compiler (`compile_trust`) |
| `hedron_core.egress` | `EgressPolicy` / decisions |
| `hedron_core.request_budget` | Nested `RequestBudget` ledger |
| `hedron_core.intent` / `hedron.intent` | `SignedIntent` + store binding |
| `hedron_core.keyring` | `SecurityKeyring` |
| `hedron_core.security_events` | Stable event codes |
| `hedron_conformance.security` | Portable security profile + fixtures |
| `hedron.cli.commands.security_check` | Offline posture CLI |
