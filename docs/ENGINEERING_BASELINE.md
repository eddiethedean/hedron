# Engineering baseline

**Status:** Living contributor baseline (CI/toolchain contract for the published **0.56.x**
train; tip `v0.57.0`, PyPI `0.56.0` while 0.57.0 upload is deferred). Detailed acceptance
evidence maps live on GitHub under
[`docs/acceptance/`](https://github.com/eddiethedean/hedron/tree/main/docs/acceptance).

## Toolchain

- `uv` manages the development workspace, lockfile, environments, and release test installs.
- Hatchling builds wheels and source distributions.
- Ruff provides formatting and linting.
- Pyright runs strict type checking on public packages; documented narrow exceptions require justification.
- pytest, pytest-xdist, httpx, and optional Playwright browser tooling implement the test layers.
- Relative documentation links and `mkdocs build --strict` run in CI.
- Root `STATUS.md` must match `docs/STATUS.md` (`scripts/sync_status_roadmap.py --check`). The roadmap is only `docs/ROADMAP.md`.
- A Rust toolchain is required in CI for `test` and non-docs `quality` (and for local
  `quality` / native wheel smoke) because `hedron-native` builds via maturin. **Docs-only**
  PRs skip the Rust toolchain and `uv build --all-packages`.

These are contributor tools, not runtime dependencies. Application users may install Hedron with any standards-compliant Python package installer.

## CI gates (actual jobs)

Pull requests run `quality` unless classified **docs-only**, in which case the same job
runs the `docs` suite (no Rust, no wheels). `test`, `browser`, and `evidence` run unless
the PR is classified **docs-only** by the allowlist in `.github/workflows/ci.yml` (see
[Contributing → CI path filters](CONTRIBUTING.md#ci-path-filters)).

| Job | Coverage |
|---|---|
| `quality` | ruff format + check, pyright, tip+2 `verify_pkg_*` (older packets on evidence), satellite import + symbol-tier gates, wheel build + clean-install smoke, STATUS/ROADMAP mirror check, docs train SSOT / recipe / sim checks, relative markdown link check, `mkdocs build --strict` |
| `quality` (docs-only) | `docs` suite: train SSOT / recipe / sim checks, relative links, `mkdocs build --strict` — **no** Rust toolchain, **no** `uv build --all-packages` |
| `test` | `pytest` with pytest-xdist (`-n auto`) on Ubuntu for Python **3.11, 3.12, 3.13, 3.14** (skipped when docs-only) |
| `browser` | Playwright HTMX suite — **Chromium on PRs**; Chromium + Firefox + WebKit on `main` / workflow_dispatch (skipped when docs-only) |
| `evidence` | Supply-chain evidence bundle scripts (skipped when docs-only) |

Beginning with phase 0.6, CI green is necessary but not sufficient for a **release** claim.
Stable evidence IDs map requirements to commands and owners under
[acceptance/EVIDENCE.md](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EVIDENCE.md).
Release cuts also run gate TOML checks via `scripts/check_release_gate.py`.

macOS and Windows are not part of the default GitHub Actions matrix; Linux is normative for
CI. Free-threaded CPython and PyPy are informational until separately promoted.

## Quality policy

- Warnings are not ignored globally; every suppression is scoped and explained.
- Public functions, classes, protocols, decorators, and configuration have typing and documentation.
- Generated artifacts are deterministic or declare their intentional variability.
- Tests do not depend on network access except separately labeled upstream compatibility jobs.
- Security, accessibility, and compatibility regressions block release.
- A framework capability is advertised only when its native framework/server evidence is retained;
  portable conformance cannot manufacture ASGI, WSGI, or framework-specific guarantees.

## Typing policy

Pyright runs in `strict` mode on publishable package `src` trees. Shared aliases live in
`hedron_core.typing_aliases` and are re-exported from `hedron_core` when they appear in
public signatures (`JsonValue`, `HtmlAttrValue`, HTMX/job/plugin TypedDicts, and related
shapes).

- Prefer `JsonValue` / `JsonObject` / TypedDict / Protocol over `Any` for structured data.
- Prefer `HtmlAttrValue` / `HtmlAttrMap` for HTML and HTMX attribute maps end-to-end.
- Use `object` for truly unknown values that are immediately narrowed (for example `Auto`
  inspection and job `result` payloads).
- Keep `Any` only for host-framework passthrough (`**fastapi_kwargs`, Flask route
  `options`) and intentionally dynamic cores (plugin entry callables, open decorator
  wrappers). Remaining sites should be obviously boundary-shaped, not lazy bags.
- Every `# type: ignore[...]` is coded and justified at the call site.
- `reportUnknown*` stays at warning severity until a package subtree is driven near-zero;
  do not promote those reports to errors without a measured ratchet.

## Licensing policy

Hedron uses the MIT License (D-033). The repository root and each publishable distribution include `LICENSE`, and package metadata declares `license = "MIT"`. The release workflow refuses to publish when those artifacts are missing.
