---
type: quickstart
title: Hedron agent quickstart
description: A short routing map for locating Hedron behavior and choosing the smallest local verification command.
tags: [quickstart, agents, navigation, local-development]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T19:14:00.347Z
sources:
  - id: openwiki-source-0f2091252a9c3383cef44ad0
    resource: repo://.agents/skills/openwiki/SKILL.md
  - id: openwiki-source-ab585d88aca3958f2aa6a541
    resource: repo://.codex/config.toml
  - id: openwiki-source-000a7add03cfbd0ac1794f3a
    resource: repo://docs/CONTRIBUTING.md
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-db8a384d21376a4f9d3a47a1
    resource: repo://release/stable-api.toml
  - id: openwiki-source-580fd261b203af5ed03d4d0d
    resource: repo://release/support-matrix.toml
  - id: openwiki-source-2faef51cd0bcbe4bb5eaae2d
    resource: repo://scripts/ci_checks.sh
  - id: openwiki-source-4c56c4085c56a3ab75df5178
    resource: repo://scripts/README.md
generated: { by: "codex", at: "2026-09-19T16:47:17.741Z" }
---

# Hedron agent quickstart

Start with the root [README](https://github.com/eddiethedean/hedron/blob/main/README.md) for the public model, package map, production boundaries, and user-facing documentation. Use [OpenWiki instructions](/openwiki/INSTRUCTIONS.md) for the agent-oriented scope of this wiki.

## Route a change to its owner

- Component props, node normalization, identity, HTML primitives, rendering contracts, and portable interaction values → [`packages/hedron-core/`](../packages/hedron-core/) and [rendering and component model](/openwiki/architecture/rendering-and-components.md).
- FastAPI application setup, pages, views, actions, routing, response conversion, sessions, and security middleware → [`packages/hedron/`](../packages/hedron/) and [requests and partial-page interactions](/openwiki/architecture/requests-and-interactions.md).
- CSRF, headers, escaping/trusted HTML, redirects, HTMX target authorization, or opt-in capabilities → [security and request boundaries](/openwiki/security/request-boundaries.md).
- Application-owned runtime context, lifespan startup, registry sealing, or production build gates → [application and runtime lifecycle](/openwiki/runtime/application-lifecycle.md).
- Runtime service ownership, session state, durable jobs, polling, or cancellation → [runtime state and background jobs](/openwiki/runtime/jobs-and-state.md).
- Data queries, tables, editors, transform plans, or optimistic edits → [data sources and editing](/openwiki/data/data-sources-and-editing.md).
- Charts, maps, browser elements, accessibility fallbacks, or packaged assets → [presentation, charts, maps, and assets](/openwiki/packages/presentation-and-assets.md).
- Flask, Django, Jinja, Workbench, Posit, or other host framework behavior → [adapters and host integrations](/openwiki/packages/adapters-and-hosts.md).
- MCP resources, tools, catalog exposure, or protocol security → [MCP and interoperability](/openwiki/integrations/mcp-and-interop.md).
- Other optional package families and feature bundles → [packages and extension surfaces](/openwiki/packages/extension-surfaces.md); check the support matrix before treating a satellite as stable.
- Public API, release metadata, tests, typing, lint, or docs checks → [quality, testing, and release contracts](/openwiki/operations/quality-and-release.md) and [test topology](/openwiki/operations/test-topology.md).

## Smallest local loop

The repository expects Python 3.10–3.14 and `uv`:

```bash
uv sync
uv run pytest tests/integration -q       # narrow FastAPI behavior
uv run ruff format --check packages tests examples
uv run ruff check packages tests examples
uv run basedpyright
```

Choose `tests/unit`, `tests/adapters`, `tests/security`, `tests/conformance`, or `examples` when those are the affected surfaces. For documentation-only work, use `uv sync --group docs` and `uv run --group docs mkdocs build --strict`; the full contributor guide lists the companion generated-content and ownership checks. Browser evidence is opt-in and uses `HEDRON_BROWSER=1` with `-n 0`.

For any source or documentation change that should be reflected in this wiki,
run the local OpenWiki freshness gate:

```bash
bash scripts/ci_checks.sh openwiki --python 3.12
```

The full local parity command starts with that gate:

```bash
bash scripts/ci_checks.sh all --python 3.12 --skip-browser
```

If the gate reports stale pages or Claims, update OpenWiki through the Codex
integration described in [OpenWiki and Local Documentation](/openwiki/operations/openwiki-and-local-documentation.md).
The integration is local-only; there is no OpenWiki GitHub Actions workflow.

Before a public-contract change, read the stable API and support metadata and follow the RFC/decision workflow. Keep changes local and focused, run the narrowest relevant checks first, and widen to the [shared quality suites](/openwiki/operations/quality-and-release.md) when package boundaries or release contracts are involved.
