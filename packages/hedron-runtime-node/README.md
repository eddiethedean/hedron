# hedron-runtime-node

**Maturity:** Experimental / Alpha (phase 0.14)

Minimal Node.js runtime that evaluates the published `hedron-conformance`
fixtures. Not a FastAPI port — only the portable IR capabilities required by
the kit.

```bash
node packages/hedron-runtime-node/bin/run-conformance.mjs
```

Failures print fixture id, contract version, and capability.
