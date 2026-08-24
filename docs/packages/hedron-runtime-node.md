# hedron-runtime-node

Tooling-grade Node.js evaluator for the Hedron portable conformance corpus.

**Maturity:** Beta (tooling-grade evaluator — not an application server)  
**Version:** `0.53.0` · **Runtime matrix:** Node.js 18 / 20 / 22 LTS  
**Install:** `npm install -g hedron-runtime-node` (published from the Hedron release workflow)

Living Hedron train `0.62.x` (in-tree tip and PyPI release `v0.62.0`; PyPI Python packages pin
`>=0.62.0,<0.63` ).

## Run

```bash
hedron-runtime-node
# or
HEDRON_CONFORMANCE_FIXTURES=/path/to/portable_v1.json node bin/run-conformance.mjs
```

Offline execution uses the packaged `fixtures/portable_v1.json` copy of the
immutable Python reference corpus.

## Non-goals

- Full Hedron port
- Application production server
