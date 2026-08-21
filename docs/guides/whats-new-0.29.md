# What’s new in 0.29

!!! note "Current train is 0.58"

    Pin `hedron>=0.53.0,<0.54` for new apps (checkout tip; PyPI still `>=0.56.0,<0.59` while deferred). The pin below is historical for the 0.29 train only.
    See [What’s new in 0.51](whats-new-0.51.md).

**Published** as `v0.29.0`. Historical pin: `hedron>=0.29.0,<0.30`.

Phase **0.29** (D-057 / RFC-0062) ships production-grade
`hedron-workbench` — an optional Posit Workbench / RStudio Server deployment
adapter. Existing FastAPI Hedron apps run unchanged by switching the launch
command.

## Highlights

- **`HedronWorkbench`:** use one `Hedron` subclass locally and on Workbench;
  inactive instances preserve ordinary Hedron behavior and the launcher avoids
  double wrapping them.
- **`hedron-workbench run` / `check`:** pre-bind loopback, discover via
  `rserver-url`, export `HEDRON_ROOT_PATH` before import, wrap once, serve.
- **Cookie Path is construction-time:** set `HEDRON_ROOT_PATH` or
  `Hedron(root_path=...)` before `Hedron()`. `workbenchify` cannot repair cookies
  after construction. Uvicorn `--root-path` alone is not enough.
- **No auto-activation:** install, import, and `RS_SERVER_URL` never wrap apps
  or grant trust.
- **Fail-closed deployment inputs:** explicit mount/public URL validation,
  bounded discovery output, exact proxy allowlists, and opt-in external binds.
- **Hedron-neutral polish:** `Hedron(root_path=...)`, re-exported
  `resolve_mount_path_from_environ`, color-mode cookie scoped to the mount Path.
- **Non-goals:** Flask/Django/WSGI, vendoring fastapi-workbench, bundling
  `rserver-url`, Posit Connect as Supported, Workbench login as Hedron identity.

## Upgrade

From `0.28.x` (app source unchanged):

```bash
python -m pip install -U "hedron>=0.29.0,<0.30"
python -m pip install -U "hedron-workbench>=0.29.0,<0.30"
# Workbench sessions:
hedron-workbench run app:app
# Local remains:
uvicorn app:app
```

Uninstalling `hedron-workbench` restores the 0.28 launch command.

Details: [RELEASE_0_29](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_29.md) · [Posit Workbench](posit-workbench.md) ·
[upgrade guide](upgrade.md).
