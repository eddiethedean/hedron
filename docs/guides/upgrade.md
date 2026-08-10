# Upgrade to Hedron 0.26

This guide covers an application upgrade from **0.25.2** to the published **0.26.x**
train. New applications should use [Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.26.0 is primarily a reliability and release-evidence milestone for the
Supported CRUD/admin surface. It does not list removals from the compatibility-protected
facade. It adds machine-checked capability inventory, 0.25.2 upgrade fixtures, secured
Explorer validation, and multi-worker deployment evidence.

Polling remains the production recommendation for live status. SSE, WebSocket,
streaming, and navigation preload remain experimental.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm the application is on `hedron==0.25.2` or record its exact older version.
3. Run unit, adapter, and browser tests on the old environment.
4. Search for imports from `hedron.experimental` and application reliance on Explorer.
5. Record the current `python -m hedron --app app:app check` output.

## Upgrade

=== "pip"

    ```bash
    python -m pip install -U "hedron>=0.26.0,<0.27"
    python -m hedron --app app:app check
    ```

=== "uv"

    ```bash
    uv add "hedron>=0.26.0,<0.27"
    uv sync
    uv run hedron --app app:app check
    ```

Keep coordinated adapters and extras on the same train:

```bash
python -m pip install -U \
  "hedron>=0.26.0,<0.27" \
  "hedron-flask>=0.26.0,<0.27" \
  "hedron-django>=0.26.0,<0.27"
```

Install only the hosts you use. Charts and the sample kit retain independent satellite
floors: `hedron-charts>=0.1.6,<0.2` and `hedron-sample-kit>=0.1.6,<0.2`.

## Required application changes

No Supported CRUD/admin API removal is listed for 0.26.0. Applications using only the
[stable facade](../api/STABLE_FACADE.md) should normally require a dependency and
lockfile update, followed by verification.

Review these boundaries even when code changes are unnecessary:

- **Explorer:** development mode is refused in production; secured mode must have real
  authentication dependencies.
- **Live transports:** do not promote experimental SSE/WebSocket helpers based on the
  0.26 release. Keep a polling fallback.
- **Charts:** exclude satellite versions older than 0.1.6.
- **Production startup:** run `hedron build` before enabling production mode.
- **Multi-worker jobs:** use a shared status/backend store; in-memory state is local
  development only.

## Validate

```bash
python -c "import hedron; print(hedron.__version__)"
python -m hedron --app app:app check
pytest
```

Then verify the user flows that cross Hedron’s trust boundaries:

- a full-page GET and an HTMX fragment GET;
- a CSRF-protected POST;
- login, logout, and an authorization failure;
- reverse-proxy mount paths and static assets;
- background-job polling from more than one worker, if used;
- Explorer remaining unavailable in production.

Expected version output is `0.26.0` or a later `0.26.x` patch.

## Roll back

Restore the previous lockfile, or temporarily reinstall the exact old release:

```bash
python -m pip install "hedron==0.25.2"
```

Do not leave an open-ended `>=0.25` constraint in production. After rollback, repeat the
same smoke tests and retain the failure that triggered rollback for an issue report.

## Upgrading from 0.24 or earlier

Use the release narratives in order because several trains changed security and
authoring contracts:

1. [0.22: CSRF composition](whats-new-0.22.md)
2. [0.23: stable CRUD/admin facade](whats-new-0.23.md)
3. [0.24: polling-only production disposition](whats-new-0.24.md)
4. [0.25: production archetype and extras quarantine](whats-new-0.25.md)
5. Apply the 0.25.2→0.26 steps on this page.

Pre-0.9 applications must also replace removed HDN templates with HDJ or typed Python
components. There is no automatic HDN converter.

## See also

- [What’s new in 0.26](whats-new-0.26.md)
- [Release notes](release-notes.md)
- [Compatibility](../COMPATIBILITY.md)
- [What’s ready](whats-ready.md)
- [Troubleshooting](troubleshooting.md)
