---
description: Generated public Hedron signatures for exact parameter and member lookup.
search:
  boost: 0.2
---

# Autodoc — public signatures

Generated signatures via **mkdocstrings** for the public surface used in Learn / Adopt
paths, mount helpers, HTMX helpers, models, CSRF / form composition, and
`hedron.experimental` live APIs.

This page expands signatures for the public surface used most often in Learn and Adopt
paths. Prefer hand-maintained contract pages for narrative and errors; use Autodoc to
verify parameter lists against installed sources. CI requires every `hedron.__all__`
export to appear in the [coverage map](COVERAGE.md), while every built-in constructor is
covered by the generated [component catalog](../components/index.md). Live SSE /
streaming / WebSocket helpers are
**not** in `__all__` — import from `hedron.experimental` (Autodoc below uses that path).

**Page template for hand contracts:** Example → Signature/members → Parameters →
Returns → Errors → See also ([Field](FIELD.md) is the gold standard). Outline pages
(`ColorMode`, `Utility components`, `Data sources`) defer full tables here or to
Components.

Stability: [Stability](STABILITY.md). Overview: [API overview](README.md).
Narrative: [Hedron](HEDRON.md) · [Interaction](INTERACTION.md) ·
[CSRF composition](CSRF_COMPOSITION.md) · [Inference](INFERENCE.md).

## Inference and model demos (0.18)

::: hedron_core.model_demo.ActionRegistry
    options:
      members:
        - register_action
        - register_adapter
        - get_action
        - get_adapter
      heading_level: 3

::: hedron_core.model_demo.InferenceInterface
    options:
      heading_level: 3

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

## Dashboards (0.17)

::: hedron_core.dashboard.DashboardBinding
    options:
      heading_level: 3

::: hedron_core.dashboard.InteractionGraph
    options:
      members:
        - declare_inputs
        - register
        - bindings
        - topological_order
      heading_level: 3

::: hedron_core.dashboard.TriggerContext
    options:
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
        - resolve_csrf_strategy
      heading_level: 3

::: hedron.security.policy.SecurityProfile
    options:
      heading_level: 3

::: hedron_core.security_policy.SecurityHeadersPolicy
    options:
      heading_level: 3

::: hedron.security.csrf.csrf_token_for_request
    options:
      heading_level: 3

::: hedron_core.csrf_strategy.DoubleSubmitCookieCsrf
    options:
      heading_level: 3

::: hedron_core.csrf_strategy.SessionTokenCsrf
    options:
      heading_level: 3

::: hedron_core.builtins.forms.CsrfField
    options:
      heading_level: 3

::: hedron_core.builtins.forms.Form
    options:
      heading_level: 3

::: hedron_core.builtins.forms.Hx
    options:
      heading_level: 3

::: hedron.security.redirects.redirect_local
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

## Live helpers (canonical: `hedron.experimental`)

Import SSE / streaming / WebSocket helpers from **`hedron.experimental`** (polling remains
Supported). Compat shims under `hedron.sse` / `hedron.streaming` / `hedron.websocket_channel`
exist but are not the Autodoc path below.

::: hedron.experimental.sse_response
    options:
      heading_level: 3

::: hedron.experimental.job_status_sse_response
    options:
      heading_level: 3

::: hedron.experimental.SseResponse
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

::: hedron.experimental.StreamingComponentResponse
    options:
      heading_level: 3

::: hedron.experimental.stream_tokens
    options:
      heading_level: 3

::: hedron.experimental.stream_chunked_list
    options:
      heading_level: 3

::: hedron.experimental.stream_document
    options:
      heading_level: 3

::: hedron.experimental.accept_page_session_channel
    options:
      heading_level: 3

::: hedron.experimental.send_region_update
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

## Interaction day-1 helpers

::: hedron_core.interaction.FragmentRegion
    options:
      heading_level: 3

::: hedron_core.interaction.InteractionResult
    options:
      heading_level: 3

::: hedron.interaction.swap
    options:
      heading_level: 3

::: hedron.builtins.Poll
    options:
      heading_level: 3

## Public exceptions and helpers

Narrative: [EXCEPTIONS.md](EXCEPTIONS.md).

::: hedron_core.csrf_strategy.CsrfValidationError
    options:
      heading_level: 3

::: hedron_core.csrf_strategy.CsrfStrategy
    options:
      heading_level: 3

::: hedron.builtins.media.ByteRangeNotSatisfiable
    options:
      heading_level: 3

::: hedron_core.browser.StorageQuotaExceeded
    options:
      heading_level: 3

::: hedron_core.browser.ViewportHint
    options:
      heading_level: 3

::: hedron_core.browser.redact_cookie_value
    options:
      heading_level: 3

::: hedron_core.builtins.forms_extra.DirectoryUploadFile
    options:
      heading_level: 3

::: hedron_core.builtins.forms_extra.validate_directory_upload
    options:
      heading_level: 3

::: hedron_core.builtins.model_demo.PredictionScore
    options:
      heading_level: 3

