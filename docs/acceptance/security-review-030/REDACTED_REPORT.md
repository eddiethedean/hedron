# REVIEW-030 redacted security report

**Date:** 2026-08-12
**Baseline:** Published `v0.30.0` Hedron contracts; public `fastapi-workbench` `0.3.4` generic corpus
**Packages:** `fastapi-workbench` `1.0.0`, `hedron-workbench` `0.30.0`
**Reviewer role:** maintainer-led, independent of the feature-authoring pass
**Method:** adversarial pytest corpus + source review of resolver, middleware, runner, CLI, redaction, dependency boundary

## Findings

| ID | Severity | Status | Summary |
|---|---|---|---|
| REV-030-001 | Medium | Mitigated | Encoded absolute request-target decode could follow `//` or `..` — rejected before strip |
| REV-030-002 | Medium | Mitigated | Cookie `Path` is construction-time preferred; launcher exports root-path env before import; Hedron adapter may repair only Hedron-owned `Path=/` cookies |
| REV-030-003 | Medium | Mitigated | `rserver-url` exec requires an absolute path and never uses a shell |
| REV-030-004 | Low | Mitigated | Compatibility aliases warn (`FWB-0008` / `HED-WB-0008`); namespaced env wins |
| REV-030-005 | Low | Mitigated | In-process serve rejects reload/multi-worker; launcher may exec Uvicorn supervisor with inherited listener (excluded from Supported) |
| REV-030-006 | Info | Mitigated | Session IDs, license-shaped tokens, and token-like query keys are redacted in check JSON and debug logs |
| REV-030-007 | Info | Mitigated | `RS_SERVER_URL` and Connect base headers do not grant trust or auto-wrap |
| REV-030-008 | Info | Mitigated | `fastapi_workbench` has no Hedron imports; `hedron-workbench` declares bounded `fastapi-workbench` dependency |
| REV-030-009 | Medium | Mitigated | Discovery stdout/stderr is bounded while read; diagnostics redact credentials and assignments |
| REV-030-010 | Medium | Mitigated | Uvicorn and Workbench share an exact proxy IP allowlist; wildcard trust and implicit external binds fail closed |

## Trust-boundary notes

- Authority in an encoded absolute target is not used as an origin or redirect target.
- Untrusted `rstudio-connect-app-base-url` / `X-Forwarded-Prefix` are ignored unless already trusted.
- Bind defaults to `127.0.0.1`; external binds require explicit opt-in.
- Importing `fastapi_workbench` or `hedron_workbench` does not wrap apps.
- Generic Workbench behavior is testable with Hedron absent.

## Residual risk

Hedron construction-time cookie scoping remains preferred. If ASGI `root_path` only
arrives with a request, the Hedron outer adapter repairs `Path=/` for the bounded set
of Hedron-owned cookies. It does not rewrite unknown third-party cookies.

## Disposition

See [`DISPOSITION.toml`](DISPOSITION.toml). `critical_high_open = false`.
