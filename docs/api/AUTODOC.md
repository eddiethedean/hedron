# Autodoc — critical public symbols (subset)

Generated signatures via **mkdocstrings** for the **primary** public surface used in
Learn / Adopt paths. This page is intentionally a **subset** of every name in
`hedron.__all__` — prefer hand-maintained contract pages for narrative, errors, and
adopter guidance; use Autodoc to verify parameter lists against installed sources.

Coverage map for the full export set: [Coverage map](COVERAGE.md). Stability levels:
[Stability](STABILITY.md). Overview: [API overview](README.md).

Narrative companions: [Inference](INFERENCE.md) · [Hedron](HEDRON.md) ·
[Interaction](INTERACTION.md).

## Inference and model demos (0.18)

::: hedron_core.model_demo.ModelDemo
    options:
      members:
        - build_from_action
        - build_from_adapter
        - build_from_callable
      heading_level: 3

::: hedron_core.inference.InferencePolicy
    options:
      members:
        - admit
        - request_cancel
        - drain_ready
        - form_batch
        - release
      heading_level: 3

::: hedron_core.inference_workflow.InferenceWorkflow
    options:
      members:
        - add_node
        - connect
        - run
        - publish
        - editor_view
      heading_level: 3

::: hedron.recorder.InteractionRecorder
    options:
      members:
        - declare_public
        - record
        - snippets
      heading_level: 3

## Application and routing

::: hedron.app.Hedron
    options:
      members:
        - page
        - component
        - action
        - region
        - fragment
        - include_component
        - include_router
      show_bases: true
      heading_level: 3

::: hedron.routing.router.HedronRouter
    options:
      members:
        - page
        - component
        - action
        - include_component
      heading_level: 3

::: hedron.app.mount_hedron_static
    options:
      heading_level: 3

::: hedron.responses.HTML
    options:
      heading_level: 3

::: hedron.responses.PageResponse
    options:
      heading_level: 3

::: hedron.responses.FragmentResponse
    options:
      heading_level: 3

::: hedron.responses.ComponentResponse
    options:
      heading_level: 3

::: hedron.responses.hedron_response
    options:
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

::: hedron_core.interaction.OobUpdate
    options:
      heading_level: 3

::: hedron.interaction.swap
    options:
      heading_level: 3

::: hedron.interaction.swap_oob
    options:
      heading_level: 3

::: hedron.interaction.retarget
    options:
      heading_level: 3

::: hedron.interaction.redirect_htmx
    options:
      heading_level: 3

::: hedron.builtins.RefreshButton
    options:
      members:
        - for_region
      heading_level: 3

## Security

::: hedron.security.policy.SecurityPolicy
    options:
      members:
        - from_name
        - response_headers
      heading_level: 3

::: hedron.security.policy.SecurityProfile
    options:
      heading_level: 3

::: hedron.security.csrf.csrf_token_for_request
    options:
      heading_level: 3

::: hedron_core.security.SafeUrl
    options:
      heading_level: 3

::: hedron_core.security.TrustedHtml
    options:
      heading_level: 3

::: hedron_core.security.Secret
    options:
      heading_level: 3

## OIDC helpers (optional `hedron[auth]`)

::: hedron.oidc.OidcClientConfig
    options:
      members:
        - resolved_authorize_url
        - resolved_end_session_url
      heading_level: 3

::: hedron.oidc.generate_pkce
    options:
      heading_level: 3

::: hedron.oidc.generate_state
    options:
      heading_level: 3

::: hedron.oidc.store_oidc_handshake
    options:
      heading_level: 3

::: hedron.oidc.normalize_claims
    options:
      heading_level: 3

::: hedron.oidc.redact_claims
    options:
      heading_level: 3

::: hedron.oidc.login_url
    options:
      heading_level: 3

::: hedron.oidc.logout_url
    options:
      heading_level: 3

## Page, component, and rendering

::: hedron_core.builtins.document.Page
    options:
      heading_level: 3

::: hedron_core.component.Component
    options:
      members:
        - render
      heading_level: 3

::: hedron_core.field.Field
    options:
      show_root_full_path: false
      heading_level: 3

