# File upload

CSRF-safe multipart upload with size and type checks in the action handler.

## Run (monorepo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/file-upload --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Upload a small `.txt` or `.csv`
(max 64 KiB in this demo).

## What it shows

- `FileUpload` control + `enctype="multipart/form-data"`
- Server-side `UploadFile` validation (type + size)
- CSRF hidden field on the form

Source: [`examples/file-upload`](https://github.com/eddiethedean/hedron/tree/main/examples/file-upload).
Related: [Cookbook — file upload](../guides/cookbook.md) ·
[Media downloads](../guides/media-downloads.md).
