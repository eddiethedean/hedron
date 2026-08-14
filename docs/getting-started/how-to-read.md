# Maturity and compatibility

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
| **`stable`** | Compatibility-protected across 0.x trains; removal requires deprecation and migration guidance |
| **`beta`** | Public and supported where the capability table says so; may change at a documented minor-train boundary |
| **`experimental`** | May change or be removed at a minor boundary |
| **`internal` / `deferred`** | Not a public application contract |

Package classifiers provide additional context: the flagship and adapters are **Beta**;
the optional `hedron-elements` incubator is **Alpha**. Always pin package versions. Package maturity
does not override the two application questions above.

## Example

Polling job status is a **Supported capability** with a documented public API. SSE and
WebSocket helpers are **Experimental**, so production applications should retain the
polling fallback. A particular callable may be API `stable` or `beta`; check its
reference page before treating its signature as compatibility-protected.

## Current release

The current published train is **0.40.x** (last published `v0.40.0`). Use:

```bash
python -m pip install "hedron>=0.40.0,<0.41"
```

There is no commercial SLA or scheduled 1.0. See [Evaluate Hedron](../guides/evaluate.md)
for the adoption checklist and [Glossary](../GLOSSARY.md) for project terminology.
