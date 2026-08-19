# What's new in 0.51

Published **0.51.0** on PyPI. Pin `hedron>=0.51.0,<0.52`. Tracking
[#507](https://github.com/eddiethedean/hedron/issues/507).

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
