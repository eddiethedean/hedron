# REVIEW-028 security review brief

**Baseline:** Published `v0.27.0` Supported inventories
([production-grade-inventory-028.toml](../production-grade-inventory-028.toml)).
**Packages:** `hedron-charts`, `hedron-native`.
**Owning decision:** D-056 / RFC-0059.

## Trust boundaries in scope

1. Static SVG/PNG and beginner-chart HTML emission (escaping, TrustedHtml sinks)
2. Accessible alternatives and payload budgets for Supported charts
3. CSP-safe local asset pins; no unpinned CDN in Supported configuration
4. Interactive/optional adapter quarantine from production defaults
5. Native escape acceleration malformed-input handling and fallback injection
   (absence, import failure, unsupported platform, runtime disable)

## Out of scope

- Commercial SLA / certification claims
- Graduating Plotly / Altair / optional adapters to Supported
- Making native required for correctness
- MCP / Gradio / conformance tooling (later phases)
- Desktop-shell / `pywebview` recipes

## Adversarial suite

To be attached under `tests/unit/test_review_028_adversarial.py` before
`CHARTS-028` / `NATIVE-028` / `PKG-028` cut evidence.

## Methodology

Structured maintainer-led review of the frozen CONTRACT-028 inventory against the
boundaries above, independent of the feature-authoring pass for this packet.
Findings and dispositions will be recorded in `DISPOSITION.toml` and summarized
in `REDACTED_REPORT.md` at cut. External commercial re-review remains optional
follow-up.

## Packet status

**Planned.** Only this brief is required while gates remain Planned
(`python scripts/verify_pkg_28.py --allow-planned`). Full
`REDACTED_REPORT.md` + `DISPOSITION.toml` (`critical_high_open = false`) are
required at `v0.28.0` cut without `--allow-planned`.
