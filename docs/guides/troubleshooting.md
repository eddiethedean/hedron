# Troubleshooting

## Wrong or unexpected version

**Symptom:** Features in the docs are missing from your install.

**Fix:** Check `python -c "import hedron; print(hedron.__version__)"`. Upgrade with
`pip install -U hedron` (or `uv add hedron@latest`). The current **published** train on
PyPI is **0.6.0**. See [STATUS](../STATUS.md).

## CSRF 403 on POST

**Cause:** Missing or mismatched CSRF token/cookie.

**Fix:** Perform a safe GET first to receive `hedron_csrf`, then send `X-CSRF-Token`
(or form field `csrf_token`) with the same value. On HTTPS, ensure the client stores
`Secure` cookies. See [Security](security.md).

## Explorer 404 or missing in production

**Cause:** `explorer="off"`, missing `hedron[dev]`, or production forced development mode off.

**Fix:** Install `hedron[dev]` for local Explorer; use `explorer="development"` only
locally; use `secured` with auth in rare cases; keep production off.

## Production startup: missing manifest (`HED-BUILD-0003`)

**Cause:** `HEDRON_ENV=production` / `production=True` without `hedron build` output.

**Fix:** Run `hedron build` and set `HEDRON_BUILD_DIR` if the manifest is not at
`.hedron/build/manifest.json`.

## Cannot import `Auto` / `DataTable` / chart helpers

**Cause:** Missing optional extra, not a planned feature gap.

**Fix:**

```bash
pip install "hedron[data]"      # Auto, DataTable, DataEditor
pip install "hedron[charts]"    # LineChart / adapters
pip install "hedron-charts[plotly]"   # example backend
```

See [Installation](../getting-started/installation.md) and
[charts and HTMX](charts-and-htmx.md).

## `NodeLike` import error from `hedron`

**Cause:** `NodeLike` lives in `hedron_core`.

**Fix:** `from hedron_core import NodeLike` (or avoid naming it and return built-ins).

## Still stuck?

Open a GitHub issue with Hedron version, command/traceback, and whether `HEDRON_ENV` is
set. Check [FAQ](faq.md) first.
