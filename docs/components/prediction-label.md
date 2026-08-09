---
title: PredictionLabel
description: Ranked prediction labels with class identity and an accessible table encoding.
---

# `PredictionLabel`

Ranked prediction labels with class identity and an accessible table encoding.

| | |
|---|---|
| Import | `from hedron import PredictionLabel` |
| Distribution | `hedron` |
| Backend activity | No |
| Normal render mode | `RenderMode.FRAGMENT` |

## Live demo

<section class="hedron-component-demo" data-hedron-component-demo="PredictionLabel"><div class="hdc-stage"><div class="hdc-result"><strong>PredictionLabel</strong><span>Ranked prediction labels with class identity and an accessible table encoding.</span></div></div></section>

The preview is a local docs simulation (not a running Hedron server). Interactive demos show a “Simulated HTMX” trace when applicable.

## Basic use

```python
from hedron import PredictionLabel

component = PredictionLabel([{'class_id': 'cat', 'score': 0.9, 'calibrated': True}])
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

Phase 0.18 model-demo presentation. Retain class identity and non-color encodings for ranked scores.

This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform.

## Constructor and parameters

```python
PredictionLabel(scores, *, title='Predictions', threshold=None, class_=None, mark=None)
```

| Parameter | Type | Meaning |
|---|---|---|
| `scores` | `Sequence[PredictionScore | Mapping]` | Ranked class scores with optional precision/calibration. |
| `title` | `str` | Accessible table caption. |
| `threshold` | `float | None` | Optional decision threshold shown in the caption. |
| `mark` | `str | None` | Optional stable test mark (`data-hedron-mark`). |

## Composition and backend behavior

Keep `PredictionLabel` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

`PredictionLabel` is primarily presentational; keep any mutation on an explicit action or component route.

## Accessibility

Expose an HTML table (or equivalent) so screen-reader users can read class, score, and calibration without relying on color alone.

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- Do not treat PredictionLabel as ground truth; pair with PredictionFeedback for governed evaluation capture.
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode=RenderMode.FRAGMENT)
assert result.html
assert not result.diagnostics
```

[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)
