# RFC-0053: Progressive enhancement, landmarks, and Page scripts

**Status:** Draft
**Phase:** 0.19 (`v0.19.0`)
**Stability:** `beta` (API)
**Evidence:** `PE-019`, `LANDMARK-019`, `SCRIPT-019`
**Related:** RFC-0009, RFC-0012, RFC-0023; D-050;
issues [#8](https://github.com/eddiethedean/hedron/issues/8),
[#27](https://github.com/eddiethedean/hedron/issues/27),
[#31](https://github.com/eddiethedean/hedron/issues/31),
[#39](https://github.com/eddiethedean/hedron/issues/39)

## Summary

Document and test the progressive-enhancement contract for forms and mutations, export landmark
helpers as real types with safe HTML attrs, and provide an allowlisted same-origin script slot on
`Page` without reintroducing free-form `<script>` nodes in the component tree.

## Motivation and background

HTMX fragments are optional enhancement. Critical flows must succeed with classic no-JS POST → full
`Page` or redirect. Apps also need typed landmarks with safe attrs and a CSP-friendly way to attach
PE scripts (toast dismiss, dialog close) without HTML post-processing.

Issue bodies for #8, #27, #31, and #39 remain normative for acceptance criteria.

## Proposed design

### Progressive enhancement (`PE-019`)

- No-`HX-Request` mutation POSTs succeed through the documented path (full document or redirect).
- HTMX fragment / `InteractionResult` paths remain covered and optional.
- Built-ins usable without HTMX are called out in Minimal form / Forms and actions guides.
- JavaScript is never mandatory for critical form/mutation flows.

### Landmarks (`LANDMARK-019`)

- Safe HTML attrs on landmark / surface components.
- Landmark helpers exported as real types (not factory variables).
- Landmark semantics remain native-first; ARIA landmark roles only when native elements are
  insufficient.

### Page scripts (`SCRIPT-019`)

- Public API to attach allowlisted external scripts to a page document via same-origin `SafeUrl`
  assets (ASSET purpose), with defer/async policy.
- Inline script content remains forbidden by default (or explicitly opt-in + documented danger).
- CSP-friendly examples (`script-src 'self'`).
- Free-form `<script>` nodes stay out of the component tree.

## Alternatives considered

1. **HTMX-only mutations.** Rejected — breaks no-JS and progressive-enhancement commitment (#8).
2. **String-inject scripts after render.** Rejected — fragile and undocumented (#39 motivation).
3. **Allow arbitrary inline scripts in the tree.** Rejected — XSS / CSP regression.

## Security implications

Script allowlisting must enforce `SafeUrl` / purpose checks and same-origin asset policy. Landmark
attrs reuse the existing safe-attribute allowlist; no event-handler attributes. PE paths must keep
CSRF validation on unsafe methods when profiles enable it.

## Accessibility implications

Landmarks, skip links, and reading order support `I18N-019` structural validation. PE ensures
keyboard and AT users are not trapped behind mandatory JS. Script-enhanced widgets must degrade to
usable HTML controls.

## Performance implications

Allowlisted scripts are explicit assets in build manifests; production still refuses missing
manifests. No implicit third-party script CDNs.

## Testing strategy

- Automated non-`HX-Request` success path for representative forms/mutations (`PE-019`).
- Type/export and attr allowlist tests for landmarks (`LANDMARK-019`).
- Render tests assert script tags appear once with expected `src` / `defer` (`SCRIPT-019`).
- Adversarial cases: rejected inline scripts, bad purposes, cross-origin URLs.

## Compatibility and migration

Additive APIs. Apps currently string-injecting scripts migrate to `Page` script slots. Landmark
factory variables become typed exports with a documented rename path if needed.

## Open questions

- Exact `Page` field names (`scripts=` vs `head=` asset slot).
- Whether Flask/Django adapters need mirrored helpers in 0.19 or inherit via core render.

## Acceptance criteria

- Documented and tested no-JS POST path alongside HTMX fragments (`PE-019`; #8).
- Landmark attrs + real types (`LANDMARK-019`; #27, #31).
- Allowlisted `Page` PE scripts with tests and CSP examples (`SCRIPT-019`; #39).
