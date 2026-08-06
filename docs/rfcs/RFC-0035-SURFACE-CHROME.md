# RFC-0035: Surface chrome — carousel, timeline, context menu, chips, progress

**Status:** Draft
**Phase:** 0.15 (`v0.15.0`)
**Related:** [NiceGUI feature cross-check](../NICEGUI_FEATURE_CROSSCHECK.md);
RFC-0003, RFC-0009, RFC-0023; roadmap Gallery/Popover/controls

## Summary

Specify the NiceGUI-accepted 0.15 surface components that sit beside already-planned Gallery,
controls, and Progress: `Carousel` and lightbox selection, semantic `Timeline`, accessible
`ContextMenu`, chip/tag input, and Progress variants (including circular). Native HTML is the
baseline; enhancement preserves keyboard and no-JavaScript semantics.

## Motivation and background

NiceGUI ships carousel, timeline, context menu, chips, and circular progress as everyday chrome.
Hedron’s 0.15 Streamlit-oriented control list did not fully spell these out; the NiceGUI audit
accepted them as expansions rather than Vue/Quasar ports.

## Proposed design

- **Carousel / lightbox:** compose with `Gallery`; slide identities stable across fragment swaps;
  selection and “open lightbox” are declared actions or dialogs (`Dialog` from 0.10); autoplay
  respects reduced motion and is off by default for essential content.
- **Timeline:** ordered entries with time/label/body slots; semantic list/structure; not a
  Gantt runtime.
- **ContextMenu:** pointer and keyboard invocation; Escape/dismiss; focus restore; non-pointer
  alternative (e.g. overflow menu button) Required for the same actions.
- **Chip / tag input:** submitted values as typed multivalue form fields; create/remove via
  explicit actions or form posts; validation-retention like other 0.15 controls.
- **Progress variants:** extend `Progress` (or sibling) for circular determinate/indeterminate;
  `aria-busy` / status text pairing remains mandatory (no visual-only spinner as sole status).

## Alternatives considered

1. **CSS-only recipes without first-party components.** Rejected for shared a11y/HTMX contracts;
   recipes remain allowed for decorative variants.
2. **Quasar/Vue carousel and menus.** Deliberate non-parity.
3. **Defer all to 0.16 extras.** Rejected for Timeline/ContextMenu/chips/Progress — high-frequency
   chrome belongs with 0.15 surface completeness; calendar/signature stay 0.16.

## Security implications

Menu actions honor CSRF and `FragmentRegion`; chip values validated server-side; lightbox media
URLs use `SafeUrl` and authz from RFC-0034 where applicable.

## Accessibility implications

Carousel controls labeled; slides not only color-distinguished; timeline readable as list;
context menu full keyboard path; chips announce add/remove; circular progress has textual value
or indeterminate status.

## Performance implications

Lazy-load offscreen carousel media; limit slide counts; avoid layout thrash on fragment swap.

## Testing strategy

Component unit renders, fragment lifecycle, keyboard/screen-reader browser suites, reduced-motion
autoplay off, no-JS fallbacks (static list/gallery), validation retention for chips.

## Compatibility and migration

Additive components. NiceGUI glossary maps `ui.carousel`, `ui.timeline`, `ui.context_menu`,
`ui.input_chips`, `ui.circular_progress` → these contracts.

## Open questions

1. Is lightbox a `Gallery` mode or a separate component?
2. Context menu: native `popover`/`menu` where available vs consistent custom pattern?
3. Chip input: free-text tags vs closed vocabulary only in v1?

## Acceptance criteria

- Each component passes 0.15 keyboard, SR, zoom/reflow, reduced-motion, fragment, and no-JS gates.
- Reference or guide examples cover carousel+gallery, timeline, context actions, chips, circular
  progress without Quasar/Vue dependencies.
