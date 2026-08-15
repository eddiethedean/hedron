# Default presentation quality plan (0.33+)

**Status:** Planned cross-cutting program for phases 0.33–0.42.
**Roadmap owner:** [Default presentation quality program](../ROADMAP.md#default-presentation-quality-program-033-cross-cutting).  
**Primary implementation surface:** `hedron-core` default theme, bundled stylesheet, semantic
component markup, scaffolds, Component Explorer, reference application, and browser conformance.

## Purpose

A new application created with `Hedron(default_styles=True)` should look deliberate and
production-ready before the application author writes CSS. The current baseline is accessible and
functional, but a complete account or administration application still needs substantial custom
presentation work to establish hierarchy, shell chrome, responsive containment, polished forms,
and coherent loading, empty, error, and recovery states.

This plan turns the qualities proven in a visually reviewed account-management application into
Hedron defaults. It does not copy that application's branding or make Hedron an identity product.
It extracts the reusable visual and interaction contracts so the same quality is available to a
fresh CRUD, administration, dashboard, or account application out of the box.

## Product contract

The refreshed default presentation MUST:

- remain ordinary semantic HTML with native form, table, link, dialog, and navigation behavior;
- work with full-page responses, HTMX fragments, history restoration, and JavaScript disabled;
- provide first-class light, dark, forced-colors, reduced-motion, print, zoom, and reflow behavior;
- use public theme tokens and additive application override layers rather than private selectors;
- avoid page-level horizontal overflow at supported viewport widths; wide data remains available in
  an explicit contained scroller;
- preserve `default_styles=False` as the fully custom-canvas escape hatch;
- keep security, authorization, account state, and recovery-token validity application-owned; and
- treat visual quality as tested behavior, not as documentation screenshots alone.

“Production-ready” here describes presentation quality and predictable behavior. It is not a claim
that a generated application is secure, compliant, branded, or complete without application-owned
policy and content.

## Validated problems to absorb into Hedron

The reference visual pass found recurring framework-level issues that should not require app CSS:

1. **Shell hierarchy:** a usable app needs a cohesive header, bounded content canvas, responsive
   side navigation, main panel, and footer—not isolated styled controls on a padded body.
2. **Composite spacing:** cards nested in tabs or shell regions can lose the padding that makes
   headings, help text, and controls readable.
3. **Grid containment:** table and lazy-result descendants can impose min-content width on a grid,
   causing clipping instead of a contained horizontal scroller.
4. **Responsive breakpoints:** a two-column administration layout must collapse based on available
   content width before its directory and action controls become cramped.
5. **Mobile navigation:** the current destination in an overflowing horizontal nav must be visible
   on initial render, history restoration, and fragment navigation.
6. **Motion timing:** full-page content must not begin transparent. Entry motion belongs only to a
   newly swapped region and must disappear under reduced-motion preferences.
7. **Public-flow composition:** register, sign-in, reset, verification, invitation, success, and
   invalid-link pages need a centered, responsive card pattern with clear context and recovery
   actions. Hedron supplies the pattern; the application supplies the policy and words.
8. **State completeness:** loading, empty, success, validation, expired/unavailable, destructive
   confirmation, and retry states need the same visual care as the happy path.

## Target default experience

### Visual foundation

- Refresh the default neutral/accent palette, typography scale, radii, borders, focus ring, shadows,
  and spacing rhythm as a coherent token set rather than component-local values.
- Keep system light/dark selection and explicit `data-theme` modes. Both modes must meet the same
  contrast and state-distinction requirements.
- Use restrained depth and gradients only where they improve hierarchy. Meaning may never depend on
  translucency, color, animation, or a backdrop-filter implementation.
- Define density and content-width tokens so forms and data-heavy surfaces can be compact without
  forking the visual system.

### Application chrome and page composition

- Give `AppShell`, its navigation region, and `MainPanel` complete default layout and responsive
  styling, including sticky desktop navigation and an overflow-safe mobile navigation row.
- Add documented composition recipes for public/auth, standard application, settings, and
  administration pages using existing semantic components where possible.
- Introduce a new component only when a stable semantic or behavioral contract is missing. Do not
  create components whose only purpose is a margin or color.
- Provide page-heading, panel-heading, status-summary, action-row, centered-card, split-form, and
  master/detail recipes through documented classes, variants, or small semantic components.

### Surfaces, forms, and data

- Make `Card`, tabs, dialogs, alerts, toasts, loading/error states, and nested panels share one
  spacing and elevation model.
- Give inputs, labels, help, validation, password affordances, primary/secondary/destructive actions,
  and field groups consistent alignment and touch targets.
- Make tables and data surfaces width-safe inside Grid, Card, Lazy, and fragment regions. Preserve
  headers and actions without forcing the page viewport wider than the shell.
- Define responsive rules using container queries where they improve reusable composition, with
  media-query fallbacks where the supported-browser contract requires them.

### Interaction polish

- Keep initial full-page content fully visible. Apply optional entry motion only after a successful
  fragment swap and only to the swapped region.
- Reveal the active item in horizontally overflowing navigation without moving keyboard focus or
  making scroll animation a correctness dependency.
- Preserve focus, title, current-page state, error announcements, and action availability across
  fragment replacement and history restoration.
- Give pending actions stable dimensions and visible `aria-busy` treatment without layout shift.

## Reference gallery

Hedron will maintain a framework-owned visual gallery that renders with no application stylesheet.
At minimum it includes:

- public sign-in and account-request layouts;
- forgot/reset forms plus success and invalid/unavailable-link recovery states;
- profile/settings forms and identity summary;
- security tabs with password, token, session, and activity surfaces;
- user directory plus invitation form at wide, intermediate, and narrow widths;
- audit filters and a wide table inside lazy/fragment regions;
- empty, loading, error, retry, validation, toast, dialog, and destructive confirmation states; and
- long labels, long email-like identifiers, translated-copy expansion, missing optional content,
  and large browser text.

These are presentation fixtures, not an authentication implementation. Example data is synthetic,
and no fixture implies that Hedron owns user persistence, permissions, or email delivery.

## Phase allocation

| Phase | Planned delivery |
|---|---|
| **0.33** | Freeze the gallery and visual contract; inventory current default CSS/markup; add geometry assertions; fix low-risk containment, composite-spacing, initial-opacity, and mobile-current-nav defects; publish the refreshed visual system as an opt-in preview if compatibility evidence is incomplete. |
| **0.34** | Make the refreshed presentation the `default_styles=True` experience; ship updated scaffolds, reference-app adoption, migration notes, classic/custom escape guidance, and clean-wheel visual evidence. |
| **0.35** | Audit the refreshed defaults in the whole-fleet inventory, supported package combinations, documentation, and supply evidence. |
| **0.36** | Bind `hedron-elements` ABI, SSR fallback, state ownership, and HTMX lifecycle to the same tokens, focus, surface, and no-JavaScript visual contract. |
| **0.37** | Complete form-associated controls, validation, async interaction states, dialogs, gestures/overlays, and generic public/recovery composition patterns. |
| **0.38** | Establish publication-quality chart tokens, axes/guides/labels, responsive density, SVG/Canvas states, interactions, accessibility, print/export, and reviewed visual fixtures. |
| **0.39** | Complete dense data, table, editor, map, and media containment, optimistic-state presentation, and integration with the 0.38 chart system. |
| **0.40** | Publish third-party authoring rules for tokens, classes, parts, slots, variants, theme compatibility, visual fixtures, and safe application overrides. |
| **0.41** | Complete active-navigation reveal, fragment-entry motion, history/focus/title behavior, bounded draft-state presentation, and multi-element failure isolation. |
| **0.42** | Lock the Supported visual inventory and prove browser, accessibility, human-AT, performance, compatibility, upgrade/rollback, and supply-chain evidence for production-grade graduation (D-070 Stage 0 refined; satisfied by `STABLE-042` / `AT-042` / `PERF-042` — do not invent `PRESENT-042`). |

The 0.33 work establishes evidence and fixes clear defects; it does not make `hedron-posit`
delivery depend on a wholesale redesign. The refreshed default becomes mandatory at 0.34 only after the compatibility
and visual gates below are reviewable.

## Acceptance and evidence

### Deterministic geometry checks

Browser tests MUST assert behavior, not only pixels:

- no document-level horizontal overflow at 320, 390, 768, 1024, and 1440 CSS pixels;
- any wide table has a scroller whose client width stays within its owning surface;
- Grid, Lazy, tab panel, Card body, and result-region ancestors use an explicit `min-width: 0`
  containment path where needed;
- composite surfaces retain their documented padding at every breakpoint;
- app-shell navigation changes mode before content or action controls overlap;
- the active mobile navigation item intersects the visible nav viewport;
- full-page `MainPanel` opacity is `1` before interaction; and
- fragment navigation finishes with stable focus/current-page state and no unexpected layout shift.

### Visual regression matrix

The reference gallery MUST have deterministic screenshots for:

- light and dark modes;
- desktop, intermediate app-shell, tablet, and narrow-mobile widths;
- default, hover/focus where deterministic, validation, disabled, loading, success, warning, danger,
  empty, and unavailable states;
- reduced motion, forced colors, print preview where supported, 200% zoom/reflow, and browser text
  enlargement; and
- minimum and current supported browser engines.

Pixel comparison is paired with DOM geometry, accessibility, and semantic assertions so a font or
antialiasing delta cannot hide a containment regression or create a permanently flaky gate.

### Accessibility and usability

- Axe/ACT automation and keyboard scenarios pass for every gallery route.
- Heading and landmark structure remains valid in full-page and fragment forms.
- Focus rings are never clipped by cards, tabs, dialogs, sticky regions, or overflow containers.
- Contrast and non-color state distinction pass in both token modes and forced colors.
- Touch targets, reflow, and content expansion pass without hiding the active action.
- Representative public form, settings, chart, table, dialog, and navigation workflows join the 0.42
  human-AT evidence set; unproven patterns remain outside the Supported visual inventory.

### Performance and delivery

- The default experience requires no application Node.js build and no remote font, icon, image, or
  script dependency.
- Layout CSS works without JavaScript. Optional navigation reveal and fragment motion are small,
  local progressive enhancements with no correctness authority.
- CSS, script, request, cumulative-layout-shift, long-task, and memory budgets are recorded before
  the 0.34 default switch and locked for 0.42 graduation.
- Clean wheel/sdist installs include the exact audited assets used by the gallery and reference app.

## Compatibility and rollout

1. Inventory documented `--hedron-*` tokens, stable component classes, application overrides, and
   snapshot expectations before changing the bundled stylesheet.
2. Prefer additive semantic tokens and selectors. Where an existing documented contract must
   change, provide a diagnostic, migration example, and compatibility fixture.
3. Keep `default_styles=False` unchanged. Applications that fully own their CSS must not receive the
   new presentation or enhancer.
4. During the preview window, expose the refreshed system through an explicit configuration that is
   removable once it becomes the default; do not maintain two permanent component implementations.
5. Test upgrades from the last 0.33 release and representative custom-theme applications before the
   0.34 switch. Rollback must require configuration/package pinning, not markup rewrites.
6. Update generated projects, docs demos, Explorer previews, screenshots, and the reference app in
   the same release that changes the default.

## Implementation map

Likely owned areas include:

- `packages/hedron-core/src/hedron_core/static/hedron-default.css`;
- `packages/hedron-core/src/hedron_core/theme.py` and public theme-token documentation;
- semantic built-ins under `hedron_core.builtins`, especially shell, surfaces, forms, feedback,
  navigation, tabs, table/data, and state components;
- page asset/enhancer loading with strict CSP and no-JavaScript fallback;
- project scaffolds, Component Explorer examples, and `examples/reference-app`;
- browser geometry, screenshot, accessibility, snapshot, package, and upgrade fixtures; and
- the 0.36–0.42 element tokens/parts/slots and SSR conformance corpus.

Private implementation names remain flexible. Public behavior, semantic markup, tokens, and gates
must be documented before the refreshed stylesheet becomes the default.

## Non-goals

- Copying Access Registry branding, government-system chrome, copy, or information architecture.
- Shipping authentication, authorization, invitation, verification, password-reset, or email policy.
- Becoming an SPA framework, client router, utility-CSS framework, or design-tool export runtime.
- Requiring Tailwind, Bootstrap, React, npm, a bundler, a remote asset CDN, or browser JavaScript for
  layout correctness.
- Making every application visually identical or preventing a fully custom theme.
- Claiming that good defaults make an application secure, accessible, compliant, or production-ready
  without application-specific evidence.

## Program exit

The plan is complete when a freshly generated Hedron application and the no-app-CSS reference
gallery meet the documented visual, responsive, accessibility, interaction, performance, and
package gates; the refreshed presentation is the normal `default_styles=True` experience; custom
canvas opt-out remains intact; and the 0.42 Supported visual inventory has upgrade, rollback,
human-AT, and independent review evidence with no hidden Deferred gate.
