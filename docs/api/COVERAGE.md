# Public API coverage map

Map of names in `hedron.__all__` to documentation. Prefer imports from `hedron` for
application code. Autodoc signatures: [AUTODOC.md](AUTODOC.md). Stability catalog:
[STABILITY.md](STABILITY.md).

## App, routing, interaction

| Export | Primary docs |
|---|---|
| `Hedron`, `mount_hedron_static` | [HEDRON.md](HEDRON.md), Autodoc |
| `HedronRouter`, `HedronRoute`, `ComponentRef`, `resolve_route_path` | [ROUTER.md](ROUTER.md), [ADDRESSABLE.md](ADDRESSABLE.md) |
| `InteractionResult`, `FragmentRegion`, `InteractionPolicy`, `HtmxRequest`, `OobUpdate` | [INTERACTION.md](INTERACTION.md), Autodoc |
| `default_interaction_policy`, `form_sync_attrs`, `htmx_request`, `approved_headers`, `htmx_context` | [INTERACTION.md](INTERACTION.md), [htmx-interactions](../guides/htmx-interactions.md) |
| `action_attrs`, `oob_swap` | [BUILT_INS.md](BUILT_INS.md), [INTERACTION.md](INTERACTION.md) |

## Inference and model demos (0.18)

| Export / package | Primary docs |
|---|---|
| `ModelDemo`, `InferenceInterface`, `ActionRegistry`, `RegisteredAction` | [INFERENCE.md](INFERENCE.md), [model demos](../guides/model-demos.md) |
| `ExampleSet`, `PredictionFeedback`, `InferencePolicy`, `InferenceWorkflow` | [INFERENCE.md](INFERENCE.md) |
| `InteractionRecorder` (`hedron`) | [INFERENCE.md](INFERENCE.md) |
| `hedron_gradio.GradioClientAdapter` | [Gradio migration](../guides/gradio-migration.md) |

## Responses and live transport

| Export | Primary docs |
|---|---|
| `HTML`, `ComponentResponse`, `PageResponse`, `FragmentResponse`, `FileComponentResponse` | [RESPONSES.md](RESPONSES.md) |
| `hedron_response`, `merge_htmx_headers` | [RESPONSES.md](RESPONSES.md) |
| `SseResponse`, `sse_response`, `job_status_sse_response`, `extension_script_tags` | [SSE.md](SSE.md), Autodoc |
| `StreamingComponentResponse`, `stream_tokens`, `stream_document`, `stream_chunked_list` | [STREAMING.md](STREAMING.md) |
| `accept_page_session_channel`, `send_region_update`, `origin_allowed`, `ALLOW_MISSING_ORIGIN` | [WEBSOCKET_CHANNEL.md](WEBSOCKET_CHANNEL.md) |
| `HX_PRELOADED`, `NavigationPreloadPolicy`, `apply_preload_headers`, `evaluate_preload_request` | [PRELOAD.md](PRELOAD.md) |

## Security and CSRF

| Export | Primary docs |
|---|---|
| `SecurityPolicy`, `SecurityProfile` | [SECURITY_TYPES.md](SECURITY_TYPES.md), [security guide](../guides/security.md) |
| `csrf_token_for_request` | Re-exported from `hedron`; [minimal form](../guides/minimal-form.md), [SECURITY_TYPES.md](SECURITY_TYPES.md) |
| `SafeUrl`, `Secret`, `TrustedHtml`, `UrlPurpose` | [SECURITY_TYPES.md](SECURITY_TYPES.md) |
| `redirect_local`, `redirect_external`, `redirect_htmx` | [SECURITY_TYPES.md](SECURITY_TYPES.md), Autodoc |

## Media, browser, and downloads

