# Public API coverage map

Map of names in `hedron.__all__` to documentation. Prefer imports from `hedron` for
application code. Autodoc signatures: [AUTODOC.md](AUTODOC.md). Stability catalog:
[STABILITY.md](STABILITY.md).

## App, routing, interaction

| Export | Primary docs |
|---|---|
| `Hedron`, `mount_hedron_static` | [HEDRON.md](HEDRON.md), Autodoc |
| `MountPath`, `resolve_mount_path`, `resolve_mount_path_from_environ`, `normalize_mount_path`, `cookie_path_for_mount`, `mount_from_request`, `prefix_local_path` | [MOUNT.md](MOUNT.md), [deployment](../guides/deployment.md) |
| `HedronRouter`, `HedronRoute`, `ComponentRef`, `resolve_route_path` | [ROUTER.md](ROUTER.md), [ADDRESSABLE.md](ADDRESSABLE.md) |
| `InteractionResult`, `FragmentRegion`, `InteractionPolicy`, `HtmxRequest`, `OobUpdate` | [INTERACTION.md](INTERACTION.md), Autodoc |
| `ActionPhase`, `AsyncPhase`, `ActionState`, `ActionPolicy`, `OperationIdentity`, `ActionTrace`, `TraceEvent`, `ActionTransitionError` | [INTERACTION.md](INTERACTION.md#phase-061-lifecycle-contracts), [0.61 implementation](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/ACTION_STATE_ASYNC_061.md), [0.61 acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_61.md) |
| `begin_operation`, `complete_operation`, `transition_action` | [INTERACTION.md](INTERACTION.md#phase-061-lifecycle-contracts), [0.61 implementation](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/ACTION_STATE_ASYNC_061.md) |
| `AsyncRegion` | [INTERACTION.md](INTERACTION.md#phase-061-lifecycle-contracts), [component page](../components/async-region.md), [0.61 acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_61.md) |
| `NavigationDecision`, `NavigationIdentity`, `NavigationMachine`, `NavigationPhase`, `NavigationPolicy`, `NavigationState`, `PrefetchDecision`, `decide_prefetch`, `is_safe_navigation_url` | [INTERACTION_062.md](INTERACTION_062.md), [0.62 acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_62.md) |
| `BoundaryDecision`, `BoundaryPhase`, `FailureBoundary`, `FailureDisposition`, `IdentityRegistry`, `IdentityTarget`, `StateTransfer`, `StateTransferPolicy` | [INTERACTION_062.md](INTERACTION_062.md), [0.62 acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_62.md) |
| `HEDRON_NAVIGATION_HEADER`, `HEDRON_NAVIGATION_PHASE_HEADER`, `HEDRON_NAVIGATION_TARGET_HEADER`, `HEDRON_NAVIGATION_TITLE_HEADER`, `HEDRON_PREFETCH_HEADER`, `apply_navigation_headers`, `evaluate_prefetch_request`, `navigation_identity_from_request` | [INTERACTION_062.md](INTERACTION_062.md), [0.62 acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_62.md) |
| `FragmentHandle`, `BoundFragment`, `ActionHandle`, `Refresh`, `refresh`, `patches`, `FragmentHost`, `Patch`, `PatchSet`, `RefreshIntent` | [REFRESHABLE_VIEWS.md](REFRESHABLE_VIEWS.md) |
| `ViewParams`, `FormBody`, `Control`, `Refreshes`, `Updates`, `OutcomeMap`, `case`, `CommandResult`, `RefreshableView`, `CommandHandler`, `Sensitive`, `InstanceKey`, `TypeSchema`, `DependsOn`, `DependencyLifetime`, `DependencyPlan`, `BoundaryBindingPlan`, `RequiresScopes` | [TYPE_DRIVEN_AUTHORING.md](TYPE_DRIVEN_AUTHORING.md), [FASTAPI_PYDANTIC_CONVERGENCE.md](FASTAPI_PYDANTIC_CONVERGENCE.md) |
| `CatalogEntry`, `InteractionCatalog`, `InteractionManifest`, `PackageProjection`, `ProjectionCapability`, `CatalogVersionError` | [INTERACTION_CATALOG.md](INTERACTION_CATALOG.md) |
| `default_interaction_policy`, `form_sync_attrs`, `htmx_request`, `approved_headers`, `htmx_context` | [INTERACTION.md](INTERACTION.md), [htmx-interactions](../guides/htmx-interactions.md) |
| `swap`, `swap_oob`, `retarget`, `redirect_htmx` | [INTERACTION.md](INTERACTION.md) (day-1 ergonomics), Autodoc |
| `action_attrs`, `oob_swap` | [BUILT_INS.md](BUILT_INS.md), [INTERACTION.md](INTERACTION.md) |

## Progressive feature and styling authoring (0.58)

| Export | Primary docs |
|---|---|
| `ScreenHandle`, `ScreenLayout` | [HEDRON.md](HEDRON.md), [whats-new-0.58](../guides/whats-new-0.58.md), Autodoc |
| `DashboardWorkspace`, `DashboardHistory`, `CachePolicy` | [dashboards](../guides/dashboards.md), [whats-new-0.58](../guides/whats-new-0.58.md), Autodoc |
| `TaskFlow`, `JobScope`, `JobScopeProvider`, `PollPolicy`, `TaskUnavailablePolicy` | [JOBS.md](JOBS.md), [whats-new-0.58](../guides/whats-new-0.58.md), Autodoc |
| `SessionAuthFlow`, `AuthResult`, `AuthSuccess`, `AuthDenied`, `RateLimitPolicy`, `SessionRotationPolicy` | [AUTH.md](AUTH.md), [whats-new-0.58](../guides/whats-new-0.58.md) |
| `UploadFlow` | [file-upload](../examples/file-upload.md), [whats-new-0.58](../guides/whats-new-0.58.md), Autodoc |
| `DesignSystem`, `StyleRecipe`, `StyleScope` | [PRESENTATION.md](PRESENTATION.md), [StyleScope](../components/style-scope.md), [whats-new-0.58](../guides/whats-new-0.58.md) |
| `Color`, `ThemeSpec`, `ThemeBuilder`, `ThemePatch`, `ThemePackage`, `THEME_PACKAGE_COMPATIBILITY`, `ThemeValidationReport` | [Theme platform](THEME.md), [phase 0.60 implementation](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/THEME_PLATFORM_060.md) |
| `ComponentThemeContract`, `CoverageProfile`, `RecipeFamily`, `StyleContext` | [Theme platform](THEME.md), [phase 0.60 contract](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/theme-platform-contract-060.toml) |
| `ScrollRegion`, `ThemePicker`, `ThemePreference` | [Component demos](../components/index.md), [phase 0.60 acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_60.md) |
| `package_theme`, `load_theme_package`, `register_theme_package`, `conformance_report`, `diff_theme_specs`, `explain_theme_spec`, `validate_theme_spec`, `register_component_theme_contract`, `registered_component_theme_contracts`, `register_recipe_family`, `registered_recipe_families`, `resolve_theme_preference`, `theme_boot_asset`, `theme_markers` | [Theme platform](THEME.md), [phase 0.60 implementation](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/THEME_PLATFORM_060.md) |
| `ComponentStateMatrix`, `StateMatrixEntry`, `ThemeExport`, `ThemeResolution`, `build_state_matrix`, `compatibility_theme_vars`, `component_contract_manifest`, `derived_theme_tokens`, `export_theme`, `inspect_theme_css`, `resolve_theme`, `theme_contract_report` | [Theme platform](THEME.md), [phase 0.63 implementation](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/INTERACTION_TOOLING_063.md) |
| `TRACE_CONTRACT_SCHEMA`, `decode_interaction_trace`, `encode_interaction_trace`, `profile_interaction_trace`, `element_metadata_manifest`, `package_identity_manifest` | [Phase 0.63 implementation](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/INTERACTION_TOOLING_063.md) |

## Inference and model demos (0.18)

| Export / package | Primary docs |
|---|---|
| `ModelDemo`, `InferenceInterface`, `ActionRegistry`, `RegisteredAction` | [INFERENCE.md](INFERENCE.md), [model demos](../guides/model-demos.md), Autodoc |
| `ExampleSet`, `PredictionFeedback`, `InferencePolicy`, `InferenceWorkflow` | [INFERENCE.md](INFERENCE.md), Autodoc |
| `InteractionRecorder` (`hedron`) | [INFERENCE.md](INFERENCE.md) |
| `DashboardBinding`, `InteractionGraph`, `TriggerContext` | Import from **`hedron_core`** (not root `hedron.__all__`) — [dashboards](../guides/dashboards.md), Autodoc |
| `hedron_gradio.GradioClientAdapter` | [Gradio migration](../guides/gradio-migration.md) |

## Responses and live transport

| Export | Primary docs |
|---|---|
| `HTML`, `ComponentResponse`, `PageResponse`, `FragmentResponse`, `FileComponentResponse` | [RESPONSES.md](RESPONSES.md) |
| `hedron_response`, `merge_htmx_headers` | [RESPONSES.md](RESPONSES.md) |

!!! warning "Live helpers are experimental — not in `hedron.__all__`"

    Import SSE / streaming / WebSocket / preload helpers from **`hedron.experimental`**
    (a root `hedron.*` compat shim exists via `__getattr__`). Prefer
    [polling](../guides/live-interaction.md) in production. See
    [LIVE_DISPOSITION](LIVE_DISPOSITION.md).

| Symbol (via `hedron.experimental`) | Primary docs |
|---|---|
| `SseResponse`, `sse_response`, `job_status_sse_response`, `extension_script_tags` | [SSE.md](SSE.md), Autodoc |
| `StreamingComponentResponse`, `stream_tokens`, `stream_document`, `stream_chunked_list` | [STREAMING.md](STREAMING.md) |
| `accept_page_session_channel`, `send_region_update`, `origin_allowed`, `ALLOW_MISSING_ORIGIN` | [WEBSOCKET_CHANNEL.md](WEBSOCKET_CHANNEL.md) |
| `HX_PRELOADED`, `NavigationPreloadPolicy`, `apply_preload_headers`, `evaluate_preload_request` | [PRELOAD.md](PRELOAD.md) |

## Security and CSRF

| Export | Primary docs |
|---|---|
| `SecurityPolicy`, `SecurityProfile`, `SecurityHeadersPolicy` | [SECURITY_TYPES.md](SECURITY_TYPES.md), [CSRF_COMPOSITION.md](CSRF_COMPOSITION.md), [security guide](../guides/security.md), Autodoc |
| `CsrfField`, `Form`, `Hx`, `DoubleSubmitCookieCsrf`, `SessionTokenCsrf` | [CSRF_COMPOSITION.md](CSRF_COMPOSITION.md), [minimal form](../guides/minimal-form.md), Autodoc |
| `csrf_token_for_request` | Re-exported from `hedron`; [minimal form](../guides/minimal-form.md) (advanced), [SECURITY_TYPES.md](SECURITY_TYPES.md) |
| `SafeUrl`, `Secret`, `TrustedHtml`, `UrlPurpose` | [SECURITY_TYPES.md](SECURITY_TYPES.md) |
| `redirect_local`, `redirect_external`, `redirect_htmx` | [SECURITY_TYPES.md](SECURITY_TYPES.md), Autodoc |
| `hedron.oidc` (`OidcClientConfig`, PKCE/state/nonce, `login_url`, …) | [AUTH.md](AUTH.md), [authentication](../guides/authentication.md), Autodoc — **not** an IdP product |
| `OAuthHelper`, `create_oauth_client` | [AUTH.md](AUTH.md) (`hedron[auth]`) |

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

## Previously unmapped helpers and types

| Export | Primary docs |
|---|---|
| `ByteRangeNotSatisfiable` | [EXCEPTIONS.md](EXCEPTIONS.md), [media-downloads](../guides/media-downloads.md) |
| `CsrfStrategy` | [CSRF_COMPOSITION.md](CSRF_COMPOSITION.md), [EXCEPTIONS.md](EXCEPTIONS.md) |
| `CsrfValidationError` | [EXCEPTIONS.md](EXCEPTIONS.md), [CSRF_COMPOSITION.md](CSRF_COMPOSITION.md) |
| `FragmentRegionError` | [EXCEPTIONS.md](EXCEPTIONS.md), [INTERACTION.md](INTERACTION.md) |
| `Dialogue` | [Dialogue](../components/dialogue.md) |
| `DialogueTurn` | [EXCEPTIONS.md](EXCEPTIONS.md), [INFERENCE.md](INFERENCE.md) |
| `DirectoryUpload` | [DirectoryUpload](../components/directory-upload.md) |
| `DirectoryUploadFile` | [EXCEPTIONS.md](EXCEPTIONS.md), [DirectoryUpload](../components/directory-upload.md) |
| `ExampleItem` | [INFERENCE.md](INFERENCE.md) |
| `FeedbackPolicy` | [INFERENCE.md](INFERENCE.md) |
| `GalleryItem` | [EXCEPTIONS.md](EXCEPTIONS.md), [Gallery](../components/gallery.md) |
| `LoginCsrfField` | [CSRF_COMPOSITION.md](CSRF_COMPOSITION.md) |
| `ParameterViewer` | [ParameterViewer](../components/parameter-viewer.md) |
| `PredictionLabel` | [PredictionLabel](../components/prediction-label.md) |
| `PredictionScore` | [EXCEPTIONS.md](EXCEPTIONS.md), [INFERENCE.md](INFERENCE.md) |
| `StorageQuotaExceeded` | [EXCEPTIONS.md](EXCEPTIONS.md) |
| `ViewportHint` | [EXCEPTIONS.md](EXCEPTIONS.md) |
| `download_all_zip` | [media-downloads](../guides/media-downloads.md) |
| `parse_byte_range` | [media-downloads](../guides/media-downloads.md) |
| `redact_cookie_value` | [EXCEPTIONS.md](EXCEPTIONS.md) |
| `validate_directory_upload` | [EXCEPTIONS.md](EXCEPTIONS.md) |

## Built-in UI components (complete `__all__` inventory)

Constructor/props live on the [component catalog](../components/index.md). Index:
[BUILT_INS.md](BUILT_INS.md). FastAPI-only builtins also under Autodoc:
`AutoForm`, `ErrorState`, `InfiniteScroll`, `Loading`, `Pagination`, `ChatInput`,
`DownloadButton`, `FileUpload`, `safe_download_response`, plus layout helpers such as
`Page`, `Stack`, `Grid`, `Form`, `TextInput`, `RefreshButton`, `Poll`, `Lazy`
(error template outside `#…-body`), `Metric`, `Toast` (danger dismiss), `ToastHost`
(covered in sections above / component pages).

| Export | Primary docs |
|---|---|
| `ActionDock`, `Alert`, `AmbientBackdrop`, `AppShell`, `Aside`, `AttrHost`, `Badge` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `AccountSummary`, `AppFooter`, `Avatar`, `Brand`, `EnvironmentBanner`, `NavStatus` | [Components](../components/index.md), [PRESENTATION.md](PRESENTATION.md) |
| `BottomDock`, `Button`, `Card`, `Carousel`, `ChatMessage`, `Checkbox` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `ChipInput`, `CircularProgress`, `ClipboardCopy`, `CodeBlock`, `CodeViewer`, `ColorInput` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `ConfirmButton`, `Container`, `ContextMenu`, `DateInput`, `DateTimeInput`, `DescriptionList` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `Dialog`, `Divider`, `Expander`, `Footer`, `FormErrors`, `FormField` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `Fragment`, `Head`, `Header`, `Heading`, `Help`, `HelpInspector` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `GridItem`, `Identity`, `ResourceList`, `ResourceRow`, `Surface` | [Components](../components/index.md), [Identity](../components/identity.md), [PRESENTATION.md](PRESENTATION.md) |
| `HtmxLink`, `IconButton`, `Image`, `Inline`, `JSONViewer`, `Label` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `Link`, `LinkButton`, `List`, `Logo`, `Main`, `MainPanel` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `MarkerSpec`, `Math`, `MenuButton`, `MultiSelect`, `Nav`, `NavGroup`, `NavLink` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `NumberInput`, `OobHost`, `PageIcon`, `Pills`, `Popover`, `Progress` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `RadioGroup`, `RangeInput`, `RatingInput`, `Section`, `SegmentedControl`, `Select` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `SelectSlider`, `Sidebar`, `Skeleton`, `Spacer`, `Status`, `SubmitButton` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `Table`, `Tabs`, `Text`, `TextArea`, `Theme`, `TimeInput` | [Components](../components/index.md), [Tabs](../components/tabs.md), [BUILT_INS.md](BUILT_INS.md) |
| `Timeline`, `Title`, `ToggleSwitch`, `Tooltip` | [Components](../components/index.md), [BUILT_INS.md](BUILT_INS.md) |
| `PageHeader`, `SplitView`, `MasterDetail`, `FormGrid`, `ActionGroup` | [AUTHORING_LOOP.md](AUTHORING_LOOP.md), [WORKFLOW.md](WORKFLOW.md), [Components](../components/index.md) |
| `Capability` / `CapabilityProvider` / `enforce_capability` | [WORKFLOW.md](WORKFLOW.md) |
| `IdempotencyPolicy` / `MemoryReplayStore` | [WORKFLOW.md](WORKFLOW.md) |
| `UploadField` / `UploadHandle` / `materialize_upload` | [WORKFLOW.md](WORKFLOW.md) |
| `NonceContext` / `compose_csp` / `ingest_csp_report` | [WORKFLOW.md](WORKFLOW.md) |
| `WorkflowManifest` / `hedron upgrade-report` | [WORKFLOW.md](WORKFLOW.md), [CLI.md](CLI.md) |
| `SkipLink`, `RequestIndicator`, `ProcessFlow`, `FlowStep`, `ConnectorFlow`, `ConnectorNode`, `ConnectorTrack` | [AUTHORING_LOOP.md](AUTHORING_LOOP.md), [Components](../components/index.md) |
| `Icon`, `Typography`, `StateView`, `TableColumn` | [AUTHORING_LOOP.md](AUTHORING_LOOP.md), [Components](../components/index.md) |

## Data and charts (extras)

| Export | Extra | Primary docs |
|---|---|---|
| `Auto` | none | [AUTO.md](AUTO.md) |
| `DataTable`, `DataEditor`, `DataChanges`, `DataPage`, `DataQuery`, `DataSaveResult`, `InMemoryDataSource` | `hedron[data]` | [DATA.md](DATA.md), [DATA_SOURCE.md](DATA_SOURCE.md), [data-apps](../guides/data-apps.md) |
| `LineChart`, `AreaChart`, `BarChart`, `ScatterChart`, `MatplotlibChart`, `PlotlyChart`, `AltairChart` | `hedron[charts]` (Beta; first-party/Matplotlib Supported, Plotly/Altair Experimental) | [CHART.md](CHART.md) |

SQLAlchemy adapter: `hedron_data.sqlalchemy_source.SQLAlchemyDataSource` — see
[data-apps](../guides/data-apps.md) (not a top-level `hedron` re-export).

## Cache, state, color, assets

| Export | Primary docs |
|---|---|
| `cache_component`, `cache_data`, `invalidate_tags` | [CACHE.md](CACHE.md) |
| `SessionState`, `session_state` | [STATE.md](STATE.md) |
| `ColorMode`, `ColorModeToggle`, `apply_color_mode_cookie`, `read_color_mode_preference`, `resolve_color_mode`, `resolved_theme_from_request` | [COLORMODE.md](COLORMODE.md), [THEME.md](THEME.md) |
| `compile_css`, `styles_from_manifest`, `StyleSymbols` | [THEME.md](THEME.md), [CONFIGURATION.md](../CONFIGURATION.md) |
| `compile_palette`, `contrast_diagnostics`, `contrast_ratio` | [THEME.md](THEME.md), [AUTHORING_LOOP.md](AUTHORING_LOOP.md) |
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

Every name in `hedron.__all__` should appear in a table on this page. If a symbol has
no deep contract page, treat the component page, guide, or
[EXCEPTIONS.md](EXCEPTIONS.md) as normative, and open an issue when a signature or
error matrix is missing. Prefer expanding Autodoc members over duplicating narrative.

**Intentionally thin (Autodoc / guide / component page only):** icon helpers
(`get_icon`, `list_icons`, `register_icon`, `trusted_svg`), most UI component props
(component pages), and FastAPI-only builtin wrappers covered by
[BUILT_INS.md](BUILT_INS.md).
