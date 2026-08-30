---
title: Video
description: Accessible HTML video player with SafeUrl source.
---

# `Video`

Accessible HTML video player with SafeUrl source.

| | |
|---|---|
| Import | `from hedron import Video` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="Video"><div class="hdc-stage"><div class="hdc-download"><span class="hdc-file-icon" aria-hidden="true">▶</span><span><strong>Video player</strong><small>Requires a SafeUrl source in the real component.</small></span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import Video
component = Video('/media/clip.mp4')
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```text
Video(src: 'SafeUrl | str', *, tracks: 'Sequence[Mapping[str, Any] | NodeLike]' = (), controls: 'bool' = True, autoplay: 'bool' = False, loop: 'bool' = False, muted: 'bool' = False, preload: 'str | None' = None, poster: 'SafeUrl | str | None' = None, allow_external: 'bool' = False, class_: 'str | None' = None, mark: 'str | None' = None, **kwargs: 'object') -> 'None'
```

| Parameter | Type | Meaning |
|---|---|---|
| `src` | `SafeUrl | str` | Media or document URL (`SafeUrl` preferred for untrusted input). |
| `tracks` | `Sequence[Mapping[str, Any] | NodeLike]` | Optional track elements or track mappings. Default: `()`. |
| `controls` | `bool` | Whether native media controls are shown. Default: `True`. |
| `autoplay` | `bool` | Whether media attempts autoplay (browser-gated). Default: `False`. |
| `loop` | `bool` | Whether media loops. Default: `False`. |
| `muted` | `bool` | Whether media starts muted. Default: `False`. |
| `preload` | `str | None` | Native media `preload` hint. Default: `None`. |
| `poster` | `SafeUrl | str | None` | Optional video poster image URL. Default: `None`. |
| `allow_external` | `bool` | Allow non-same-origin / non-asset URLs when True. Default: `False`. |
| `class_` | `str | None` | Optional CSS class string (`class` in HTML). Default: `None`. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). Default: `None`. |

## Composition and backend behavior

Keep `Video` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`Video` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Keyboard and screen-reader operable; no-JS fallback required where interactive.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not treat client-only hints (geolocation, browser storage) as authorization.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
