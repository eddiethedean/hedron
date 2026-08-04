# How to read Hedron docs

Hedron uses a few maturity words that sound similar. This page is the decoder ring.

## Package maturity vs API stability vs capability claims

| Label | Where you see it | What it means for you |
|---|---|---|
| **Beta / Alpha** (package) | PyPI classifiers, README package table | How ready the *distribution* is. Beta packages are usable; pin versions. Alpha packages (`hedron-charts`, `hedron-sample-kit`) change faster. |
| **API stability** (`beta`, `experimental`, `internal`, `deferred`) | [STABILITY](../api/STABILITY.md) | Compatibility promises for a callable surface inside a package. |
| **Supported / Deferred** (capability) | Adapter docs, acceptance rows | Whether Hedron claims that *feature* works on that host today. Deferred is documented and must not be treated as Supported. |
| **Accepted** (RFC / contract) | API pages, RFCs | The design is selected. It does **not** by itself mean every detail is implemented—check “Shipped” and the roadmap phase. |
| **Shipped in 0.N** | API / guide banners | Implemented in the published train that maps to phase `0.N` (`v0.N.0`). |

## Phases and versions

Capability phases are numbered `0.N`. The initial release for that phase is **`v0.N.0`**.
Phase **0.10** therefore maps to package train **`0.10.0`**, not a patch of 0.1.

There is no scheduled `1.0`. Patch releases stay inside their owning phase.

## HDJ vs HDN

- **HDN** was removed in **0.9**. There is no compatibility mode or converter. Stay on **0.8** if you still need HDN.
- **HDJ** (Hedron Jinja, `.hdj`) is the optional template format via `hedron[jinja]` / `hedron-jinja`.

## What to read first

1. [Installation](installation.md) → [Quickstart](quickstart.md)
2. [Forms and actions](../guides/forms-and-actions.md) → [HTMX interactions](../guides/htmx-interactions.md)
3. [What’s ready today](../guides/whats-ready.md) when evaluating production use
4. Specs, RFCs, and acceptance evidence under **Specification** when you need design authority

Stuck on a term? See the [Glossary](../GLOSSARY.md).
