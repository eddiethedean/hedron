# Troubleshooting

## Install / version mismatches

**Symptom:** Docs mention CLI or `hedron.testing`, but commands/imports fail.

**Fix:** Check `python -c "import hedron; print(hedron.__version__)"`. If you see
`0.3.0`, you are on PyPI. Either stay on the quickstart path or install **0.4** from
`main` — [installation](../getting-started/installation.md).

## `hedron new` then `uv lock` fails with unsatisfiable `hedron>=0.4.0`

**Cause:** Scaffold targets 0.4 while PyPI only has 0.3.

**Fix:** Install Hedron from git/`main` into the project, or wait for the PyPI publish.

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

**Cause:** Those APIs are planned, not shipped.

**Fix:** Use shipped built-ins and FastAPI endpoints. See
[Planned contracts](../api/README.md#planned-contracts).

## `NodeLike` import error from `hedron`

**Cause:** `NodeLike` lives in `hedron_core`.

**Fix:** `from hedron_core import NodeLike` (or avoid naming it and return built-ins).

## Duplicate component registration after `run_build` + app start

**Cause:** Historical issue when builds left plugins registered in-process.

**Fix:** Current 0.4 builds restore the registry after compilation. Upgrade to current
`main` if you still see duplicates.

## Still stuck?

Open a GitHub issue with Hedron version, install source (PyPI vs git), command/traceback,
and whether `HEDRON_ENV` is set. Check [FAQ](faq.md) first.