| Export | Primary docs |
|---|---|
| `Audio`, `Video`, `CameraCapture`, `MicrophoneCapture`, `IFrame`, `PdfViewer`, `Map`, `GeoJSONLayer`, `Gallery` | [Component pages](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `media_file_response`, `safe_download_response` | [Media downloads](../guides/media-downloads.md), Autodoc |
| `BrowserContext`, `browser_context`, `browser_context_from_request` | Autodoc; request-scoped browser hints (not authorization) |
| `BrowserStorage`, `BrowserStorageUnavailable` | Autodoc; client storage is spoofable — never authorize from it |
| `GeolocationButton`, `GeolocationHint` | [Component pages](../components/geolocation-button.md); coordinates are client-reported |
| `InteractionRecorder`, `RecordedExchange`, `RecordingSnippet` | [INFERENCE.md](INFERENCE.md) |
| `render`, `render_component_response`, `render_interaction`, `RenderContext`, `RenderMode`, `RenderResult` | [RENDERING.md](RENDERING.md), [INTERACTION.md](INTERACTION.md) |

## Built-in UI components

Documented primarily on [component pages](../components/index.md) and
[BUILT_INS.md](BUILT_INS.md). Includes layout (`Page`, `Stack`, `Grid`, …), forms
(`Form`, `TextInput`, …), interaction (`RefreshButton`, `Poll`, `Lazy`, …), and
utilities (`Metric`, `Toast`, …).

FastAPI-only builtins also listed under Autodoc / built-ins:
`AutoForm`, `ErrorState`, `InfiniteScroll`, `Loading`, `Pagination`, `ChatInput`,
`DownloadButton`, `FileUpload`, `safe_download_response`.

## Data and charts (extras)

| Export | Extra | Primary docs |
|---|---|---|
| `Auto` | none | [AUTO.md](AUTO.md) |
| `DataTable`, `DataEditor`, `DataChanges`, `DataPage`, `DataQuery`, `DataSaveResult`, `InMemoryDataSource` | `hedron[data]` | [DATA.md](DATA.md), [DATA_SOURCE.md](DATA_SOURCE.md), [data-apps](../guides/data-apps.md) |
| `LineChart`, `AreaChart`, `BarChart`, `ScatterChart`, `MatplotlibChart`, `PlotlyChart`, `AltairChart` | `hedron[charts]` (Alpha) | [CHART.md](CHART.md) |

SQLAlchemy adapter: `hedron_data.sqlalchemy_source.SQLAlchemyDataSource` — see
[data-apps](../guides/data-apps.md) (not a top-level `hedron` re-export).

## Cache, state, color, assets

| Export | Primary docs |
|---|---|
| `cache_component`, `cache_data`, `invalidate_tags` | [CACHE.md](CACHE.md) |
| `SessionState`, `session_state` | [STATE.md](STATE.md) |
| `ColorMode`, `ColorModeToggle`, `apply_color_mode_cookie`, `read_color_mode_preference`, `resolve_color_mode`, `resolved_theme_from_request` | [COLORMODE.md](COLORMODE.md), [THEME.md](THEME.md) |
| `compile_css`, `styles_from_manifest`, `StyleSymbols` | [THEME.md](THEME.md), [CONFIGURATION.md](../CONFIGURATION.md) |
| `get_icon`, `list_icons`, `register_icon`, `trusted_svg` | Component / theme docs; icons live in `hedron_core` |

## Async helpers and misc

| Export | Primary docs |
|---|---|
| `await_if_needed`, `gather`, `run_sync` | Autodoc; sync/async boundary in handlers |
| `addressable`, `Field`, `Model`, `Props`, `FormModel`, `Component`, `render`, `RenderContext`, `RenderMode`, `RenderResult` | [COMPONENT.md](COMPONENT.md), [FIELD.md](FIELD.md), [MODELS.md](MODELS.md), [RENDERING.md](RENDERING.md) |
| `html` | Tag helpers used in guides |
| `Markdown`, `highlight_code`, `process_image`, `validate_email_address` | [CONTENT.md](CONTENT.md) |
| `OAuthHelper`, `create_oauth_client` | [AUTH.md](AUTH.md) |
| `__version__` | Package metadata |

## Phase 0.13 surfaces (`hedron_core` / `hedron.tracing`)

| Symbol | Primary docs |
|---|---|
| `PrepareContext`, `PartialFailurePolicy`, `prepare_tree` | [PREPARE.md](PREPARE.md) |
| `SecurityAuditSink`, `set_security_audit_sink`, `emit_security_audit`, … | [AUDIT.md](AUDIT.md) |
| `configure_tracing`, `span`, `TraceConfig` | [TRACING.md](TRACING.md) |

## Gaps policy

If a symbol is in `__all__` but only listed here (no deep contract page), treat the
component page or guide as normative for behavior, and open an issue when a signature
or error matrix is missing. Prefer expanding Autodoc members over duplicating narrative.

**Intentionally thin (Autodoc / guide only):** icon helpers (`get_icon`, `list_icons`,
`register_icon`, `trusted_svg`), some response merge helpers, and FastAPI-only builtin
wrappers already covered by [BUILT_INS.md](BUILT_INS.md) / component pages.
