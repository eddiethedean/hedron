# How to read Hedron docs

Hedron uses a few maturity words. For day-to-day reading you only need three:

| Label | What it means for you |
|---|---|
| **Beta** (package) | The distribution is usable; **pin versions** in production. Alpha packages (`hedron-charts`, `hedron-sample-kit`) change faster. |
| **Supported** (feature) | Hedron claims this capability works on that host today. |
| **Deferred** (feature) | Documented and owned, but **not** ready—do not market or depend on it as Supported. |

API compatibility levels (`stable` / `beta` / `experimental` / `internal` / `deferred`) live in
the [STABILITY](../api/STABILITY.md) catalog for callable surfaces. RFC **Accepted** means the
design is selected—not that every detail is implemented. Prefer [What’s ready today](../guides/whats-ready.md)
when evaluating production use.

## Phases and versions

Capability phases are numbered `0.N`. The initial release for that phase is **`v0.N.0`**.
Phase **0.10** therefore maps to package train **`0.10.0`**, not a patch of 0.1.

There is no scheduled `1.0`. Patch releases stay inside their owning phase.

## HDJ vs HDN

- **HDN** was removed in **0.9**. There is no compatibility mode or converter. Stay on **0.8** if you still need HDN.
- **HDJ** (Hedron Jinja, `.hdj`) is the optional template format via `hedron[jinja]` / `hedron-jinja`.

## What to read first

1. [Installation](installation.md) → [Quickstart](quickstart.md)
2. [HTMX interactions](../guides/htmx-interactions.md) → [Minimal form POST](../guides/minimal-form.md)
3. [What’s ready today](../guides/whats-ready.md) when evaluating production use
4. Specs, RFCs, and acceptance evidence under the **Maintainers** tab when you need design authority

Stuck on a term? See the [Glossary](../GLOSSARY.md).
