---
type: architecture
title: Monorepo architecture
description: Hedron is a uv-managed Python workspace whose framework-neutral core, FastAPI runtime, satellites, adapters, and tooling have separate package boundaries and maturity contracts.
tags: [architecture, monorepo, packages, stability]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T19:14:00.347Z
sources:
  - id: openwiki-source-561ff05cc03f3c3a61bdaf8c
    resource: repo://packages/hedron-core/pyproject.toml
  - id: openwiki-source-134ef4bb83b56ebdee05387f
    resource: repo://packages/hedron/pyproject.toml
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-580fd261b203af5ed03d4d0d
    resource: repo://release/support-matrix.toml
generated: { by: "codex", at: "2026-09-19T15:43:01.076Z" }
---

# Monorepo architecture

Hedron is organized as a Python monorepo rather than as one installable package. The root project is a non-package `uv` workspace, and its member list is the authoritative starting point for locating package source, tests, and package-local metadata. The root development dependency group includes the workspace packages plus the test, lint, typing, documentation, and browser tooling used to work on them. See the [quality and release contracts](/openwiki/operations/quality-and-release.md) for the verification path.

## Package layers

The dependency direction starts with `hedron-core`, the framework-neutral rendering core. Its package metadata describes it as the rendering core and limits its runtime dependencies to Pydantic, packaging, TOML compatibility on older Python versions, and typing extensions. The `hedron` package is the FastAPI-native application layer: it depends on `hedron-core` and adds FastAPI, Starlette, signed-cookie support, multipart parsing, and its own optional satellite integrations.

That boundary is useful when deciding where a change belongs:

- Put framework-neutral component, HTML, identity, rendering, and shared protocol behavior in `packages/hedron-core/`.
- Put FastAPI application, routing, request, response, security, state, and job behavior in `packages/hedron/`.
- Put data, charts, maps, host adapters, presentation integrations, and other optional capabilities in their own workspace packages instead of making the core runtime depend on them.

The repository README groups the broader workspace into runtime packages, data and presentation satellites, host and environment adapters, extension and interop packages, quality/tooling packages, and the alternate `edron` facade. The published support matrix is the source of truth for maturity: `hedron-core`, `hedron`, `edron`, `hedron-data`, `hedron-charts`, and `hedron-maps` are stable, while host adapters and most other satellites are beta or tooling-grade. A package's version line alone does not promote it into the stable platform.

## How to navigate a change

Start from the public behavior and follow the owning layer inward. A page or interaction change usually begins in `packages/hedron/`; a component contract or renderer change may need `packages/hedron-core/`; data or presentation behavior belongs in the relevant satellite. Check the support matrix before depending on a package across an independently versioned boundary, and use the existing [user-facing documentation](https://hedron.readthedocs.io/en/latest/) for detailed API and release guidance.

The most important cross-links are:

- [Rendering and component model](/openwiki/architecture/rendering-and-components.md) for the core-to-runtime render path.
- [Requests and partial-page interactions](/openwiki/architecture/requests-and-interactions.md) for the FastAPI route and browser interaction boundary.
- [Packages and extension surfaces](/openwiki/packages/extension-surfaces.md) for adapters and optional features.
