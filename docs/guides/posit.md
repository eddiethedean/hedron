# Posit deployments (`hedron-posit`)

Run the same Hedron application locally, in Posit Workbench, and on Posit Connect
with one facade.

New to application development or Workbench? Start with
[Your first application in Posit Workbench](../getting-started/first-app-posit-workbench.md). It
installs `hedron-posit`, constructs `HedronPosit`, and uses the Workbench-aware launcher before
returning here for the deployment contract.

**Requires:** `hedron-posit>=0.43.0,<0.44` (or `hedron[posit]>=0.43.0,<0.44`).
Compatibility package: `hedron-workbench>=0.43.0,<0.44` (or `hedron[workbench]`).
Generic Workbench ASGI behavior remains in `fastapi-workbench>=1.0.0,<2.0`.

## Preferred facade

```python
from hedron import Page, Text
from hedron_posit import (
    ConnectConfig,
    ConnectCookieMode,
    HedronPosit,
    PositConfig,
    PositProduct,
)

app = HedronPosit(
    title="My app",
    security="standard",
    explorer="off",
    session_secret="replace-me",
    posit=PositConfig(
        product=PositProduct.AUTO,
        connect=ConnectConfig(cookie_mode=ConnectCookieMode.NATIVE),
    ),
)

@app.page("/")
def home() -> Page:
    return Page(Text("Hello"), title="Home")
```

`product=auto` resolves from protected Connect markers (`POSIT_PRODUCT=CONNECT`),
existing Workbench evidence (`RS_SERVER_URL` / launcher handoff), or inactive
(ordinary Hedron). Conflicting evidence fails closed (`HED-POSIT-01xx`).

## Local

```bash
uvicorn app:app --reload
# or
hedron-posit run app:app
hedron-posit check --format json
hedron-posit doctor
```

With no Posit evidence the app matches ordinary `Hedron` routing and cookies.

## Workbench

```bash
hedron run app:app
hedron-posit run app:app
hedron-workbench run app:app   # compatibility CLI
```

Workbench mode delegates discovery and path normalization to `fastapi-workbench`
through `hedron-posit`. Session URLs remain ephemeral — use
`external_base_url` or Connect for durable email/OAuth callbacks.

Supported Workbench floor is **2025.05.1** (linux/amd64). Current verified lane is
Workbench **2026.07.0**. Live evidence: `docs/acceptance/realwb-030-202505/RESULT.log`
and `docs/acceptance/realwb-030/RESULT.log`.

See also [Posit Workbench](posit-workbench.md) for the compatibility
`HedronWorkbench` surface (supported through at least 0.35; no 0.33 deprecation
warning).

## Native Connect

Supported floor for on-host GUID content is Connect **2025.06.0** (protocol floor
2024.11.0). Current verified lane is Connect **2026.07.0**. Native mode requires:

- protected Connect runtime evidence (`POSIT_PRODUCT=CONNECT`);
- exactly one `RStudio-Connect-App-Base-URL` whose path matches ASGI `root_path`;
- request cookies passed through unchanged (`ConnectCookieMode.native`);
- owned response-cookie Path repair exactly once.

Install `hedron-posit` into the content environment (pip extra or wheel). Connect
**2025.06.0** FastAPI workers import `pkg_resources.parse_version` before user
code; setuptools 82+ removed that module. `hedron-posit` ships a tiny shim so
workers start. Copying source trees without installing the package is not enough
on 2025.06.

Off-host Connect and live vanity-URL expansion remain **Experimental**.

Reference app: `examples/connect-reference/`.

## Bridge extension point (not Supported in 0.33)

`ConnectCookieMode.authenticated_header_v1` is retained only as a documented
extension-point enum. Selecting it fails startup with `HED-POSIT-0401`. Stage 0
evidence recorded `BRIDGE_DECISION=drop_supported` (native cookies OK on
2025.06.0 and 2026.07.0). Do not enable a Supported bridge until a future Accepted decision
reproduces native request-cookie loss on a named topology.

## Migration from `hedron-workbench`

```python
# Before (still supported)
from hedron_workbench import HedronWorkbench
app = HedronWorkbench(...)

# Preferred
from hedron_posit import HedronPosit
app = HedronPosit(...)
```

`HedronWorkbench` is a thin subclass of `HedronPosit`. Existing
`workbench_*` constructor keywords, imports, CLI, and `hedron[workbench]` remain
supported.

## Operations and diagnostics

- `app.posit_status()` — typed product / cookie / bridge / capability record
- `app.workbench_status()` — redacted Workbench deployment record
- CLI `check` / `doctor` emit `posit_status` fields in text and JSON
- Secrets, cookies, GUID-shaped paths, and credential headers are redacted

## Security notes

- Connect credentials / user-session headers are never Hedron authentication.
- Product resolution never auto-enables bridge or peer trust.
- See [threat model](threat-model.md) and [RELEASE_0_33](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_33.md).
