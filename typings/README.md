# Local type stubs

Install a maintained third-party stub package when one exists for an untyped dependency. When
none exists, add a narrow `.pyi` file here for the public symbols Hedron uses. Keep the stub faithful
to the dependency's public API and use concrete types or protocols; stubs must not introduce `Any`.

`flask_login` currently has no bundled typing metadata in the supported dependency range. The local
stub covers only the request-local `current_user` API used by the optional Flask adapter.

`flask.globals` narrows the extension registry used by the Flask adapter to an object-valued mapping.

`fastapi.testclient` uses a narrow local stub for the request and response methods used by Hedron's
optional adapter. Keep third-party stubs limited to the public surface the workspace consumes.

`fastapi.openapi.utils.get_openapi` returns a JSON-shaped object mapping in the local partial stub;
callers still narrow each decoded schema value before mutation. `starlette.types` uses object-valued
ASGI scope and message mappings so adapters must validate request-controlled fields explicitly.

`json.loads` is typed locally to return `object`, so JSON input must be validated before use.

`graphviz` and `networkx` stubs cover only the source rendering and graph iteration surfaces used by
the optional chart adapters. They keep optional packages out of the required dependency set while
preserving typed boundaries when those adapters are enabled.

`axe_playwright_python.sync_playwright` has a narrow stub for its scan result; Playwright's own
typed sync API is imported directly so its maintained package declarations remain authoritative.

`tomllib` and `tomli` declare recursive TOML values as `object` for callers that consume decoded
configuration. Keep TOML values narrowed before field-specific use.
