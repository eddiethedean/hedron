# RFC-0037: CodeEditor and interactive extras

**Status:** Draft
**Phase:** 0.16 (`v0.16.0`)
**Related:** [NiceGUI feature cross-check](../NICEGUI_FEATURE_CROSSCHECK.md)
(`ui.codemirror`, signature/calendar/typeahead examples, interactive image);
RFC-0014 (plugins), RFC-0010, RFC-0021, RFC-0023; roadmap `hedron-extras`

## Summary

Define optional 0.16 extras for a CSP-safe `CodeEditor` (CodeMirror-class, distinct from
`CodeBlock`/`JSONEditor`), plus calendar, signature-pad, and typeahead/combobox extras or recipes,
and optional interactive-image annotation overlays beyond crop/region selection. These ship as
curated extras with pinned assets — not Quasar/Vue ports.

## Motivation and background

NiceGUI’s CodeMirror element and example catalog (FullCalendar, signature pad, search-as-you-type,
image overlays) show demand for specialized editors. Hedron’s 0.16 workbench already owns
`JSONEditor` and image crop/region; this RFC owns the NiceGUI-accepted remainder.

## Proposed design

- **`CodeEditor`:** language allowlist, read-only vs edit modes, size budgets, submit via form /
  explicit action (full text or patch); no `eval` of buffer contents; CSP-compatible asset pin;
  keyboard and screen-reader path documented (limitations honest if upstream editor is imperfect).
- **Calendar / signature / typeahead:** independently installable extras or documented recipes over
  actions + fragments; capability manifests and missing-dependency guidance per RFC-0014.
- **Annotation overlays:** optional layer on 0.16 interactive image tools — normalized regions,
  labels, export metadata; drag alternatives Required.
- Absence of an extra adds no core import, asset, or startup cost.

## Alternatives considered

1. **Only `JSONEditor` + `TextArea`.** Insufficient for syntax-aware editing demand.
2. **Embed Monaco/CodeMirror in core.** Rejected — weight and CSP surface belong in extras.
3. **NiceGUI `ui.editor` rich text.** Prefer Markdown/`TrustedHtml` or a separate future extra;
   not in this RFC’s v1 scope unless demand forces it.

## Security implications

No execution of editor buffers; sanitize pasted HTML if any rich mode appears later; signature
images size-limited; calendar events are data not code; typeahead queries rate-limited and
authorized; annotation payloads schema-bounded.

## Accessibility implications

CodeEditor must document SR/keyboard support level; signature needs non-pointer alternative
(upload/clear); calendar full keyboard; typeahead combobox pattern (aria); annotations have
numeric/list alternatives to drawing.

## Performance implications

Lazy-load editor assets; max document size; virtualization optional; annotation point budgets.

## Testing strategy

Extra install isolation tests; CSP browser tests; adversarial oversized buffers; a11y suites
appropriate to each extra; workbench flow tests compose with `AppScenario`.

## Compatibility and migration

New optional distribution features under `hedron-extras` (or successor). NiceGUI maps
`ui.codemirror` → `CodeEditor`; examples → calendar/signature/typeahead extras.

## Open questions

1. CodeMirror vs alternative editor engine — pin choice at acceptance.
2. First-party extras vs recipe-only for calendar/signature in v1?
3. Annotation overlays same package as crop tools or separate extra?

## Acceptance criteria

- Each shipped extra installs cleanly in isolation and appears in capability manifests.
- CodeEditor cannot execute buffer contents; CSP tests pass.
- 0.16 exit gate includes editor/annotation rows from this RFC.
