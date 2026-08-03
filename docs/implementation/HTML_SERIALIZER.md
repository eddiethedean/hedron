# HTML serializer implementation

## Requirements

The serializer converts normalized nodes to deterministic HTML while enforcing context-specific safety and correct HTML semantics.

## Behavior

- Escape text and quoted attribute values.
- Validate and normalize tag and attribute names through static HTML metadata.
- Handle boolean, enumerated, URL-bearing, token-list, data, ARIA, and HTMX attributes through typed conversion.
- Serialize void elements correctly and reject children on them.
- Preserve deterministic attribute ordering for snapshots and caches.
- Require `TrustedHtml` for raw fragments and `SafeUrl` plus final-context policy for URL-bearing attributes.
- Reject inline event handlers and disallowed dynamic attributes under baseline policy.

Serialization should write to an efficient append-only buffer. A future native implementation may replace the buffer stage only if it passes byte-level conformance.

## Context boundaries

JSON specifications are serialized as data outside executable JavaScript contexts. CSS values are not accepted as generic strings. SVG is treated as active content and enters through registered trusted assets or a sanitizer integration.

## Verification

Use an adversarial corpus for text, attributes, URLs, Unicode, malformed names, raw HTML, SVG, and HTMX selectors. Compare representative output with browser parsing and validate deterministic results across supported Python versions.
