# REVIEW-029 redacted security report

**Date:** 2026-08-11
**Baseline:** Published `v0.28.2` mount/CSRF/redirect contracts
**Package:** `hedron-workbench` `0.30.0`
**Reviewer role:** maintainer-led, independent of the feature-authoring pass
**Method:** adversarial pytest corpus + source review of resolver, middleware, runner, CLI, redaction

## Findings

| ID | Severity | Status | Summary |
|---|---|---|---|
| REV-029-001 | Medium | Mitigated | Encoded absolute request-target decode could follow `//` or `..` — rejected before strip |
| REV-029-002 | Medium | Mitigated | Cookie `Path` is construction-time preferred; launcher exports `HEDRON_ROOT_PATH` before import; outer adapter may repair only Hedron-owned `Path=/` cookies from a validated request mount |
| REV-029-003 | Medium | Mitigated | `rserver-url` exec requires an absolute path and never uses a shell |
| REV-029-004 | Low | Mitigated | Compatibility aliases warn (`HED-WB-0008`); namespaced env wins |
| REV-029-005 | Low | Mitigated | In-process serve rejects reload/multi-worker; launcher may exec Uvicorn's supervisor with the inherited listener (mutually exclusive; excluded from Supported) |
| REV-029-006 | Info | Mitigated | Session IDs, license-shaped tokens, and token-like query keys are redacted in check JSON and debug logs |
| REV-029-007 | Info | Mitigated | `RS_SERVER_URL` and Connect base headers do not grant trust or auto-wrap |
| REV-029-008 | Info | Mitigated | Mount-prefixed `Location` uses Hedron `prefix_local_path` once; traversal mounts fail closed |
| REV-029-009 | Medium | Mitigated | Discovery stdout/stderr is bounded while read; diagnostics redact credentials and assignments |
| REV-029-010 | Medium | Mitigated | Uvicorn/Hedron share an exact proxy IP allowlist; wildcard trust and implicit external binds fail closed |

## Trust-boundary notes

- Authority in an encoded absolute target is not used as an origin or redirect target.
- Untrusted `rstudio-connect-app-base-url` / `X-Forwarded-Prefix` are ignored unless Hedron already trusts the peer.
- Bind defaults to `127.0.0.1`; external binds require explicit opt-in.
- Uvicorn and Hedron consume the same exact-IP proxy allowlist; `*` is rejected.
- Importing `hedron_workbench` does not wrap apps.

## Residual risk

The launcher still configures cookie paths before import. If ASGI `root_path`
only arrives with a request, the outer adapter now repairs `Path=/` for the
bounded set of Hedron-owned cookies. It does not rewrite unknown third-party
cookies. Tests cover session and CSRF continuity through the real Connect mount.

## Disposition

See [`DISPOSITION.toml`](DISPOSITION.toml). `critical_high_open = false`.
