# Accessibility feature research

**Research date:** 2026-08-04<br>
**Normative web-content baseline:** WCAG 2.2 Level A and AA<br>
**Normative semantic baseline:** HTML and WAI-ARIA 1.2<br>
**Authoring-tool reference:** ATAG 2.0<br>
**Scope:** Hedron components, generated output, authoring APIs, HDJ, Explorer, testing, optional
packages, documentation, and release evidence

This research identifies accessibility capabilities that Hedron can add to its roadmap. It does
not certify the current framework or applications built with it. Framework-provided markup is only
one part of an accessible application; application content, domain flows, integrations, browser and
assistive-technology support, and human evaluation remain necessary.

## Primary standards and guidance baseline

The research uses first-party standards and guidance:

- [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/) and
  [Understanding WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/)
- [What's New in WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/)
- [WAI-ARIA 1.2](https://www.w3.org/TR/wai-aria-1.2/) and the
  [Accessible Name and Description Computation 1.2](https://www.w3.org/TR/accname-1.2/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/), used as informative pattern
  and keyboard guidance rather than a normative specification or production component library
- [Authoring Tool Accessibility Guidelines 2.0](https://www.w3.org/TR/ATAG20/)
- [Accessibility Conformance Testing overview and rules](https://www.w3.org/WAI/standards-guidelines/act/)
- [WCAG-EM evaluation methodology](https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/)
- [Involving users in accessibility evaluation](https://www.w3.org/WAI/test-evaluate/involving-users/)
- [WAI guidance for accessible audio and video](https://www.w3.org/WAI/media/av/)
- [Supplemental cognitive accessibility guidance](https://www.w3.org/WAI/WCAG2/supplemental/)
- [Mobile accessibility at W3C](https://www.w3.org/WAI/standards-guidelines/mobile/)
- [Developing an accessibility statement](https://www.w3.org/WAI/planning/statements/)

WCAG 2.2 A/AA and WAI-ARIA 1.2 are the stable targets. WAI-ARIA 1.3 and WCAG 3 are active drafts;
they may inform experiments but cannot silently change a release gate or support claim. WCAG 3 is
explicitly incomplete and uses a developing conformance model. A future refresh must record any
draft feature adopted experimentally and its browser/assistive-technology evidence.

## Existing Hedron strengths

Hedron already treats accessibility as a component and release contract rather than optional
documentation. Existing plans cover:

- native semantic elements before ARIA, contextual escaping, typed `aria` mappings, and no
  arbitrary event-handler attributes;
- accessible names, labels, descriptions, required/invalid state, form errors, busy regions,
  alerts, progress, status, and retry affordances;
- keyboard behavior, visible focus, logical focus restoration after HTMX swaps, and ordinary HTML
  or no-JavaScript fallbacks;
- theme contrast, zoom, reflow, reduced motion, forced colors, touch targets, and meaning that does
  not depend on color alone;
- table captions/headers, DataEditor keyboard intent, chart descriptions, static alternatives, and
  tabular visualization fallbacks;
- browser hooks and axe-style scans, accessibility panels in Explorer, documented waivers, and
  release-blocking accessibility defects; and
- accessibility gates repeated in the later controls, media, analysis, dashboard, and inference
  phases.

The gaps are depth, traceable evidence, author assistance, and complete treatment of rich
interactions—not an absence of basic semantic intent.

## Recommended capability packet

| Capability family | Recommendation |
|---|---|
| Standards profile | Version the WCAG/ARIA/HTML/ACT baselines and keep stable requirements separate from draft experiments. |
| Component contracts | Add a machine-readable `AccessibilityContract` for every public component and variant. |
| Authoring assistance | Apply ATAG principles to CLI, Explorer, HDJ, generators, templates, examples, and transformations. |
| Diagnostics | Produce source-associated automatic, semi-automatic, and manual checks with rule provenance and certainty. |
| Accessibility-tree testing | Add role/name/state/value snapshots and targeted assertions across dynamic states, not DOM-only snapshots. |
| Interaction testing | Add reusable keyboard, focus, pointer, touch, voice-input-compatible, live-region, and timeout scenarios. |
| Assistive-technology evidence | Maintain a scoped browser/AT matrix with versions, tasks, results, known issues, and retest cadence. |
| WCAG 2.2 additions | Explicitly cover focus not obscured, non-drag alternatives, target size, consistent help, redundant entry, and accessible authentication. |
| Media | Add captions, transcripts, audio description, language tracks, accessible player controls, and live-caption integration points. |
| Rich spatial tools | Require list/outline/table and direct-control alternatives for charts, maps, crop tools, splitters, reorder UIs, dashboards, and workflow canvases. |
| Cognitive support | Add predictable actions, undo/review, clear visible labels, task progress, timeout control, consistent help, and user presentation preferences. |
| Conformance reporting | Generate evidence inventories and accessibility-statement inputs without generating an automatic conformance claim. |
| User evaluation | Require appropriately scoped evaluation with disabled users for representative complex workflows. |

## Versioned `AccessibilityContract`

Every public built-in, package component, and significant variant should publish an inspectable
contract containing:

- intended native element or ARIA role, allowed states/properties, required owned/context roles,
  accessible-name and description sources, and relationships;
- visible label requirements and whether a text alternative is author-required, generated,
  decorative, or unavailable;
- keyboard interaction table, focus entry/exit/restoration, roving-tabindex or active-descendant
  policy, escape behavior, and no-trap requirement;
- pointer, touch, drag, gesture, and direct single-pointer alternatives, including target-size and
  spacing assumptions;
- dynamic state transitions, busy/progress/error/success announcements, live-region politeness and
  atomicity, deduplication, and rate limits;
- zoom/reflow, text spacing, orientation, forced-colors, contrast, color-independent meaning,
  reduced-motion, animation/flashing, and user-style behavior;
- media alternatives, data/visualization alternatives, no-JavaScript behavior, and fallback
  equivalence where applicable;
- supported browser/assistive-technology evidence, manual checks, known limitations, and waiver
  identifiers; and
- WCAG success-criterion, ARIA/APG pattern, ACT-rule, source package, version, and stability links.

Contracts describe obligations and evidence. They do not imply that arbitrary application content
or composition conforms merely because each leaf component has a contract.

## WCAG 2.2 interaction requirements to make explicit

Hedron names several of these concepts today, but they need specific reusable behavior and tests.

### Focus not obscured

- Sticky headers, bottom docks, chat panels, cookie/feedback surfaces, popovers, toasts, dialogs,
  virtual keyboards, and responsive overlays must not fully hide the focused control.
- Layouts may reflow, move focus into a modal scope, dismiss non-persistent content, provide an
  immediate escape/reveal command, or scroll the focused item into view.
- Focus visibility is tested at every supported breakpoint, zoom/text-spacing configuration, and
  virtual-keyboard viewport, not only at desktop defaults.

### Dragging and spatial operation

- Reordering, splitters, sliders, image crop/selection, chart brush, maps, tree/grid drag, dashboard
  layout, and workflow edges must have keyboard and single-pointer alternatives that do not require
  dragging.
- Alternatives include move-before/after controls, numeric fields, select-and-place, direction and
  step controls, coordinate/size fields, ordered lists, and structured node/edge editors.
- Pointer alternatives do not replace keyboard support; both are tested with focus and announced
  state changes.

### Target size and input modalities

- Theme/component geometry validates the WCAG 2.2 AA 24-by-24 CSS-pixel target or spacing rule,
  with documented inline, equivalent-control, user-agent, and essential exceptions.
- Tests cover coarse pointers, touch zoom, pointer cancellation, label-in-name, orientation,
  concurrent input mechanisms, and browser text enlargement without disabling platform behavior.
- A larger recommended design-system target may be offered, but it must be distinguished from the
  normative minimum.

### Consistent help, redundant entry, and error recovery

- Applications can register a consistent help/contact/feedback location that remains discoverable
  across page and fragment navigation.
- Multi-step flows can reuse or offer previously entered information without copying secrets into
  client state. Authors must declare essential/security exceptions.
- Forms and consequential actions support visible instructions, field and summary errors, focus to
  the error context, retained valid values, suggested corrections, review/confirm, undo or reversal,
  and timeout warnings/extensions where permitted.

### Accessible authentication

- Login components use correct input purpose/autocomplete tokens, permit password-manager fill and
  copy/paste, expose show-password controls accessibly, and do not fragment one-time-code input in a
  way that prevents paste/autofill.
- An authentication flow must offer a path that does not depend on memorization, puzzles, object
  recognition, or transcription. Passkeys/WebAuthn, magic links, device approval, and pasteable or
  automatically filled codes are host/provider options rather than a new Hedron identity system.
- CAPTCHA, MFA, recovery, reauthentication, and timeout flows are included in the same assessment;
  an accessible login page does not compensate for an inaccessible recovery path.

## Authoring-tool accessibility and assistance

Hedron's CLI, Explorer, component preview, HDJ authoring, generators, examples, and visual workflow
editor are authoring tools in the practical ATAG sense. The roadmap should use ATAG in two parts:

1. make the authoring interfaces themselves accessible to disabled authors; and
2. help every author produce and preserve accessible output.

Concrete features include:

- accessible, keyboard-complete Explorer, preview, diagnostics, and workflow editing surfaces that
  respect platform display/control preferences and persist author-specific settings separately
  from generated content;
- accessibility metadata fields presented alongside ordinary component properties—not hidden in
  an advanced panel—including alt/decorative intent, labels, descriptions, language, captions,
  transcript, table/chart summaries, and interaction alternatives;
- accessible defaults and templates at least as prominent as risky choices, with accessibility
  support enabled by default and warnings when authors disable or bypass it;
- source-associated checking that identifies the affected component/HDJ line/prop, explains how to
  decide manual questions, offers repair guidance, and produces an accessible status report;
- preservation of labels, relationships, language, alt text, captions, table headers, reading
  order, and other accessibility information through inspect/eject, copy/paste, conversion,
  serialization, caching, optimization, fragments, and code generation;
- author-reviewed suggestions for alternative text or plain-language help. AI-generated content is
  never inserted as verified accessibility information without acceptance/editing and provenance;
- reversible authoring changes or explicit confirmation, especially for bulk repair, template,
  workflow, and generated-code operations; and
- component examples and tutorials that demonstrate accessible practice instead of merely passing
  static markup checks.

An ATAG conformance claim requires a separate applicability report and evidence. The roadmap may
target applicable A/AA outcomes without claiming that all of ATAG is already satisfied.

## Diagnostics and Explorer

The existing accessibility panel can grow into a review workspace:

- rendered accessibility tree with role, computed name/description, value/state, ownership, and
  source component/HDJ mapping;
- heading, landmark, label/control, language, reading-order, tab-order, and focus-path outlines;
- keyboard-command map and interactive focus trace through initial, loading, success, validation,
  error, modal, disconnected, and restored-history states;
- live-region event log showing visible message, programmatic announcement, politeness, atomicity,
  duplicate suppression, and timing;
- contrast/non-text-contrast, target-size/spacing, focus-obscuration, text-spacing, zoom/reflow,
  orientation, reduced-motion, forced-colors, and color-vision review modes;
- media-track/transcript and visualization/table-alternative inventories;
- automatic, semi-automatic, and manual findings distinguished visibly, with WCAG/ARIA/ACT mapping,
  rule and engine version, severity, certainty, remediation, source, and affected users; and
- a waiver registry with owner, rationale, affected users, alternative, evidence, expiry, target
  version, and release-blocking policy.

Explorer must not label a page "accessible" because an automated scan is empty. WAI guidance is
explicit that tools assist evaluation but cannot determine accessibility on their own.

## Test and evidence architecture

### Automated and semantic tests

- Run static semantic/ARIA validation and pinned axe/ACT-aligned browser scans after each meaningful
  dynamic state becomes visible, including inside supported open shadow roots and same-origin
  frames.
- Add accessibility-tree snapshots and targeted role/name/state/value assertions. Snapshot updates
  are reviewable patches; broad regeneration cannot silently approve semantic regressions.
- Provide an `AccessibilityScenario` helper for tab/shift-tab, arrow/home/end/page keys, enter/space,
  escape, shortcuts, pointer/touch alternatives, focus assertions, announcements, timeouts, and
  history/fragment transitions.
- Emit machine-readable JSON and SARIF with stable Hedron diagnostic IDs plus upstream rule
  provenance. Engine disagreement or incomplete/manual results remain visible.

### Manual assistive-technology matrix

Maintain a scoped matrix rather than claiming every browser/AT combination. At minimum, release
evidence should cover representative tasks with:

- VoiceOver with Safari on macOS and iOS;
- NVDA with Firefox and Chromium on Windows;
- TalkBack with Chromium on Android; and
- keyboard-only, switch/voice-input-compatible label-in-name checks, browser zoom, platform high
  contrast/forced colors, reduced motion, and text-spacing/user-style overrides.

JAWS or other proprietary AT may be added when licensing and audience evidence justify it. Each
record includes OS/browser/AT versions, settings, task, expected announcement/operation, result,
known issue, evidence owner, and retest date. Passing one screen reader is not generalized to all
users or disability groups.

### Evaluation with disabled users

Representative complex workflows—data editing, uploads, charts, chat/live updates, authentication,
dashboard filtering, and visual inference workflows—should be evaluated with appropriately
compensated disabled participants. Research plans define task/audience fit, consent, privacy,
accommodations, data retention, reporting scope, and how issues feed the roadmap. User evaluation
complements, rather than replaces, WCAG conformance evaluation.

## Media, data, and visualization additions

### Audio and video

- `Audio` and `Video` accept typed caption/subtitle tracks with language and kind, transcript or
  descriptive transcript, audio-description track or described version, and author-declared media
  alternative status.
- Player controls have names, keyboard operation, focus order, target size, captions/description
  selection, playback speed, pause/stop, volume independent of system volume, and no unexpected
  autoplay. Full-screen state and errors are announced without trapping focus.
- Interactive transcripts can follow playback and seek from text without making motion/highlighting
  essential. Live media exposes a provider boundary for human or reviewed caption services;
  automatic captions are drafts, not sufficient evidence by themselves.

### Tables, editors, charts, maps, images, and models

- Tables preserve captions, header associations, sort/filter/edit state, selected row/cell identity,
  and validation messages under virtualization and pagination.
- Editors publish discoverable keyboard modes and avoid trapping screen-reader browse/focus modes.
  Drag/reorder, fill, resize, and spatial editing have direct-control alternatives.
- Charts and maps provide author-reviewed title, short summary, detailed description, data table or
  list, non-color encoding, keyboard-accessible declared selections, and equivalent filter/action
  paths. Automated narrative summaries disclose provenance and remain editable.
- Image annotation/crop and 3D/workflow canvases expose a structured list/outline/table view with
  selection, reorder, coordinates/dimensions, connections, and results. The spatial canvas is an
  enhancement, never the only route to create or operate the content.

## Cognitive accessibility and personalization

WCAG conformance does not cover every cognitive and learning disability need. Hedron can provide
optional, clearly scoped support without claiming to measure whether prose is understandable:

- visible labels and instructions using application-authored plain language; consistent control
  identification, navigation, and help placement;
- step/progress context, summaries before consequential actions, retained values, undo/back, review,
  reminders, and clear recovery paths;
- user-controlled animation, auto-update frequency, media playback, notification intensity, density,
  font/line/word spacing, and simplified presentation where the application supplies one;
- typed help, glossary, abbreviation, and alternative-explanation slots that remain visible and
  programmatically associated; and
- time-limit declaration with warning, remaining time, pause/extend policy, saved work, and session
  security ownership.

Preferences are non-secret user settings. They do not rewrite domain content automatically, bypass
authorization, or become proof that the resulting application meets a particular user need.

## Internationalization and structure

The platform should validate and preserve:

- page and passage language, text direction, bidirectional isolation, localized labels/errors,
  and accessible names that continue to contain the visible label after translation;
- one discoverable page title, meaningful heading hierarchy, landmarks, skip links, reading order,
  and consistent navigation/help across full-page and fragment responses; and
- locale-aware dates, times, numbers, pronunciation-sensitive abbreviations, and error examples
  without relying on placeholder text as the only instruction.

Automatic translation or right-to-left layout changes require the same component, focus, reflow,
truncation, target, and assistive-technology evidence as the source locale.

## Reporting and release governance

- Generate an evidence inventory from component contracts, browser/AT results, diagnostics,
  waivers, known limitations, technologies relied upon, and test dates.
- Provide an accessibility-statement template/export containing standard, scope, contact/feedback
  routes, known limitations and alternatives, tested environments, assessment approach, and date.
- Never generate a `conforms`, VPAT/ACR, legal-compliance, or certification statement automatically.
  Those require a scoped human assessment and organizational approval.
- Release policy defines blocker severity, affected-user impact, regression policy, waiver authority
  and expiry, remediation ownership, and a public/security-sensitive reporting path.
- Third-party components and plugins publish their own contract and evidence. Hedron reports the
  boundary and cannot transitively guarantee an application through package metadata alone.

## Phase assignments

| Accepted capability | Owner |
|---|---:|
| Caption/transcript/audio-description media tracks and accessible player behavior | 0.15 expanded; 0.19 conformance depth |
| WCAG 2.2 accessible-authentication ergonomics over host identity/OIDC | 0.15 expanded; 0.19 evidence |
| Keyboard/single-pointer alternatives for editor, image, splitter, chart, dashboard, and workflow drag operations | 0.12/0.16/0.17/0.18 expanded; 0.19 conformance depth |
| Structured non-spatial workflow canvas editor and result view | 0.18 expanded |
| Versioned standards profile and `AccessibilityContract` catalog | 0.19 |
| ATAG-oriented authoring assistance, preservation, checking, and repair guidance | 0.19 |
| Accessibility tree, focus, live-region, visual-mode, and source-mapped Explorer workspace | 0.19 |
| Accessibility scenario API, ACT/axe results, ARIA snapshots, and manual browser/AT matrix | 0.19 |
| Cognitive/personalization helpers and internationalization/accessibility validation | 0.19 |
| Evidence inventory, statement template, waiver governance, and disabled-user evaluation | 0.19 |

## Deliberate constraints

Hedron will not:

- claim that a component library can make arbitrary application content conform;
- equate zero automated findings with accessibility or WCAG conformance;
- use ARIA where native HTML supplies the required semantics and behavior;
- treat APG examples as normative or production-ready source to copy blindly;
- promote WAI-ARIA 1.3 or WCAG 3 draft behavior to a stable guarantee without an accepted baseline
  change and interoperability evidence;
- insert AI-generated alt text, captions, descriptions, summaries, or repairs as verified content
  without author review and provenance;
- require a visual canvas, drag gesture, color, animation, audio, hover, touch, or one screen reader
  as the only interaction/information path; or
- generate legal compliance, certification, ACR/VPAT, or conformance claims from framework tests.

## Refresh procedure

1. Record the dated WCAG, WAI-ARIA, accessible-name, ACT, ATAG, APG, HTML, browser, testing-engine,
   and assistive-technology baselines.
2. Review WCAG and ARIA errata plus the status of WCAG 3 and ARIA 1.3; draft work remains explicitly
   experimental until the roadmap changes its normative baseline.
3. Re-enumerate every public component, variant, dynamic state, authoring surface, transformation,
   optional adapter, example, and template against the `AccessibilityContract` schema.
4. Re-run automatic, semantic-tree, interaction, visual-mode, browser/AT, and manual/user-evaluation
   evidence with recorded versions and scoped tasks.
5. Review expired waivers, known limitations, third-party boundaries, accessibility feedback, and
   regression severity before a release claim.
6. Update this research ledger, RFC-0023, acceptance criteria, both roadmap mirrors, README phase
   summary, and documentation navigation together.
