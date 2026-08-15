# What’s new in 0.30

!!! note "Current train is 0.41"

    Pin `hedron>=0.41.0,<0.42` for new apps. See [What’s new in 0.41](whats-new-0.41.md).

**Published** as `v0.30.0`. Historical pin: `hedron>=0.30.0,<0.31`.

Phase **0.30** (D-058 / RFC-0063) extracts generic Posit Workbench / RStudio Server
deployment into monorepo-owned **`fastapi-workbench` `1.0.0`**, and makes
`hedron-workbench` a thin Hedron specialization that depends on it.

## Highlights

- **`fastapi-workbench` 1.0.0:** plain FastAPI apps get `fastapi-workbench run module:app`
  without installing Hedron. Independent semver (`>=1.0.0,<2.0`).
- **`hedron-workbench` 0.30.0:** depends on `fastapi-workbench>=1.0.0,<2.0`; delegates
  generic resolver, path middleware, and launcher behavior; keeps Hedron-specific
  cookie/mount handoff and `HedronWorkbench`.
- **No auto-activation:** install, import, and `RS_SERVER_URL` never wrap apps or grant
  trust.
- **Non-goals:** Flask/Django/WSGI in `fastapi-workbench`, Connect publishing as Supported,
  expanding Supported live transports.

## Upgrade

From `0.29.x` (Hedron apps):

```bash
python -m pip install -U "hedron>=0.34.0,<0.35"
python -m pip install -U "hedron-workbench>=0.32.0,<0.33"
# Workbench sessions:
hedron-workbench run app:app
# Local remains:
uvicorn app:app
```

Plain FastAPI (no Hedron):

```bash
python -m pip install -U "fastapi-workbench>=1.0.0,<2.0"
fastapi-workbench run app:app
```

Details: [RELEASE_0_30](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_30.md) · [upgrade guide](upgrade.md) ·
[fastapi-workbench guide](fastapi-workbench.md).
