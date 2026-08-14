## [0.37.0]

- Coordinated train cut for phase 0.37 (D-065).

### Fixed

- `render_element_markup` rejects `style=` except the `--hedron-gap` layout
  allowlist, and runs `href` / `src` / `formaction` / `poster` / `srcset` /
  HTMX URL attributes through `SafeUrl` so `vbscript:`, `data:`, `file:`, and
  `javascript:` cannot be emitted (#244).

# Changelog

## [0.36.0] — 2026-08-13

- Initial Alpha release: element ABI registry integration, shared bridge, and
  `hedron-example` reference light-DOM element (RFC-0060 / D-064).
