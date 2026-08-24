---
hide:
  - toc
---

# Component demos

Every public Hedron component has a dedicated page (searchable; linked from the category
pages below). The left nav lists **categories**, not every component — start with the
table of ten, then open a group. Static components use real semantic HTML. Features that
normally call an HTMX endpoint use a clearly labelled JavaScript simulation so loading,
replacement, retry, paging, polling, editing, and validation remain usable on the hosted
documentation site.

!!! info "What the simulation does"

    JavaScript supplies deterministic in-browser responses only inside these docs previews. Production examples keep authentication, authorization, CSRF, validation, persistence, caching, and fragment rendering on the Python server. Each interactive page explains that boundary.

## Start with these 10

| Component | Why |
|---|---|
| [`Page`](page.md) / [`Text`](text.md) | First full document |
| [`Stack`](stack.md) / [`Card`](card.md) | Layout and surfaces |
| [`Form`](form.md) / [`TextInput`](text-input.md) / [`SubmitButton`](submit-button.md) | Classic forms |
| [`Button`](button.md) / [`RefreshButton`](refresh-button.md) | Commands and HTMX refresh |
| [`DataTable`](data-table.md) | Tabular data (`hedron[data]`) |

Then browse the groups below. Golden path:
[HTMX interactions](../guides/htmx-interactions.md) →
[Minimal form](../guides/minimal-form.md).

Use the pages below to choose a component, inspect its output, understand its constructor, and test its accessibility and backend contract.

## Document and composition

Full pages, metadata, and fragment composition.

[`Page`](page.md) · [`Fragment`](fragment.md) · [`Head`](head.md) · [`Title`](title.md)

## Landmarks

Semantic regions that give a page its accessible structure. `Header`, `Main`, `Nav`, `Aside`, `Footer`, and `Section` are real typed exports with allowlisted safe HTML attributes, not factory variables.

[`Header`](header.md) · [`Main`](main.md) · [`Nav`](nav.md) · [`Aside`](aside.md) · [`Footer`](footer.md) · [`Section`](section.md)

## Layout

Explicit containers and one-dimensional or grid composition.

[`Container`](container.md) · [`PageHeader`](page-header.md) · [`SplitView`](split-view.md) · [`MasterDetail`](master-detail.md) · [`FormGrid`](form-grid.md) · [`ActionGroup`](action-group.md) · [`Stack`](stack.md) · [`Inline`](inline.md) · [`Grid`](grid.md) · [`GridItem`](grid-item.md) · [`Divider`](divider.md) · [`MainPanel`](main-panel.md) · [`AppShell`](app-shell.md) · [`SkipLink`](skip-link.md) · [`ProcessFlow`](process-flow.md) · [`FlowStep`](flow-step.md) · [`ConnectorNode`](connector-node.md) · [`ConnectorFlow`](connector-flow.md) · [`ConnectorTrack`](connector-track.md) · [`ScrollRegion`](scroll-region.md) · [`ActionDock`](action-dock.md) · [`BottomDock`](bottom-dock.md) · [`Spacer`](spacer.md) · [`NavGroup`](nav-group.md)

## Content

Text, links, media, code, lists, tables, and Markdown.

[`Heading`](heading.md) · [`Text`](text.md) · [`Link`](link.md) · [`Image`](image.md) · [`CodeBlock`](code-block.md) · [`List`](list.md) · [`DescriptionList`](description-list.md) · [`Table`](table.md) · [`Markdown`](markdown.md) · [`Typography`](typography.md) · [`Icon`](icon.md) · [`Avatar`](avatar.md) · [`Identity`](identity.md) · [`Audio`](audio.md) · [`PredictionLabel`](prediction-label.md) · [`ParameterViewer`](parameter-viewer.md) · [`Dialogue`](dialogue.md) · [`Gallery`](gallery.md) · [`GeoJSONLayer`](geo-json-layer.md) · [`GeolocationHint`](geolocation-hint.md) · [`IFrame`](i-frame.md) · [`Logo`](logo.md) · [`Map`](map.md) · [`Math`](math.md) · [`PageIcon`](page-icon.md) · [`PdfViewer`](pdf-viewer.md) · [`Video`](video.md)

## Surfaces and status

Cards, labels, alerts, and loading placeholders.

[`Card`](card.md) · [`Surface`](surface.md) · [`StyleScope`](style-scope.md) · [`Badge`](badge.md) · [`Alert`](alert.md) · [`Skeleton`](skeleton.md) · [`StateView`](state-view.md) · [`Carousel`](carousel.md) · [`ContextMenu`](context-menu.md) · [`Help`](help.md) · [`Popover`](popover.md) · [`Timeline`](timeline.md) · [`Tooltip`](tooltip.md) · [`AmbientBackdrop`](ambient-backdrop.md)

