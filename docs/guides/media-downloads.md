# Media downloads and players

Authorized file delivery for `Audio`, `Video`, `PdfViewer`, and gallery download-all
([RFC-0034](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0034-MEDIA-DOWNLOAD-RANGE.md)).

## FastAPI (Supported)

```python
from pathlib import Path
from hedron import media_file_response, download_all_zip, Audio, SafeUrl, UrlPurpose

MEDIA = Path("/var/media")

@app.get("/media/{name}")
def media(name: str, request: Request, user=Depends(require_user)):
    return media_file_response(
        MEDIA / name,
        root=MEDIA,
        filename=name,
        content_type="audio/mpeg",
        authorized=True,  # set from your authz check
        request_headers=request.headers,
        disposition="inline",
        max_size=50_000_000,
    )

Page(Audio(SafeUrl.parse("/media/clip.mp3", purpose=UrlPurpose.ASSET)))
```

- Authorization runs before any bytes leave the jail under `root`.
- Satisfiable `Range` → `206` + `Content-Range`; unsatisfiable → `416`.
- Authenticated responses use `Cache-Control: private, no-store`.
- `download_all_zip(..., max_total_bytes=...)` rejects oversize bundles.

## Flask / Django (composition)

Use the same authz → path-jail → size/disposition pattern on the host response type.
Parse `Range` with `parse_byte_range` (or mirror its single-range rules), then set
`Content-Range` / status yourself. Player markup (`Audio`, `Video`, `PdfViewer`, `Gallery`)
is portable via `hedron-core`; only the response helper is FastAPI/Starlette-shaped in 0.15.

Also see [Cookbook — file upload / download](cookbook.md) and `safe_download_response`.