::: hedron_core.rendering.render
    options:
      heading_level: 3

::: hedron_core.rendering.RenderMode
    options:
      heading_level: 3

::: hedron_core.rendering.RenderResult
    options:
      heading_level: 3

::: hedron_core.html.html
    options:
      heading_level: 3

## State and cache

::: hedron.state.SessionState
    options:
      heading_level: 3

::: hedron.state.session_state
    options:
      heading_level: 3

::: hedron_core.cache.invalidate_tags
    options:
      heading_level: 3

::: hedron.cache.cache_data
    options:
      heading_level: 3

::: hedron.cache.cache_component
    options:
      heading_level: 3

## Common built-ins used in guides

::: hedron_core.builtins.content.Text
    options:
      heading_level: 3

::: hedron_core.builtins.content.Heading
    options:
      heading_level: 3

::: hedron_core.builtins.layout.Stack
    options:
      heading_level: 3

::: hedron_core.builtins.surfaces.Card
    options:
      heading_level: 3

::: hedron_core.builtins.forms.Form
    options:
      heading_level: 3

::: hedron_core.builtins.forms.TextInput
    options:
      heading_level: 3

::: hedron_core.builtins.forms.SubmitButton
    options:
      heading_level: 3

::: hedron.builtins.RefreshButton
    options:
      heading_level: 3

::: hedron.builtins.Poll
    options:
      heading_level: 3

::: hedron.builtins.Lazy
    options:
      heading_level: 3

::: hedron.builtins.AutoForm
    options:
      heading_level: 3

## Color mode

::: hedron_core.color_mode.ColorMode
    options:
      heading_level: 3

::: hedron_core.color_mode.resolve_color_mode
    options:
      heading_level: 3

::: hedron.color_mode.apply_color_mode_cookie
    options:
      heading_level: 3

::: hedron.color_mode.read_color_mode_preference
    options:
      heading_level: 3

## Live helpers

::: hedron.sse.sse_response
    options:
      heading_level: 3

::: hedron.sse.job_status_sse_response
    options:
      heading_level: 3

::: hedron.sse.SseResponse
    options:
      heading_level: 3

::: hedron.jobs.enqueue_durable
    options:
      heading_level: 3

::: hedron.jobs.job_status_response
    options:
      heading_level: 3

::: hedron.jobs.schedule_post_response
    options:
      heading_level: 3

::: hedron_core.jobs.JobBackend
    options:
      members:
        - submit
        - get
        - request_cancel
        - cleanup_expired
        - mark
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

## Prepare lifecycle (0.13)

::: hedron_core.prepare.PrepareContext
    options:
      heading_level: 3

::: hedron_core.prepare.PartialFailurePolicy
    options:
      heading_level: 3

## Security audit (0.13)

::: hedron_core.audit.SecurityAuditEvent
    options:
      heading_level: 3

::: hedron_core.audit.set_security_audit_sink
    options:
      heading_level: 3

::: hedron_core.audit.emit_security_audit
    options:
      heading_level: 3

## Tracing (0.13)

::: hedron.tracing.configure_tracing
    options:
      heading_level: 3

::: hedron.tracing.span
    options:
      heading_level: 3

## Async helpers

::: hedron.async_utils.await_if_needed
    options:
      heading_level: 3

::: hedron.async_utils.gather
    options:
      heading_level: 3

::: hedron.async_utils.run_sync
    options:
      heading_level: 3

## Diagnostics

::: hedron_core.diagnostics.Diagnostic
    options:
      heading_level: 3

## See also

- [Hedron contract](HEDRON.md) · [Router](ROUTER.md) · [Interaction](INTERACTION.md)
- [Prepare](PREPARE.md) · [Audit](AUDIT.md) · [Tracing](TRACING.md)
- [Component](COMPONENT.md) · [Field](FIELD.md) · [SSE](SSE.md) · [Diagnostics](DIAGNOSTICS.md)
- [CLI](CLI.md) · [Page](PAGE.md) · [Adapters](ADAPTERS.md) · [Public API coverage map](COVERAGE.md)
- Component catalog (props/examples): [Components](../components/index.md)
