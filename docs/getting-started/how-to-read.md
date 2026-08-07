# How to read Hedron docs

You do **not** need maturity vocabulary to install or complete the golden path
(Install → First app → HTMX → Minimal form → Learning path). Use this page when evaluating
production use or reading API/stability catalogs.

## Maturity words (when you need them)

| Label | What it means for you |
|---|---|
| **Beta** (package) | The PyPI distribution is usable; **pin versions** in production. |
| **Alpha** (package) | On PyPI; pin and expect faster churn (`hedron-charts`, notebook, MCP, Gradio, …). |
| **Supported** (capability) | Hedron claims this capability works on that host today — ship with pins. |
| **Experimental** (capability) | Public API shipped; may change; prefer documented fallbacks (e.g. polling). |
| **Deferred** (capability) | Documented and owned, but **not** ready — do not market or depend on it as Supported. |

Do **not** combine labels. Prefer “Supported” or “Beta package” — never pair Supported
with a Beta tag in one phrase.
Package maturity (Beta / Alpha) and capability readiness (Supported / Experimental / Deferred)
are separate axes.

API compatibility levels (`stable` / `beta` / `experimental` / `internal` / `deferred`) live in
the [STABILITY](../api/STABILITY.md) catalog for callable surfaces. RFC **Accepted** means the
design is selected—not that every detail is implemented. Prefer
[What’s ready today](../guides/whats-ready.md) and [Evaluate Hedron](../guides/evaluate.md)
when evaluating production use.

## Versions

Capability phases are numbered `0.N`. The initial release for that phase is **`v0.N.0`**.
Phase **0.18** maps to packages **`0.18.x`** (current **`0.18.0`**), not a patch of 0.1.

There is no scheduled `1.0`. Patch releases stay inside their owning phase.

## Public docs vs maintainer corpus

| Audience | Where |
|---|---|
| Adopters | **Learn**, **Adopt**, **Build**, **Examples**, **Reference** (Components + API), and **Project** — maturity snapshot: [What's ready today](../guides/whats-ready.md) |
| Maintainers / RFC authors | [For maintainers](../guides/maintainers.md) + GitHub-only trees (`docs/rfcs/`, `docs/acceptance/`, `docs/STATUS.md`, `docs/RELEASE.md`, …) |

## Template history (upgrade only)

Optional Jinja/HDJ templates use `hedron[jinja]`. An earlier experimental template prototype
(**HDN**) was removed in **0.9**—see the [upgrade guide](../guides/upgrade.md) only if you
are migrating from 0.8.

## What to read first

1. [Installation](installation.md) → [Quickstart](quickstart.md)
2. [HTMX interactions](../guides/htmx-interactions.md) → [Minimal form POST](../guides/minimal-form.md)
3. [What’s ready today](../guides/whats-ready.md) / [Evaluate Hedron](../guides/evaluate.md) when evaluating production use

Stuck on a term? See the [Glossary](../GLOSSARY.md).
