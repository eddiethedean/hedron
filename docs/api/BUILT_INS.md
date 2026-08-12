---
status: shipped
---

# Built-in component baseline

[Browse all built-in component demos](../components/index.md){ .md-button .md-button--primary }

This page is an **index** into dedicated [component pages](../components/index.md). Each
component page is the constructor/parameter reference (generated from live signatures when
the docs manifest is stubbed). Prefer those pages over treating this file as a full API
manual.

!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package
    maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` /
    `deferred`).

**Status:** Accepted · current train **0.32**

## How to use this index

1. Pick a component from the groups below (or search the [component catalog](../components/index.md)).
2. Open its page for signature, parameters, accessibility, and testing notes.
3. For HTMX interaction patterns, see [HTMX interactions](../guides/htmx-interactions.md).
4. For inference presentation widgets, also see [Inference API](INFERENCE.md).

## Document and composition

[`Page`](../components/page.md) · [`Fragment`](../components/fragment.md) ·
[`Head`](../components/head.md) · [`Title`](../components/title.md)

## Landmarks and layout

[`Header`](../components/header.md) · [`Main`](../components/main.md) ·
[`Nav`](../components/nav.md) · [`Aside`](../components/aside.md) ·
[`Footer`](../components/footer.md) · [`Section`](../components/section.md) ·
[`Container`](../components/container.md) · [`Stack`](../components/stack.md) ·
[`Inline`](../components/inline.md) · [`Grid`](../components/grid.md) ·
[`Divider`](../components/divider.md) · [`Spacer`](../components/spacer.md)

## Content and media

[`Heading`](../components/heading.md) · [`Text`](../components/text.md) ·
[`Link`](../components/link.md) · [`Image`](../components/image.md) ·
[`Audio`](../components/audio.md) · [`Video`](../components/video.md) ·
[`IFrame`](../components/i-frame.md) · [`PdfViewer`](../components/pdf-viewer.md) ·
[`CodeBlock`](../components/code-block.md) · [`List`](../components/list.md) ·
[`DescriptionList`](../components/description-list.md) · [`Table`](../components/table.md) ·
[`Markdown`](../components/markdown.md) · [`Math`](../components/math.md) ·
[`Map`](../components/map.md) · [`Gallery`](../components/gallery.md)

## Surfaces, controls, forms

[`Card`](../components/card.md) · [`Badge`](../components/badge.md) ·
[`Alert`](../components/alert.md) · [`Skeleton`](../components/skeleton.md) ·
[`Button`](../components/button.md) · [`ConfirmButton`](../components/confirm-button.md) ·
[`Form`](../components/form.md) · [`TextInput`](../components/text-input.md) ·
[`NumberInput`](../components/number-input.md) · [`DateInput`](../components/date-input.md) ·
[`MultiSelect`](../components/multi-select.md) · [`ToggleSwitch`](../components/toggle-switch.md) ·
[`CameraCapture`](../components/camera-capture.md) ·
[`MicrophoneCapture`](../components/microphone-capture.md) ·
[`DirectoryUpload`](../components/directory-upload.md) · …
[full forms group](../components/forms.md)

## Interaction (FastAPI / HTMX)

[`AutoForm`](../components/auto-form.md) · [`RefreshButton`](../components/refresh-button.md) ·
[`Lazy`](../components/lazy.md) · [`Poll`](../components/poll.md) ·
[`InfiniteScroll`](../components/infinite-scroll.md) ·
[`Pagination`](../components/pagination.md) · [`Loading`](../components/loading.md) ·
[`ErrorState`](../components/error-state.md) · [`ChatInput`](../components/chat-input.md) ·
[`ChatMessage`](../components/chat-message.md) · [`Dialog`](../components/dialog.md)

Helpers: `action_attrs`, `oob_swap` — see [Interaction](INTERACTION.md).

## Data, charts, utilities

[`Auto`](../components/auto.md) · [`DataTable`](../components/data-table.md) ·
[`DataEditor`](../components/data-editor.md) · charts via `hedron[charts]` —
[Charts API](CHART.md) · [`Metric`](../components/metric.md) ·
[`FileUpload`](../components/file-upload.md) ·
[`DownloadButton`](../components/download-button.md) ·
[`Progress`](../components/progress.md) · [`Toast`](../components/toast.md) ·
[`ColorModeToggle`](../components/color-mode-toggle.md)

## Inference presentation (0.18)

[`PredictionLabel`](../components/prediction-label.md) ·
[`ParameterViewer`](../components/parameter-viewer.md) ·
[`Dialogue`](../components/dialogue.md)

Supporting public types (not components): `PredictionScore`, `DialogueTurn`,
`GalleryItem`, `ExampleItem`, `FeedbackPolicy` — see [EXCEPTIONS.md](EXCEPTIONS.md)
(types section) and [INFERENCE.md](INFERENCE.md).

Non-UI contracts (`ModelDemo`, `ExampleSet`, `PredictionFeedback`, `InferenceWorkflow`)
are documented on [INFERENCE.md](INFERENCE.md), not as components.

## Upload / media helpers

| Export | Docs |
|---|---|
| `DirectoryUploadFile`, `validate_directory_upload` | [EXCEPTIONS.md](EXCEPTIONS.md), [`DirectoryUpload`](../components/directory-upload.md) |
| `parse_byte_range`, `download_all_zip`, `ByteRangeNotSatisfiable` | [Media downloads](../guides/media-downloads.md), [EXCEPTIONS.md](EXCEPTIONS.md) |

## Errors

This index does not define HTTP errors. Component render failures, CSRF, and fragment
authorization are documented on [CSRF composition](CSRF_COMPOSITION.md),
[Responses](RESPONSES.md), and [Public exceptions](EXCEPTIONS.md).

## Native HTML escape hatch

`html.<tag>(*children, **attributes)` — see any early component page or
[SECURITY_TYPES](SECURITY_TYPES.md) for `SafeUrl` / `TrustedHtml` rules.

## Naming rule

Hedron component names use PascalCase. Native elements use lowercase `hedron.html`
attributes and tags. Python keyword collisions use a trailing underscore such as
`class_`; rendered HTML always uses the canonical attribute name.

### Additive `class_` theme hooks

Content and control builtins such as `Button`, `LinkButton`, `SubmitButton`,
`IconButton`, `Text`, `Heading`, `Alert`, `Badge`, and `Status` accept optional
`class_`. Host theme classes are **appended after** Hedron’s own `hedron-*`
classes (for example
`Button("Save", variant="primary", class_="button button-primary")`).

Use `class_` only as a design-system bridge. Do **not** use it to bypass security
attributes, CSRF wiring, SafeUrl constraints, or other typed props — those remain
enforced on the component API.

## Historical phase notes

Phase 0.1–0.10 acceptance narratives remain in release notes / what’s-new pages. This
index tracks the living **0.30** built-in catalog — do not treat older phase lists as the
complete API.
