---
hide:
  - toc
---

# Component demos

Every public Hedron component has a dedicated, usable example and a detailed operating guide. Static components use real semantic HTML. Features that normally call an HTMX endpoint use a clearly labelled JavaScript simulation so loading, replacement, retry, paging, polling, editing, and validation remain usable on the hosted documentation site.

!!! info "What the simulation does"

    JavaScript supplies deterministic in-browser responses only inside these docs previews. Production examples keep authentication, authorization, CSRF, validation, persistence, caching, and fragment rendering on the Python server. Each interactive page explains that boundary.

Use the pages below to choose a component, inspect its output, understand its constructor, and test its accessibility and backend contract.

## Document and composition

Full pages, metadata, and fragment composition.

[`Page`](page.md) · [`Fragment`](fragment.md) · [`Head`](head.md) · [`Title`](title.md)

## Landmarks

Semantic regions that give a page its accessible structure.

[`Header`](header.md) · [`Main`](main.md) · [`Nav`](nav.md) · [`Aside`](aside.md) · [`Footer`](footer.md) · [`Section`](section.md)

## Layout

Explicit containers and one-dimensional or grid composition.

[`Container`](container.md) · [`Stack`](stack.md) · [`Inline`](inline.md) · [`Grid`](grid.md) · [`Divider`](divider.md)

## Content

Text, links, media, code, lists, tables, and Markdown.

[`Heading`](heading.md) · [`Text`](text.md) · [`Link`](link.md) · [`Image`](image.md) · [`CodeBlock`](code-block.md) · [`List`](list.md) · [`DescriptionList`](description-list.md) · [`Table`](table.md) · [`Markdown`](markdown.md)

## Surfaces and status

Cards, labels, alerts, and loading placeholders.

[`Card`](card.md) · [`Badge`](badge.md) · [`Alert`](alert.md) · [`Skeleton`](skeleton.md)

## Controls

Buttons and links for commands and navigation.

[`Button`](button.md) · [`LinkButton`](link-button.md) · [`IconButton`](icon-button.md)

## Forms

Typed, labelled controls and validation presentation.

[`Form`](form.md) · [`FormField`](form-field.md) · [`Label`](label.md) · [`TextInput`](text-input.md) · [`TextArea`](text-area.md) · [`Select`](select.md) · [`Checkbox`](checkbox.md) · [`RadioGroup`](radio-group.md) · [`SubmitButton`](submit-button.md) · [`FormErrors`](form-errors.md) · [`AutoForm`](auto-form.md)

## Interaction

FastAPI and HTMX-oriented request/response components.

[`RefreshButton`](refresh-button.md) · [`Lazy`](lazy.md) · [`Poll`](poll.md) · [`InfiniteScroll`](infinite-scroll.md) · [`Pagination`](pagination.md) · [`Loading`](loading.md) · [`ErrorState`](error-state.md) · [`Dialog`](dialog.md) · [`ChatMessage`](chat-message.md) · [`ChatInput`](chat-input.md)

## Data

Automatic rendering, tabular display, and editable data.

[`Auto`](auto.md) · [`DataTable`](data-table.md) · [`DataEditor`](data-editor.md)

## Utilities

Metrics, viewers, progress, status, disclosure, tabs, and files.

[`Metric`](metric.md) · [`FileUpload`](file-upload.md) · [`DownloadButton`](download-button.md) · [`CodeViewer`](code-viewer.md) · [`JSONViewer`](json-viewer.md) · [`Progress`](progress.md) · [`Status`](status.md) · [`Toast`](toast.md) · [`Expander`](expander.md) · [`Tabs`](tabs.md) · [`Sidebar`](sidebar.md)

## Theme

User-facing color-mode preference controls.

[`ColorModeToggle`](color-mode-toggle.md)

## Charts

Accessible visualization components and optional plotting adapters.

[`LineChart`](line-chart.md) · [`AreaChart`](area-chart.md) · [`BarChart`](bar-chart.md) · [`ScatterChart`](scatter-chart.md) · [`MatplotlibChart`](matplotlib-chart.md) · [`PlotlyChart`](plotly-chart.md) · [`AltairChart`](altair-chart.md)
