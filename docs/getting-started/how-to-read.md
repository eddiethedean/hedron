# How to read Hedron docs

You do **not** need maturity vocabulary to install or complete the golden path
(Installation → First app → HTMX → Minimal form). Use this page when evaluating
production use or reading API/stability catalogs.

## Maturity cheat-sheet (three axes)

**Package** maturity (Beta / Alpha on PyPI) ≠ **capability** readiness (Supported /
Experimental / Deferred) ≠ **API compatibility** level (`stable` / `beta` /
`experimental` / `internal` / `deferred` in [STABILITY](../api/STABILITY.md)).

A **Beta** package can expose **Supported** capabilities whose API level is still
`beta`. That is normal on the `0.x` train — pin package versions and read the capability
table on [What’s ready today](../guides/whats-ready.md) before shipping.

| Label | Axis | What it means for you |
|---|---|---|
| **Beta** / **Alpha** | Package (PyPI) | Usable distribution; **pin versions**. Alpha expects faster churn. |
| **Supported** | Capability | Works on that host today **with pins** — not a warranty or SLA. Most callable APIs remain compatibility level `beta` unless listed in the small **stable** table. |
| **Experimental** | Capability | Public API shipped; may change; prefer documented fallbacks (e.g. polling). |
| **Deferred** | Capability | Documented and owned, but **not** ready — do not depend on it as Supported. |
| **`stable` / `beta` / …** | API level | Compatibility promise for a callable surface in STABILITY — **Supported ≠ `stable`**. |

When writing docs, name the axis: “Beta **package**”, “Supported **capability**”,
“API level `beta`”. Do not collapse them into one vague “beta” adjective.

RFC **Accepted** means the design is selected—not that every detail is implemented.
Prefer [What’s ready today](../guides/whats-ready.md) and
[Evaluate Hedron](../guides/evaluate.md) when evaluating production use.

## Versions

Capability phases are numbered `0.N`. The living published train is **0.25**
(`v0.25.0`). Pin production installs with `hedron>=0.25.0,<0.26`.

There is no scheduled `1.0`. Patch releases stay inside their owning phase.

## Public docs vs maintainer corpus

| Audience | Where |
|---|---|
| Adopters | **Start**, **Guides**, **Examples**, **Reference** (Components + API), and **Project** (including **Evaluate**) — maturity snapshot: [What's ready today](../guides/whats-ready.md) |
| Maintainers / RFC authors | [Maintainer handbook](../guides/maintainer-handbook.md) + GitHub-only trees (`docs/rfcs/`, `docs/acceptance/`, `docs/STATUS.md`, `docs/RELEASE.md`, …) |

## Template history (upgrade only)

Optional Jinja/HDJ templates use `hedron[jinja]`. An earlier experimental template prototype
(**HDN**) was removed in **0.9**—see the [upgrade guide](../guides/upgrade.md) only if you
are migrating from 0.8.

## What to read first

1. [Build your first app](quickstart.md) → [HTMX interactions](../guides/htmx-interactions.md)
2. [Minimal form POST](../guides/minimal-form.md) → [Installation](installation.md) as needed
3. [What’s ready today](../guides/whats-ready.md) / [Evaluate Hedron](../guides/evaluate.md) when evaluating production use

Stuck on a term? See the [Glossary](../GLOSSARY.md).