## Controls

Buttons and links for commands and navigation.

[`HtmxLink`](htmx-link.md) · [`NavLink`](nav-link.md) · [`Button`](button.md) · [`LinkButton`](link-button.md) · [`IconButton`](icon-button.md) · [`ClipboardCopy`](clipboard-copy.md) · [`ConfirmButton`](confirm-button.md) · [`MenuButton`](menu-button.md)

## Forms

Typed, labelled controls and validation presentation.

[`Form`](form.md) · [`Hx`](hx.md) · [`SwapReveal`](swap-reveal.md) · [`BusyRegion`](busy-region.md) · [`CsrfField`](csrf-field.md) · [`LoginCsrfField`](login-csrf-field.md) · [`FormField`](form-field.md) · [`Label`](label.md) · [`TextInput`](text-input.md) · [`TextArea`](text-area.md) · [`Select`](select.md) · [`Checkbox`](checkbox.md) · [`RadioGroup`](radio-group.md) · [`SubmitButton`](submit-button.md) · [`FormErrors`](form-errors.md) · [`AutoForm`](auto-form.md) · [`CameraCapture`](camera-capture.md) · [`ChipInput`](chip-input.md) · [`ColorInput`](color-input.md) · [`DateInput`](date-input.md) · [`DateTimeInput`](date-time-input.md) · [`DirectoryUpload`](directory-upload.md) · [`GeolocationButton`](geolocation-button.md) · [`MicrophoneCapture`](microphone-capture.md) · [`MultiSelect`](multi-select.md) · [`NumberInput`](number-input.md) · [`Pills`](pills.md) · [`RangeInput`](range-input.md) · [`RatingInput`](rating-input.md) · [`SegmentedControl`](segmented-control.md) · [`SelectSlider`](select-slider.md) · [`TimeInput`](time-input.md) · [`ToggleSwitch`](toggle-switch.md)

## Interaction

FastAPI and HTMX-oriented request/response components.

[`OobHost`](oob-host.md) · [`AttrHost`](attr-host.md) · [`SseRegion`](sse-region.md) · [`SseTrigger`](sse-trigger.md) · [`RequestIndicator`](request-indicator.md) · [`RefreshButton`](refresh-button.md) · [`Lazy`](lazy.md) · [`Poll`](poll.md) · [`InfiniteScroll`](infinite-scroll.md) · [`Pagination`](pagination.md) · [`Loading`](loading.md) · [`ErrorState`](error-state.md) · [`Dialog`](dialog.md) · [`ChatMessage`](chat-message.md) · [`ChatInput`](chat-input.md) · [`AsyncRegion`](async-region.md)

## Data

Automatic rendering, tabular display, and editable data.

[`Auto`](auto.md) · [`DataTable`](data-table.md) · [`ResourceList`](resource-list.md) · [`ResourceRow`](resource-row.md) · [`DataEditor`](data-editor.md)

## Utilities

Metrics, viewers, progress, status, disclosure, tabs, and files.

[`Brand`](brand.md) · [`AccountSummary`](account-summary.md) · [`EnvironmentBanner`](environment-banner.md) · [`NavStatus`](nav-status.md) · [`AppFooter`](app-footer.md) · [`Metric`](metric.md) · [`FileUpload`](file-upload.md) · [`DownloadButton`](download-button.md) · [`CodeViewer`](code-viewer.md) · [`JSONViewer`](json-viewer.md) · [`Progress`](progress.md) · [`Status`](status.md) · [`Toast`](toast.md) · [`ToastHost`](toast-host.md) · [`Expander`](expander.md) · [`Tabs`](tabs.md) · [`Sidebar`](sidebar.md) · [`CircularProgress`](circular-progress.md) · [`HelpInspector`](help-inspector.md)

## Theme

User-facing color-mode preference controls.

[`ThemePicker`](theme-picker.md) · [`ColorModeToggle`](color-mode-toggle.md)

## Charts

Accessible visualization components and optional plotting adapters.

[`Chart`](chart.md) · [`LineChart`](line-chart.md) · [`AreaChart`](area-chart.md) · [`BarChart`](bar-chart.md) · [`ScatterChart`](scatter-chart.md) · [`MatplotlibChart`](matplotlib-chart.md) · [`PlotlyChart`](plotly-chart.md) · [`AltairChart`](altair-chart.md)
