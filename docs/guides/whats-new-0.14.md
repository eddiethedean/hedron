# What's new in Hedron 0.14

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and published 1.0 status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

Phase **0.14** ships portable runtimes and acceleration under **D-048**.

## Highlights

- **`hedron-conformance`** — versioned language-neutral fixtures, normalization rules, and a
  capability-level runner (`hedron-conformance run` / `hedron conformance`).
- **Experimental Java and Node runtimes** — pass the published kit; not FastAPI ports.
- **Optional `hedron-native`** — Rust-accelerated HTML escaping with automatic pure-Python
  fallback; absence never changes semantics (`hedron accel-status`).
- **HDJ instrumentation** — exact loop/macro budgets, contracted extension evidence,
  `hdj.scoped_style` / `hdj.validate_attr`, broader static a11y checks, and portable
  SARIF-shaped checker fixtures (`HDJ-DEF-014`).

## Install

```bash
pip install "hedron>=0.14.0"
pip install "hedron[conformance]" "hedron[native]"  # optional
```

See [Upgrade](upgrade.md) and [conformance kit](../conformance/INDEX.md).
