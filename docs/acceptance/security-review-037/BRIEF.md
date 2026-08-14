# Security review brief — phase 0.37 (form-associated elements and interactive primitives)

**Package / train at cut:** Hedron `v0.38.0` + Alpha `hedron-elements` `0.38.0`  
**Owning RFC:** [RFC-0060](../../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) (D-065)  
**Gates:** `FORM-037`, `VALIDITY-037`, `INTERACT-037`, `ACTIONSTATE-037` (cross-cutting with `HTMX-037` / `PKG-037`)  
**Tracking:** [#93](https://github.com/eddiethedean/hedron/issues/93); high-severity
[#230](https://github.com/eddiethedean/hedron/issues/230)–[#237](https://github.com/eddiethedean/hedron/issues/237)

## Scope

Independent review of the **form, async interaction, and gesture/overlay** surface:

- Form submission authority: server-owned CSRF, business validation, and authorization; client
  validation cannot suppress server errors or authorize mutations (extends EL-036-04 disposition)
- `ElementInternals` and native fallback parity without widening submission authority
- File/directory controls: bounded object lifecycle, type/size/path adversarial cases, cancel/cleanup
- `InteractionState`: opaque operation correlation IDs must not carry secrets or grant authority;
  late/duplicate responses correlated safely
- Overlay focus traps, inert/background behavior, and dismissal without focus loss or authority bypass
- Gesture allowlists: typed intent payloads reject DOM nodes, selectors, arbitrary MIME/path/HTML/URL
- Command palette / toast surfaces invoke registered routes under ordinary authz/CSRF validation
- HTMX swap/history paths preserve server errors and do not drop unsent user intent silently
- High-severity remediations in the 0.37 packet: HTMX `data-hx-*` / element-markup eval (#230,
  #237, #244), Flask production cookie flags (#231), MCP Origin and body-limit checks (#232, #233),
  directory-upload NUL paths (#234), SelectSlider value encoding (#235), Redis idempotency
  pointer delete (#236)

## Out of scope

- High-fidelity chart grammar/renderer (phase 0.38; separate RFC-0069 review)
- `OptimisticMutation` and rich-surface adapters (phase 0.39)
- React-island bridge and third-party author kit (phase 0.40)
- Draft transfer (phase 0.41)
- Production-grade / `stable` promotion (phase 0.42)
- Reopening `polling_only` live-transport disposition
- Treating element events or overlay DOM as an authorization boundary

## Required artifacts at cut

- `REDACTED_REPORT.md` — findings with severity and disposition
- `DISPOSITION.toml` — machine-checked closure of critical/high items

## Review questions

1. Can a form-associated element or fallback submit values the server did not authorize?
2. Do file controls retain objects beyond bounded user-initiated flows or leak paths across sessions?
3. Can gesture/overlay catalog entries mutate authoritative records without registered server actions?
4. Does `InteractionState` ever reflect success/cancellation before the server contract acknowledges it?
5. Do CSRF, validation fragments, and overlay dismissal survive HTMX swap/disconnect races safely?
6. Are diagnostics (`HED-ELEMENT-*` form/state/gesture codes) payload-safe and actionable?

## Status

Complete at `v0.38.0` cut: [REDACTED_REPORT.md](REDACTED_REPORT.md) and
[DISPOSITION.toml](DISPOSITION.toml) record zero open critical/high findings. Follow-on
[#244](https://github.com/eddiethedean/hedron/issues/244) is closed.
