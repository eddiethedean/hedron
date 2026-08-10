# REVIEW-027 redacted security review report

**Gate evidence:** PARITY-027 / PKG-027  
**Baseline:** Published `v0.26.0`  
**Packages:** `hedron-data`, `hedron-flask`, `hedron-django`, `hedron-jinja`,
`hedron-extras`  
**Date:** 2026-08-10  
**Method:** Structured maintainer-led review of the frozen CONTRACT-027 inventory
against ROADMAP satellite trust boundaries (data export bounds, adapter
fragment/OOB/CSRF under host sessions, HDJ sinks/CSP, extras quarantine,
portable parity), backed by the adversarial CI suite.

## Executive summary

No open **critical** or **high** findings remain for the declared Supported
satellite inventories. Experimental live helpers and specialty UI remain outside
the production-grade claim. Explorer process-local audit (`REV-026-003`) stays
an accepted Explorer-owned risk and is not expanded into this packet.

## Boundary results

| Boundary | Result |
|---|---|
| Data query/export bounds | Spreadsheet and source paths remain explicit; silent dataframe extras stay excluded |
| Adapter fragment/OOB/CSRF | Host-owned sessions; undeclared targets fail closed; CSRF still required on FastAPI standard |
| HDJ sinks / prologue | Missing prologue rejected; v1 prologue required |
| Extras quarantine | Default `hedron_extras.__all__` excludes TerminalView/Joystick/DeviceBridge/CodeEditor |
| Portable parity | PAGE/FRAGMENT/header allowlists shared across FastAPI/Flask/Django Supported paths |

## Critical / high

All critical/high dispositions are **fixed** or **not applicable** (see
`DISPOSITION.toml`).

## Residual risk

`REV-026-003` Explorer audit buffer remains accepted_risk with Explorer ownership.
Plugin entry-point trust remains accepted_risk toward 0.29. They do not block the
production-grade label for the declared satellite Supported inventories.
