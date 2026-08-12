# Workbench reference

Ordinary Hedron app with a page, HTMX fragment, and CSRF-ready cookies.
**No `hedron_workbench` imports.**

`app_facade.py` provides the recommended one-class variant using
`HedronWorkbench`; it behaves like `Hedron` locally and consumes launcher state
on Workbench.

## Local

```bash
uv run uvicorn examples.workbench-reference.app:app --app-dir .
uv run uvicorn app_facade:app --app-dir examples/workbench-reference --reload
```

## Workbench

```bash
hedron-workbench run app_facade:app
# or from this directory after installing the extra:
hedron-workbench run app:app
```

## Docker smoke (REALWB-030)

Requires `PWB_LICENSE` in repo-root `.env` (Posit license key). Never commit it.
REALWB stops Workbench with a 120s grace period and runs
`rstudio-server license-manager deactivate` before teardown so license-key activations
are released for the next local or CI run.
The live matrix probes the pinned Workbench image and real `rserver-url`, then runs
**two package passes**:

1. **hedron-workbench** — `app_facade.py` via `hedron-workbench run` (HTMX, CSRF,
   Hedron assets, external invite URLs, WebSockets, inactive-facade parity).
2. **fastapi-workbench** — plain FastAPI `app.py` via `fastapi-workbench run`
   (mounted pages/forms, OpenAPI, redirects, encoded-target guards, diagnostics,
   WebSockets, outside-Workbench parity).

The image is pinned by digest, and `.env` is parsed as data rather than executed as shell code.

On an Apple Silicon host the official image runs as `linux/amd64`. The matrix
labels an `rserver-url` exit 139 as `emulation_limited`; run that helper-contract
probe on an amd64 host before release while retaining the remaining arm64 Docker
evidence.

```bash
bash ../../scripts/realwb_smoke.sh
# backward-compatible alias:
bash ../../scripts/realwb_029.sh
```

See also [`examples/fastapi-workbench-reference/`](../fastapi-workbench-reference/README.md).

