# What's new in 0.51

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and published 1.0 status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

Published **0.51.0** on PyPI. For new apps, use the current compatibility floor `hedron>=1.0.0`.
In-tree tip is **0.51.2**. Tracking [#507](https://github.com/eddiethedean/hedron/issues/507).

## 0.51.2

Quality and typing patch on the 0.51 train. Install current applications from PyPI with
`hedron>=1.0.0`; the historical train remains documented below for maintainers.

- Replace runtime `assert` validation with explicit errors on chart adapters, Gradio client, hosts, and jobs.
- Typing ratchet on charts/maps/MCP/Jinja/Redis and host-integration modules (`handles`, pages, Explorer router).
- Fail-soft exception paths log at debug/warning; HDJ document-shape helpers extracted.

## 0.51.1

Bugfix patch on the 0.51 train. Install current applications with `hedron>=1.0.0`.

- Adaptive concurrency cancels in-flight siblings when any task returns `HED-CONC-0001` (#103).
- FastAPI fragment render honors `allow_htmx_eval` on `InteractionPolicy` (#74).
- Job SSE no longer re-emits an acknowledged non-terminal snapshot (#207).
- HTMX `select_oob` accepts comma-separated `#id` lists (#70); duplicate OOB element ids fail closed (#85).
- WebSocket channel rejects valid non-object JSON without crashing (#98).
- Connection registry single-flights concurrent first `get` (#106).
- Adapter URL reversal uses boundary-safe mount-prefix matching (#202).
- `SessionState` refreshes after direct session mutation and shares one cache across duplicate dependencies (#149, #150).
- Workbench resolver preserves an extra public-base prefix; `check`/`run` skip mount rediscovery when Uvicorn set `root_path` (#135, #186).
- TreeView rejects `javascript:` data sources; HTMX busy clears on send/response errors.
- Login CSRF, auth rate limiting, Flask CSRF for non-POST unsafe methods, Workbench cookie Path checks (#138, #139, #187, #160).
- Packaged asset paths cannot escape the static directory; simulator captions are HTML-escaped (#220, #204).

## 0.51.0

Curated extras depth (RFC-0078 / D-087 / D-088):

- `ExtrasFeature` is the `hedron-extras` inventory authority. It projects into
  `PluginContext.register_feature` and does not replace `FeatureBundle`.
- Shared light-DOM extras hosts reconnect after HTMX swaps, abort in-flight
  work, and clean up listeners and object URLs.
- JSON/Data/Chart workbenches are cancelable and revision-aware. JSON is never
  evaluated as code.
- TreeView/Typeahead have stable ids, abortable requests, and select/datalist
  fallbacks. Image crop/region/annotation intents use normalized coordinates
  and server-confirmed output.
- `BrowserPythonSandbox` stays Experimental. Default plugin registration is
  opt-in (`hedron_extras_sandbox` / `HEDRON_EXTRAS_SANDBOX=1`). Import remains
  `from hedron_extras.sandbox import BrowserPythonSandbox`.
- Experimental UI (`CodeEditor`, `TerminalView`, joystick, device) stays behind
  `hedron[experimental-ui]`.

Companion flagship authoring (#504–#506):

- Accessible password show/hide on `TextInput(type="password")`.
- Opt-in `SwapReveal` tied to HTMX after-swap, honoring `prefers-reduced-motion`.
- Generic HTMX busy via `BusyRegion` / `Hx(busy=...)` (`aria-busy` + indicator).
  Unmarked requests do not set `aria-busy` on `document.body`. Overlapping
  requests on one host keep `aria-busy` until the last one finishes. A simple
  `#id` `Hx.indicator` also drives the Hedron busy indicator.
