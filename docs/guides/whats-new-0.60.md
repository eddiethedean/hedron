---
description: What's new in Hedron 0.60 custom themes and styling completion.
search:
  boost: 1.4
---

# What's new in 0.60

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and 1.0 candidate status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

Hedron 0.60 is implemented, verified, tagged, and published on PyPI. Applications use
`hedron>=0.66.2,<0.67`.

## Highlights

- Absolute CSS Color 4 input with deterministic conversion, gamut mapping, and sRGB fallback.
- Immutable `ThemeSpec`, copy-on-write `ThemeBuilder`, ordered `ThemePatch`, provenance, aliases,
  coverage profiles, relationship-aware validation, fingerprints, and deterministic data-only packages.
- Registry-derived component contracts with semantic roles, contrast relationships, accessibility
  behavior, fallback policy, and complete-profile conformance reports.
- Forced-colors and more-contrast theme mappings, finite presentation-only recipe families, and
  serializable `StyleContext` precedence without process-global mutation.
- Server-first `ThemePreference` / `ThemePicker` markers and a CSP-safe bounded boot asset.
- Zero-application-CSS completion for `Brand`, `ToastHost`, `ConnectorFlow`, and `ScrollRegion`.
- Read-only Explorer Theme Lab with side-by-side modes, token/state inspection, diffs, fallback
  warnings, accessibility exercises, and JSON report export.
- Portable third-party conformance and 27-gate release evidence tooling.

## Compatibility and boundaries

The existing `Theme`, `DesignSystem`, built-in `default` / `aurora` themes, hex brand input,
recipes, scopes, public markers, component CSS, compiler cascade, and `default_styles=False` path
remain compatible. Theme packages are local data only: they cannot execute hooks or fetch remote
assets. Human assistive-technology sign-off remains open and is not claimed by the release packet.

See the [release notes](release-notes.md), [upgrade guide](upgrade.md), and the
[0.60 release packet on GitHub](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_60.md).
