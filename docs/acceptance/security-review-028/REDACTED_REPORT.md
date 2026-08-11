# REVIEW-028 redacted security review report

**Gate evidence:** CHARTS-028 / INTERACTIVE-028 / NATIVE-028 / SUPPLY-028 / PKG-028  
**Baseline:** Published `v0.27.0`  
**Packages:** `hedron-charts`, `hedron-native`  
**Date:** 2026-08-10  
**Method:** Structured maintainer-led review of the frozen CONTRACT-028 inventory
against ROADMAP charts/native trust boundaries (SVG/TrustedHtml sinks, CDN reject,
interactive Auto quarantine, asset pins, payload budgets, native malformed-input
and disable injection), backed by the adversarial CI suite.

## Executive summary

No open **critical** or **high** findings remain for the declared Supported
charts/native inventories. Plotly/Altair and optional visualization adapters remain
Experimental and outside production Auto defaults. Native acceleration remains
optional with Python-reference fallback under absence, import failure, unsupported
platform, and `HEDRON_NATIVE_DISABLE`.

## Boundary results

| Boundary | Result |
|---|---|
| Static SVG/PNG + beginner charts | Active SVG/CDN/callback reject; a11y tabular alternatives; payload budgets |
| Interactive quarantine | Plotly/Altair `maturity=experimental`; Auto skips without `as_=` |
| Asset pins | `RUNTIME_PINS` digests fail-closed for Experimental hosts; Supported path does not require them |
| Native escape / disable | Parity with Python reference; disable env forces Python path |
| Supply / offline | License inventory + SBOM notes + offline install rehearsal documented |

## Critical / high

All critical/high dispositions are **fixed** or **not applicable** (see
`DISPOSITION.toml`).

## Residual risk

Interactive browser hosts still require `window.Plotly` / `vegaEmbed` at mount time
even with vendored pins registered — apps must serve those assets when opting into
Experimental interactive charts. Human AT for charts remains out of scope for 0.28.
These do not block the production-grade label for the declared Supported inventories.
