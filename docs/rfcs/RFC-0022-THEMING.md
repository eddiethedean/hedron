# RFC-0022: Theming

**Status:** Accepted

## Design

Themes are collections of semantic CSS custom properties, typography, color, spacing, motion, elevation, and component variant defaults. Scoped classes isolate component structure; variables carry shared design values. Themes do not generate arbitrary CSS from user data.

The default cascade order is reset, tokens, base, components, utilities, and application overrides. Applications may select a theme globally, at a mounted sub-application boundary, or at an explicit subtree where inheritance is safe. System light/dark preference may select a declared mode without hiding the resulting CSS.

Component customization proceeds through semantic props, extra classes, variables, override layers, or ejected styles. Packaged components document supported tokens and variants. Unknown required tokens and incomplete finite variants produce build diagnostics.

## Accessibility and security

Themes must meet contrast and focus visibility requirements, respect reduced-motion preferences, and avoid conveying critical meaning through color alone. Remote fonts and resources require explicit policy.

## Acceptance criteria

- Theme switching preserves scoped identifiers and component behavior.
- Token manifests are deterministic and inspectable.
- The reference themes pass defined contrast, focus, motion, and forced-colors checks.

