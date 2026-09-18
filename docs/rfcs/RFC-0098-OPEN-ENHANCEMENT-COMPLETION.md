# RFC-0098: Open enhancement completion and complementary application features

**Status:** Accepted, implemented, and verified in `v1.1.0`
**Target:** Hedron `1.1.0`
**Baseline:** Stable `v1.0.17`; implemented source `v1.1.0`
**Implementation:** [OPEN_ENHANCEMENTS_1_1](../implementation/OPEN_ENHANCEMENTS_1_1.md)
**Acceptance:** [RELEASE_1_1](../acceptance/RELEASE_1_1.md) ·
[release-gate-1.1.toml](../acceptance/release-gate-1.1.toml)

## Outcome and scope

Phase 1.1 implements the open enhancement backlog and the complementary features needed to use
those enhancements together in complete application flows. The 2026-09-18 GitHub snapshot contains
20 open feature requests: #889–#893, #913–#919, and #939–#946. Issues #889 and #890 are included by
their feature-request content despite having no enhancement label. The exact inventory and
implementation order live in the implementation plan; all 20 are required scope.

The former 1.1 testing phase moves intact to 1.2 under RFC-0097. The former 1.2–1.7 phases move
to 1.3–1.8. This phase uses existing render, AppScenario, state-matrix, and Playwright facilities;
the computed-style work in #915 extends those facilities without depending on the future managed
browser harness.

## Design and authority

1. Reuse existing presentation, theme, form, navigation, action, asset, URL, and testing contracts.
   Freeze exact additive APIs and package ownership before implementation; issue sketches are not
   final public spellings.
2. Keep identity and data providers independent of domain packages. FastAPI/framework security and
   backing-service authorization remain authoritative. UI visibility never grants access.
   AuthMate, ShuETL, Datdex, and fastapi-pagination are compatibility targets or optional adapters.
3. Compose secret updates, validation, help, alignment, and unsaved guards into one settings flow.
   Stored secrets never reach client output; failed submissions never echo replacement secrets.
   Only authoritative save/reset outcomes advance the clean baseline.
4. Compose chrome, branding, process illustrations, and color-mode presentation through finite
   Python configuration and theme tokens. Preserve existing defaults and the current HTMX/Alpine
   lifecycle authority. Logical geometry, focus, safe fallbacks, and actual computed styles are
   part of the contracts.
5. Share application asset provenance between sealed builds, runtime verification, and browser
   conformance. Request-bound Posit URL generation reuses installed deployment trust policy.
   Rejected interaction targets can reach trusted error sinks without weakening authorization.

Complementary scope is explicit: coherent form commit/reset and redaction behavior; reusable
authorized collection states and URL restoration; shared shell geometry and presentation metadata;
and a packaged deployment/conformance reference flow. These complete the new features rather than
introducing a new router, application store, identity system, ORM, build framework, or test runner.
Additional ideas require a recorded scope amendment with an owning issue and acceptance evidence.

## Alternatives considered

Keeping testing first would delay the requested adopter enhancements. Scattering the backlog
across later theme phases would leave dependent application flows incomplete. Implementing issue
sketches verbatim would bypass current-source reconciliation and shared contracts. A new browser
harness for #915 would duplicate RFC-0097. This phase instead groups the full backlog, freezes
coherent additive contracts, and extends existing testing facilities.

## Security and accessibility implications

Trusted error destinations and deployment prefixes come from framework/policy configuration,
never rejected request targets or unchecked headers. Provider decisions shape presentation only;
routes and services independently enforce authorization. Collection counts, caches, previews,
manifests, and failure evidence cannot disclose another principal's data or credentials.

Labels, linked error summaries, required help, write-only editing, guard confirmations, icon-only
controls, and ordered flows retain semantic HTML and keyboard/focus behavior. Failed-submit focus
recovery is scoped to the initiating form. RTL, zoom, forced colors, reduced motion, no-JS behavior,
and light/dark contrast receive evidence; this phase does not make a general WCAG claim or replace
the later compensated human-evaluation phase.

## Performance and testing

Freeze measured limits for collection page sizes, provider requests, dirty scopes, header observers,
asset collection, and browser-matrix concurrency/artifacts. Collections cannot materialize the full
dataset. Dispose listeners/observers on replacement; abort or ignore obsolete requests. Deterministic
manifests and bounded conformance fixtures are required, without a build-system scalability rewrite.

Use render and AppScenario tests for contracts, Playwright for user-agent effects, computed-style
relationships and geometry for presentation, synthetic secret/adversarial fixtures for trust
boundaries, and clean-package tests for optional imports and deployment. The acceptance packet
defines required results. Freeze exact matrices/budgets before verification; a missing browser is
incomplete evidence. Issue closure requires linked implementation and passing evidence.

## Compatibility and migration

Existing 1.0 defaults, string help/errors, testing imports, and framework authority remain compatible.
New policies are opt-in; changed Beta surfaces require documented migration. The implementation and
acceptance indexes point to the relocated testing packet, with unique `*-120` testing gates and
`*-110` enhancement gates. No current release versions, pins, tags, or production defaults change
during this planning revision. Document feature installation and rollback before the release cut.

## Open questions for scope freeze

- Exact public spellings, package ownership, adapter packaging, and capability maturity.
- Form commit/reset signals, provider uncertainty behavior, and bounded pagination/URL schemas.
- Header measurement ownership, presentation-manifest additions, and stylesheet parity criteria.
- Named maintainers, browser/host/dependency matrices, and measured resource/performance budgets.

## Acceptance criteria and completion policy

All inventory issues and required complementary work must be implemented, documented, and verified
before the Phase 1.1 release cut. An explicit scope amendment is required to move any required item;
an evaluation or non-admission decision alone does not complete this implementation phase.
Issue closure follows verified implementation and linked evidence. Package versions, support claims,
release facts, and current 1.0 pins stay unchanged during planning. Every new capability receives
an explicit maturity decision, compatibility evidence, and proportionate security, accessibility,
browser, packaging, and rollback checks.
