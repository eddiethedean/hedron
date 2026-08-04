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

## Jobs

::: hedron.jobs.enqueue_durable
    options:
      heading_level: 3

::: hedron.jobs.job_status_response
    options:
      heading_level: 3

::: hedron.jobs.schedule_post_response
    options:
      heading_level: 3

::: hedron_core.jobs.InMemoryJobBackend
    options:
      heading_level: 3

::: hedron_core.jobs.set_job_backend
    options:
      heading_level: 3

::: hedron.streaming.StreamingComponentResponse
    options:
      heading_level: 3

::: hedron.streaming.stream_tokens
    options:
      heading_level: 3

::: hedron.streaming.stream_chunked_list
    options:
      heading_level: 3

::: hedron.streaming.stream_document
    options:
      heading_level: 3

::: hedron.websocket_channel.accept_page_session_channel
    options:
      heading_level: 3

::: hedron.websocket_channel.send_region_update
    options:
      heading_level: 3

::: hedron_core.preload.NavigationPreloadPolicy
    options:
      heading_level: 3

::: hedron_core.builtins.live_ui.Dialog
    options:
      heading_level: 3

::: hedron_core.builtins.live_ui.ChatMessage
    options:
      heading_level: 3

::: hedron.builtins.chat.ChatInput
    options:
      heading_level: 3

## Framework adapters

Signatures for `hedron-flask` and `hedron-django` public exports. Narrative matrix:
[Adapters](ADAPTERS.md).

::: hedron_flask.app.HedronFlask
    options:
      heading_level: 3

::: hedron_flask.routing.hedron_route
    options:
      heading_level: 3

::: hedron_flask.responses.interaction_response
    options:
      heading_level: 3

::: hedron_flask.responses.component_response
    options:
      heading_level: 3

::: hedron_flask.routing.FlaskUrlReverser
    options:
      heading_level: 3

::: hedron_django.app.HedronDjango
    options:
      heading_level: 3

::: hedron_django.routing.hedron_view
    options:
      heading_level: 3

::: hedron_django.responses.interaction_response
    options:
      heading_level: 3

::: hedron_django.responses.component_response
    options:
      heading_level: 3

::: hedron_django.routing.DjangoUrlReverser
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
- [CLI](CLI.md) · [Page](PAGE.md) · [Adapters](ADAPTERS.md) · [Public API coverage map](COVERAGE.md)
