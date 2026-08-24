# Phase 0.63 style bundles

`hedron_core.compile_style_bundle()` provides a deterministic CSS artifact for
the compatibility stylesheet or a selected component set. The scoped form is
theme-aware and uses the same reset, token, accessibility, and state rules as
the complete stylesheet.

For server asset registration, use `style_bundle_asset_refs()`. It returns
local assets in dependency order: `tokens.css`, `base.css`, `a11y.css`, then
the selected component files. The same `/hedron-static` directory is mounted
by the FastAPI, Flask, Django, Posit, and static adapters, so registration does
not require framework-specific CSS generation.

`compare_style_bundle_sizes()` is the release evidence check that confirms a
component-scoped bundle is smaller than the complete compatibility asset.
Applications should keep the complete stylesheet for compatibility and opt
into scoped assets only when their component inventory is known.
