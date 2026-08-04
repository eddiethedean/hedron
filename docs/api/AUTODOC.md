# Autodoc — `Hedron` and core symbols

Generated signatures via **mkdocstrings**. Prefer the hand-maintained contract pages for
narrative, errors, and adopter guidance; use this page to verify parameter lists against
the installed sources.

## `hedron.Hedron`

::: hedron.app.Hedron
    options:
      members:
        - page
        - component
        - action
        - include_component
        - include_router
      show_bases: true
      heading_level: 3

## `hedron.HedronRouter`

::: hedron.routing.router.HedronRouter
    options:
      members:
        - page
        - component
        - action
        - include_component
      heading_level: 3

## Interaction

::: hedron_core.interaction.InteractionResult
    options:
      heading_level: 3

::: hedron_core.interaction.FragmentRegion
    options:
      heading_level: 3

::: hedron_core.interaction.InteractionPolicy
    options:
      heading_level: 3

## Page and rendering

::: hedron_core.builtins.document.Page
    options:
      heading_level: 3

::: hedron_core.rendering.RenderMode
    options:
      heading_level: 3

## Common built-ins used in guides

::: hedron_core.builtins.content.Text
    options:
      heading_level: 3

::: hedron_core.builtins.layout.Stack
    options:
      heading_level: 3

::: hedron.builtins.RefreshButton
    options:
      heading_level: 3

## Live helpers

::: hedron.sse.sse_response
    options:
      heading_level: 3

::: hedron.sse.job_status_sse_response
    options:
      heading_level: 3

::: hedron.streaming.stream_tokens
    options:
      heading_level: 3

## CSRF helper

::: hedron.security.csrf.csrf_token_for_request
    options:
      heading_level: 3

## `hedron_core.Field`

::: hedron_core.field.Field
    options:
      show_root_full_path: false
      heading_level: 3

## `hedron_core.component.Component`

::: hedron_core.component.Component
    options:
      members:
        - render
      heading_level: 3

## `hedron_core.diagnostics.Diagnostic`

::: hedron_core.diagnostics.Diagnostic
    options:
      heading_level: 3

## See also

- [Hedron contract](HEDRON.md) · [Router](ROUTER.md) · [Interaction](INTERACTION.md)
- [Component](COMPONENT.md) · [Field](FIELD.md) · [SSE](SSE.md) · [Diagnostics](DIAGNOSTICS.md)
- [CLI](CLI.md) · [Page](PAGE.md) · [Public API coverage map](COVERAGE.md)
