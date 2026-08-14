# Security review — phase 0.37 (redacted)

**Package / train at cut:** Hedron `v0.37.0` + Alpha `hedron-elements` `0.37.0`  
**Owning RFC:** RFC-0060 · **Gate:** `AT-037` / `REGRESS-037` · **Tracking:** #93  
**Reviewer:** maintainer-led (2026-08-14)

## Findings

No open critical or high findings for 0.37 scope.

| ID | Severity | Summary | Disposition |
|---|---|---|---|
| EL-037-01 | info | Form authority remains server-owned; ElementInternals is a hint only | accepted |
| EL-037-02 | info | `data-hx-*` aliases now share EVAL-020 / SafeUrl policy (#230) | accepted — fixed |
| EL-037-03 | info | Element markup rejects `hx-on` / `javascript:` (#237) | accepted — fixed |
| EL-037-07 | info | Element markup rejects `style=` except layout allowlist and `vbscript:`/`data:` URLs (#244) | accepted — fixed |
| EL-037-04 | low | Gesture catalog intents forbid raw URLs/selectors | accepted — documented |
| EL-037-05 | info | MCP Origin fail-closed without allowlist (#232); bounded body read (#233) | accepted — fixed |
| EL-037-06 | info | Flask production session cookies set Secure/SameSite (#231) | accepted — fixed |

## Adversarial coverage exercised

- HTMX eval bypass via `data-hx-*` attributes
- Markup injection via element attribute values
- Directory upload NUL and traversal paths (#234)
- MCP cross-origin POST with missing allowlist
- Oversized MCP request bodies before JSON parse

## Residual risk

Alpha `hedron-elements` remains incubator until phase 0.42. Adopters must pin `>=0.37.0,<0.38` and treat InteractionState/gesture catalog APIs as evolving.
