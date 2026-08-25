# Hedron `v0.66.0` HDJ parity acceptance

Phase 0.66 is governed by [RFC-0093](../rfcs/RFC-0093-HDJ-PARITY-AND-REGISTRY-INTEGRATION.md),
D-111, and D-112. The predecessor is `v0.65.0`.

## Verified HDJ foundation gates

- [x] `CONTRACT-066` — scope, authority, non-goals, and deferrals are explicit.
- [x] `BINDING-066` — immutable app binding and cross-app refusal pass.
- [x] `REGISTRY-066` — component/asset/theme/style projection passes.
- [x] `INTERACTION-066` — logical-ID views/forms/catalog/schema/bundles pass.
- [x] `CONTEXT-066` — explicit HTMX and render trace facts pass.
- [x] `PROVIDER-066` — first-party provider manifests and declaration checks pass.
- [x] `STYLE-066` — application styling facts are useful and source-redacted.
- [x] `SECURITY-066` — no manifest execution, ambient request, or cross-app capability passes.
- [x] `COMPAT-066` — existing explicit component/asset HDJ construction passes unchanged.
- [x] `DOCS-066` — public API and migration examples describe the real render path.
- [x] `PKG-066` — coordinated metadata, typed facade, and clean package checks pass.
- [x] `REGRESS-066` — full Jinja and relevant adapter/component regressions pass.

## Planned open-issue gates

- [ ] `DATA-AUDIT-066` — #718 mutations remain atomic when the audit hook fails.
- [ ] `HTMX-JSON-066` — #719 approved HTMX headers never emit non-standard JSON.
- [ ] `MAP-NUMERIC-066` — #720 map view state rejects non-finite browser payload values.
- [ ] `CLAIM-REDACT-066` — #721 null raw claims redact safely.
- [ ] `THEME-ARCHIVE-066` — #722 theme package extraction enforces archive budgets.
- [ ] `ALTAIR-JSON-066` — #723 Altair payloads remain standards-valid with non-finite input.
- [ ] `PLOTLY-JSON-066` — #724 Plotly ndarray values serialize as JSON arrays.
- [ ] `PIN-CEILING-066` — #725 generated future-major dependency ceilings are valid.
- [ ] `WS-PRODUCER-066` — #726 producer failures propagate without idle-timeout misreporting.
- [ ] `AUTH-RATE-066` — #727 non-finite rate-limit windows fail validation.
- [ ] `TYPE-MEASURE-066` — #728 bounded measure props and recipes pass presentation evidence.
- [ ] `TYPE-EFFECT-066` — #729 safe editorial effects pass fallback and accessibility evidence.
- [ ] `CONTEXT-PRESENT-066` — #730 contextual typography variants pass component coverage.

The machine-readable ownership and status source is
[`open-issues-066.toml`](open-issues-066.toml). During intake, #613 and #140 were closed because their
fixes and focused regressions were already present on `main`. The 0.66 phase is not release-ready
until all thirteen unchecked rows are Verified and their issues are closed with evidence.

## Explicitly Deferred

Dynamic dependencies, foreign Jinja execution, and installed-package HDJ namespaces remain
unsupported in the HDJ v1 render path. Their inventory types remain readable for deployment
inspection, but no 0.66 documentation describes them as executable.
