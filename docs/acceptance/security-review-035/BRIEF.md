# Security review brief — phase 0.35 (whole-fleet closure)

**Package / train at cut:** Hedron `v0.35.0` fleet audit  
**Owning RFC:** [RFC-0068](../../rfcs/RFC-0068-WHOLE-FLEET-CLOSURE.md)  
**Gate:** `SUPPLY-035` / fleet honesty (cross-cutting)  
**Tracking:** [#91](https://github.com/eddiethedean/hedron/issues/91)

## Scope

Independent review of the **fleet closure** surface:

- Ambiguous or unowned Alpha maturity labels vs published artifacts
- Experimental surfaces accidentally treated as Supported in solver defaults
- Supply-chain completeness (license, SBOM, provenance) for every published channel
- PRESENT-034 deferred presentation status honestly reflected in docs/inventory
- No abandoned packages retained solely to enlarge the published fleet

## Out of scope

- Renaming the cut to Hedron `1.0` or commercial SLA/WCAG/VPAT claims
- Reopening `polling_only` live-transport disposition
- Per-satellite deep re-reviews already closed in 0.26–0.34 (reuse prior packets)

## Required artifacts at cut

- `REDACTED_REPORT.md` — findings with severity and disposition
- `DISPOSITION.toml` — machine-checked closure of critical/high items

## Review questions

1. Does every publishable package/tool have an owner and a terminal or future disposition?
2. Can an adopter install a Supported pin and silently pull Experimental authority?
3. Are SBOM/provenance/license inventories complete for PyPI, npm, and Maven publish paths?
4. Do docs and the fleet inventory agree on Gradio/MCP/notebook/Alpha tooling labels?
5. Is PRESENT-034 status explicit (deferred / audited) rather than silently claimed Supported?

## Status

**Planned** — maintainer-led or external review completes before cut; BRIEF-only is sufficient
during Stage 0 `--allow-planned` refine.
