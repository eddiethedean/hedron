# Maturity and compatibility

Evaluator cheat-sheet for the three label axes. Builders can skip this page and use
[What’s ready today](../guides/whats-ready.md).

Builders usually need two answers:

1. **Can I use this capability for a pinned application today?**
2. **How much compatibility does its public API promise?**

The first answer is on [What’s ready today](../guides/whats-ready.md). The second is in
the [API stability catalog](../api/STABILITY.md).

| Capability readiness | Meaning | Application decision |
|---|---|---|
| **Supported** | Tested for the stated host and constraints | May be used in a pinned production application; not an SLA |
| **Experimental** | Shipped, but operational or compatibility evidence is incomplete | Evaluate explicitly and keep the documented fallback |
| **Deferred** | Designed or tracked, but not offered for adoption | Do not depend on it |

| API level | Compatibility promise |
|---|---|
| **`stable`** | Compatibility-protected throughout 1.x; an incompatible change requires a new major release plus migration guidance |
| **`beta`** | Public and supported where the capability table says so; may change at a documented minor-train boundary |
| **`experimental`** | May change or be removed at a minor boundary |
| **`internal` / `deferred`** | Not a public application contract |

Package classifiers provide additional context: `hedron-core`, `hedron`, `edron`, `hedron-data`,
`hedron-charts`, and `hedron-maps` are
**Stable** packages in 1.0, while satellites retain Beta or tooling-grade maturity. Always
pin package versions. Package maturity does not override the two application questions above.

## Example

Polling job status is a **Supported capability** with a documented public API. SSE and
WebSocket helpers are **Experimental**, so production applications should retain the
polling fallback. A particular callable may be API `stable` or `beta`; check its
reference page before treating its signature as compatibility-protected.

## Current release

The current published train is the **1.0.x** release (`v1.0.6`). PyPI serves Hedron and Edron
`1.0.6`. Install from PyPI:

```bash
python -m pip install "hedron>=1.0.0"
```

Pins: [Installation](installation.md).

There is no commercial SLA. See [Evaluate Hedron](../guides/evaluate.md)
for the adoption checklist and [Glossary](../GLOSSARY.md) for project terminology.
