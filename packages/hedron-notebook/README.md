# hedron-notebook

Experimental Alpha server-side notebook preview helper for Hedron (RFC-0042).
Runs a normal Hedron ASGI app from an authoring notebook with inline iframe and
external-link modes. Distinct from the 0.16 browser-Python / JupyterLite sandbox.

```bash
pip install hedron-notebook
```

Default guidance is localhost-only development. Hosted or publicly reachable
hosts raise an explicit warning. This package is **not** a Supported production
server.
