# What's new in Hedron 0.35

**Published** as `v0.35.0`. Historical pin: `hedron>=0.35.0,<0.36`.
For new apps, use `hedron>=0.56.0,<0.59`; see [What’s new in 0.51](whats-new-0.51.md).

Phase 0.35 closes the 0.26+ package-graduation program with a whole-fleet audit: every
publishable distribution has an owned Supported (or tooling-grade Supported) scope or an
explicit terminal disposition. This is **not** Hedron `1.0`.

## Highlights

- **Fleet inventory** — `production-grade-inventory-035.toml` covers every `packages/*` plus
  published Node/Java runtimes with owner, maturity, disposition, and evidence pointers
- **Solver / compose honesty** — Supported extras, mixed-version satellite pins, reference-app
  isolation and combination smoke suites
- **Docs / supply reconcile** — whats-ready and tooling READMEs agree with inventory; license,
  SBOM, offline, and rollback notes under `fleet-supply-035/`
- **PRESENT-034** — default presentation gallery remains deferred/experimental; audited under
  `FLEET-035` + `DOCS-035` (no `PRESENT-035` gate)
- **Tooling maturity** — notebook, sample-kit, sim, and runtime evaluators labeled Beta
  tooling-grade for their declared 0.31 Supported roles

## Install

```bash
python -m pip install -U "hedron>=0.35.0,<0.36"
```

## See also

[RFC-0068](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0068-WHOLE-FLEET-CLOSURE.md) ·
[RELEASE_0_35](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_35.md) ·
[#91](https://github.com/eddiethedean/hedron/issues/91)
