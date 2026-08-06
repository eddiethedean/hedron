# RFC-0044: HTMX shell primitives and public InteractionResult rendering

**Status:** Accepted
**Phase:** 0.17 (`v0.17.0`)
**Stability:** `beta`
**Evidence:** `SHELL-017`, `ASSERT-017`, `HEDDOC-017`
**Issues:** [#28](https://github.com/eddiethedean/hedron/issues/28),
[#29](https://github.com/eddiethedean/hedron/issues/29),
[#30](https://github.com/eddiethedean/hedron/issues/30),
[#35](https://github.com/eddiethedean/hedron/issues/35),
[#40](https://github.com/eddiethedean/hedron/issues/40),
[#15](https://github.com/eddiethedean/hedron/issues/15),
[#24](https://github.com/eddiethedean/hedron/issues/24)
**Related:** RFC-0009, RFC-0035, RFC-0039

## Summary

Ship first-class HTMX in-shell authoring primitives (`HtmxLink` / `NavLink`, `class_` / theme hooks
on content builtins, `OobHost` / `AttrHost`, `AppShell` / `MainPanel` with a document-or-fragment
view helper) and a stable public `InteractionResult` → Response conversion API that replaces
private `HedronRoute._convert_interaction_result` use. Also complete remaining catalog docs
(`error-codes.md` / `#15`) and Dialog/Tabs/Pagination/Lazy markup asserts (`#24`; Toast already
shipped in 0.15).

## Motivation and background

Authenticated shell apps (e.g. Access Registry patterns) currently drop to `html.a(**hx_attrs(...))`
because `Link` rejects HTMX attributes, lack OOB host roots, and call private conversion helpers
when they own CSRF/headers/region policy. These are DX/contract gaps adjacent to the 0.17 dashboard
theme and already issue-owned on the roadmap.

## Proposed design

### Navigation and shell

- `HtmxLink` / `NavLink`: `href` remains `SafeUrl` (`UrlPurpose.NAVIGATION`); HTMX attrs follow the
  same SafeUrl purpose rules as `html.a`; optional active/current styling; works under `Nav`.
- `class_` / theme hooks on content builtins (`#29`) for shell styling without raw HTML escape.
- `OobHost` / `AttrHost` (`#30`): stable OOB fragment roots and attribute hosts.
- `AppShell` / `MainPanel` (`#40`): document-or-fragment view helper for in-shell panel swaps
  composing with existing `#26` PE dual-path asserts.

### Public render_interaction

Expose a documented API (e.g. `hedron.responses.render_interaction`) that converts
`InteractionResult` → Starlette/FastAPI `Response`, honoring caller-supplied `InteractionPolicy`
and `SecurityPolicy` (including `csrf_enabled=False` / custom headers). Deprecate reliance on
`HedronRoute._convert_interaction_result` in changelogs. Optionally auto-detect
`InteractionResult` returns from handlers using the app’s registered policy.

### Docs and asserts (phase leftovers)

- Expand `error-codes.md` (or split by domain) so public docs match `hedron_core.codes`; CLI/
  Explorer/SARIF share the same list (`HEDDOC-017`, `#15`).
- Component-aware markup asserts for Dialog, Tabs, Pagination, and Lazy/Loading (`ASSERT-017`,
  `#24`). Toast asserts remain 0.15 evidence — not re-owned by 0.17.

## Alternatives considered

1. **Extend `Link` with optional HTMX bag only.** Acceptable variant of NavLink; RFC allows either
   a dedicated component or typed `htmx=` on `Link` if SafeUrl rules are identical.
2. **Leave private conversion as the escape hatch.** Rejected — upgrade landmine for apps that own
   security policy.
3. **Defer shell DX to 0.20.** Rejected — issues already mapped to 0.17; STATUS advertises them.

## Security implications

NavLink/OobHost must reject unsafe targets/selectors consistent with `InteractionPolicy`.
`render_interaction` must not weaken fail-closed region authorization when apps pass custom
policies. Document that owning CSRF does not imply owning region authz defaults incorrectly.

## Accessibility implications

AppShell/MainPanel and NavLink active states must preserve landmark semantics and focus on panel
swap; PE dual path remains required.

## Performance implications

Negligible; shell primitives are ordinary components. Assert helpers must stay cheap in unit tests.

## Testing strategy

NavLink select + select-oob + push-url; OobHost roots; AppShell document vs fragment; 
`render_interaction` toast OOB / redirect / reswap / undeclared-target rejection; Dialog/Tabs/
Pagination/Lazy asserts. Gates: `SHELL-017`, `ASSERT-017`, `HEDDOC-017`.

## Compatibility and migration

Additive builtins and public API. Changelog notes deprecation of copied private conversion paths.
Issue `#24` title/docs drop Toast from the remaining work list.

## Open questions

None blocking Acceptance. Exact symbol name (`render_interaction` vs `interaction_response`) may
match adapter naming during implementation.

## Acceptance criteria

- Documented public conversion API; tests cover policy/security overrides.
- NavLink/AppShell/OobHost documented as recommended shell panel-navigation pattern.
- `error-codes.md` aligns with registered codes; Dialog/Tabs/Pagination/Lazy asserts land.
