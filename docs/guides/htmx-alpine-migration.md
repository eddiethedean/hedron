# HTMX/Alpine 1.1 migration guide

This guide describes the compatibility transition from the Hedron 1.0 interaction surface to the
smaller 1.1 implementation. The 1.0 Stable package boundary includes `hedron-core`, `hedron`,
`edron`, `hedron-data`, `hedron-charts`, and `hedron-maps`. Host and vendor-adapter packages
remain Beta and are not part of the stable platform promise.

## Migration table

| 1.0 or legacy path | 1.1 replacement | Transition behavior |
|---|---|---|
| `Hx(...)` | `HtmxAttrs(...)` | `Hx` is an outerHTML-default compatibility wrapper; new code should use the generic name. |
| `Interaction.to_attributes()` | `Interaction.to_lowering().to_attributes()` | The old method delegates to typed Alpine/HTMX lowering. |
| A standalone local interaction that assumes an ancestor `x-data` | `Interaction.local(..., state={...})` | Explicit state emits a self-contained Alpine scope. For 0.67 compatibility, omitted self-owned state is initialized to `False` for each declared key (or the action name when no key is declared). |
| Raw `hx-*` dictionaries in components | `HtmxAttrs(...).as_html_attrs()` | Maintained built-ins use one validated builder. Raw kwargs remain an input compatibility boundary. |
| Alpine bindings on basic text/select/check/radio controls | `enhance="native"` | Native mode is available now; the legacy default remains during the 1.1 transition. |
| Alpine animated disclosure | `Expander(..., enhance="native")` | Native mode renders `<details>/<summary>`; Alpine collapse remains opt-in. |
| `data-hedron-after-load` follow-up request | Declarative hidden sentinel with `hx-trigger="hedron:after-load ..."` | The marker is retained for migration compatibility; Hedron no longer calls `htmx.ajax()`. |
| Direct `ComponentRef.hx_attrs()` | `ComponentRef.htmx_attributes()` | The old method returns stringified values as a compatibility wrapper. |
| Eager browser assets | `Hedron(..., demand_driven_assets=True)` | Opt in during 1.1; 2.0 may make demand-driven loading the default. |

## Ownership rules

- Native HTML owns form submission, validity, disclosure, and baseline keyboard behavior.
- HTMX owns declared requests and server HTML placement.
- Official Alpine owns disposable local presentation inside an explicit scope.
- Hedron owns server truth and the lifecycle handoff only; it does not initiate follow-up requests.

Do not store authorization, secrets, or authoritative domain state in Alpine state. Do not use
`x-on` or `hx-*` attributes to create a second request path around the declared interaction.

## Release checks

Run the repository checks with the pinned environment:

```text
bash scripts/ci_checks.sh all --python 3.12 --all-browsers --release-gate
```

The release flag makes skipped browser, dependency, and optional-backend evidence fail the run.
Without it, those checks are reported as unsupported evidence so a local convenience run cannot be
mistaken for a complete release verification.