::: hedron_core.builtins.model_demo.DialogueTurn
    options:
      heading_level: 3

::: hedron_core.builtins.media.GalleryItem
    options:
      heading_level: 3

::: hedron.builtins.media.parse_byte_range
    options:
      heading_level: 3

## Models, mount, and HTMX helpers

::: hedron_core.models.Props
    options:
      heading_level: 3

::: hedron_core.models.FormModel
    options:
      heading_level: 3

::: hedron_core.security.UrlPurpose
    options:
      heading_level: 3

::: hedron.mount.MountPath
    options:
      heading_level: 3

::: hedron.mount.resolve_mount_path
    options:
      heading_level: 3

::: hedron.mount.normalize_mount_path
    options:
      heading_level: 3

::: hedron.mount.cookie_path_for_mount
    options:
      heading_level: 3

::: hedron.mount.mount_from_request
    options:
      heading_level: 3

::: hedron.mount.prefix_local_path
    options:
      heading_level: 3

::: hedron.interaction.HtmxRequest
    options:
      heading_level: 3

::: hedron_core.interaction.default_interaction_policy
    options:
      heading_level: 3

::: hedron_core.interaction.form_sync_attrs
    options:
      heading_level: 3

::: hedron.interaction.htmx_request
    options:
      heading_level: 3

::: hedron.htmx.htmx_context
    options:
      heading_level: 3

::: hedron.htmx.approved_headers
    options:
      heading_level: 3

::: hedron.builtins.action_attrs
    options:
      heading_level: 3

::: hedron.builtins.oob_swap
    options:
      heading_level: 3

::: hedron.responses.FileComponentResponse
    options:
      heading_level: 3

::: hedron.responses.merge_htmx_headers
    options:
      heading_level: 3

::: hedron.responses.render_interaction
    options:
      heading_level: 3

::: hedron.responses.render_component_response
    options:
      heading_level: 3

::: hedron_core.addressable.addressable
    options:
      heading_level: 3

::: hedron.routing.reverse.ComponentRef
    options:
      heading_level: 3

::: hedron.routing.reverse.resolve_route_path
    options:
      heading_level: 3

::: hedron.security.redirects.redirect_external
    options:
      heading_level: 3

::: hedron_core.theme.Theme
    options:
      heading_level: 3

::: hedron_core.browser.BrowserContext
    options:
      heading_level: 3

## Built-in components (Autodoc sample)

Full constructor tables remain on [Components](../components/index.md). Autodoc below
covers additional frequently used exports from `hedron.__all__`.

::: hedron_core.builtins.shell.AppShell
    options:
      heading_level: 3

::: hedron_core.builtins.surfaces.Alert
    options:
      heading_level: 3

::: hedron_core.builtins.surfaces.Badge
    options:
      heading_level: 3

::: hedron_core.builtins.forms.Checkbox
    options:
      heading_level: 3

::: hedron_core.builtins.forms.Select
    options:
      heading_level: 3

::: hedron_core.builtins.forms.TextArea
    options:
      heading_level: 3

::: hedron_core.builtins.forms.FormField
    options:
      heading_level: 3

::: hedron_core.builtins.forms.FormErrors
    options:
      heading_level: 3

::: hedron_core.builtins.forms.Label
    options:
      heading_level: 3

::: hedron.builtins.ErrorState
    options:
      heading_level: 3

::: hedron.builtins.Loading
    options:
      heading_level: 3

::: hedron.builtins.Lazy
    options:
      heading_level: 3

::: hedron.builtins.Pagination
    options:
      heading_level: 3

::: hedron.builtins.InfiniteScroll
    options:
      heading_level: 3

::: hedron.builtins.files.FileUpload
    options:
      heading_level: 3

::: hedron.builtins.files.DownloadButton
    options:
      heading_level: 3

::: hedron.builtins.files.safe_download_response
    options:
      heading_level: 3

::: hedron_core.builtins.content.CodeBlock
    options:
      heading_level: 3

::: hedron_core.builtins.content.Table
    options:
      heading_level: 3

::: hedron_core.builtins.utilities.Tabs
    options:
      heading_level: 3

::: hedron_core.builtins.content.Link
    options:
      heading_level: 3

::: hedron_core.builtins.landmarks.Nav
    options:
      heading_level: 3

::: hedron_core.builtins.shell.HtmxLink
    options:
      heading_level: 3

::: hedron_core.auto.Auto
    options:
      heading_level: 3

## See also

- [Hedron contract](HEDRON.md) · [Router](ROUTER.md) · [Interaction](INTERACTION.md)
- [Prepare](PREPARE.md) · [Audit](AUDIT.md) · [Tracing](TRACING.md)
- [Component](COMPONENT.md) · [Field](FIELD.md) · [SSE](SSE.md) · [Diagnostics](DIAGNOSTICS.md)
- [Exceptions](EXCEPTIONS.md) · [CLI](CLI.md) · [Page](PAGE.md) · [Adapters](ADAPTERS.md)
- [Public API coverage map](COVERAGE.md)
- Component catalog (props/examples): [Components](../components/index.md)
