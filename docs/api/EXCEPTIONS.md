# Public exceptions

!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Package maturity (Beta/Alpha) is separate from API level.

Public exception and failure types re-exported from `hedron` (and related helpers that
raise ordinary `ValueError`). Prefer catching these by type when writing host adapters
or shared libraries. HTTP mapping for CSRF failures remains **403** on built-in
profiles — see [CSRF composition](CSRF_COMPOSITION.md).

## `CsrfValidationError`

Raised by pluggable CSRF strategies (`DoubleSubmitCookieCsrf`, `SessionTokenCsrf`) when
`validate(...)` fails. Host adapters map this to HTTP **403**.

```python
from hedron import CsrfValidationError, DoubleSubmitCookieCsrf

strategy = DoubleSubmitCookieCsrf()
try:
    strategy.validate(cookie="a", form_token="b", header_token=None)
except CsrfValidationError:
    ...  # typically → HTTP 403
```

Typical message: `"CSRF validation failed"`.

::: hedron_core.csrf_strategy.CsrfValidationError
    options:
      heading_level: 3

## `FragmentRegionError`

Raised when an HTMX `HX-Target` (or resolved `region_id`) is not an authorized
`FragmentRegion`. Subclass of `ValueError` with `.requested`, `.declared`, and `.code`
(default `HED-HTMX-0001`). FastAPI/`HedronRoute` and the Flask/Django adapters map this
to HTTP **403**.

```python
from hedron import FragmentRegionError, InteractionPolicy
from hedron_core.interaction import authorize_htmx_target

policy = InteractionPolicy(declared_regions=())
try:
    authorize_htmx_target(policy, "#main", is_htmx=True)
except FragmentRegionError as exc:
    assert exc.code == "HED-HTMX-0001"
    ...  # typically → HTTP 403
```

See [Interaction](INTERACTION.md) and [HTMX interactions](../guides/htmx-interactions.md).

::: hedron_core.interaction.FragmentRegionError
    options:
      heading_level: 3

## `ByteRangeNotSatisfiable`

Raised when a media byte-range request cannot be satisfied. Subclass of `ValueError`
with a `.size` attribute. Media helpers map this to HTTP **416** and
`Content-Range: bytes */{size}`.

See [Media downloads](../guides/media-downloads.md).

::: hedron.builtins.media.ByteRangeNotSatisfiable
    options:
      heading_level: 3

## `StorageQuotaExceeded`

Raised by `BrowserStorage.set` when a namespace exceeds `max_entries` or `max_bytes`.
Subclass of `RuntimeError`. This is a **quota** failure, not an authorization decision —
client storage remains spoofable.

Related: `BrowserStorageUnavailable` when the client storage API is unavailable.

::: hedron_core.browser.StorageQuotaExceeded
    options:
      heading_level: 3

## Directory upload validation

`validate_directory_upload(...)` and `DirectoryUploadFile` support
[`DirectoryUpload`](../components/directory-upload.md). Validation failures raise
`ValueError` (path traversal, `max_files`, `max_total_size`) — not a dedicated exception
class.

::: hedron_core.builtins.forms_extra.DirectoryUploadFile
    options:
      heading_level: 3

::: hedron_core.builtins.forms_extra.validate_directory_upload
    options:
      heading_level: 3

## Browser helpers

`ViewportHint` and `redact_cookie_value` are public browser-context helpers. Cookie
redaction is for logs/diagnostics — never treat client hints as authorization.

::: hedron_core.browser.ViewportHint
    options:
      heading_level: 3

::: hedron_core.browser.redact_cookie_value
    options:
      heading_level: 3

## Inference presentation types

Typed rows used by inference UI components (not raised errors):

| Type | Used by |
|---|---|
| `PredictionScore` | [`PredictionLabel`](../components/prediction-label.md) |
| `DialogueTurn` | [`Dialogue`](../components/dialogue.md) |
| `GalleryItem` | [`Gallery`](../components/gallery.md) |

See [Inference](INFERENCE.md) and [BUILT_INS](BUILT_INS.md).

::: hedron_core.builtins.model_demo.PredictionScore
    options:
      heading_level: 3

::: hedron_core.builtins.model_demo.DialogueTurn
    options:
      heading_level: 3

::: hedron_core.builtins.media.GalleryItem
    options:
      heading_level: 3

## See also

- [CSRF composition](CSRF_COMPOSITION.md) · [Interaction](INTERACTION.md)
- [Error codes](../guides/error-codes.md) · [Troubleshooting](../guides/troubleshooting.md)
- [Coverage map](COVERAGE.md) · Autodoc subset: [AUTODOC.md](AUTODOC.md)
