# REVIEW-029 security review brief

**Baseline:** Published `v0.28.2` Supported mount/CSRF/redirect contracts.
**Package:** `hedron-workbench`.
**Owning decision:** D-057 / RFC-0062.

## Trust boundaries in scope

1. Encoded absolute request-target decoding (scheme, authority not trusted)
2. Header/origin trust (`RS_SERVER_URL`, forwarded prefix/host/proto, Connect base)
3. Open redirects and traversal in mount-prefixed Location
4. Cookie Path scoped at construction via `HEDRON_ROOT_PATH`
5. Subprocess/binary selection and bounded output (absolute argv, no shell)
6. Loopback bind exposure and unified exact-IP `forwarded_allow_ips`
7. Debug/check JSON redaction (session/project/token/license)
8. Import timing (no wrap before env export)

## Out of scope

- Flask / Django adapters
- Posit Workbench product security / licensing
- Treating Workbench login as Hedron identity
- Commercial SLA / certification

## Adversarial suite

`tests/security/test_workbench_adversarial.py`

## Methodology

Structured maintainer-led review independent of the feature-authoring pass.
Findings in `DISPOSITION.toml` and `REDACTED_REPORT.md` at cut.

## Packet status

**Verified** — see `REDACTED_REPORT.md` and `DISPOSITION.toml` (`critical_high_open = false`).
