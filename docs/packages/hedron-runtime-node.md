# hedron-runtime-node

Tooling-grade Node.js evaluator for the Hedron portable conformance corpus.

**Maturity:** Beta (tooling-grade evaluator — not an application server)
**Version:** `0.66.2` · **Runtime matrix:** Node.js 18 / 20 / 22 LTS
**Install:** `npm install -g hedron-runtime-node` (published from the Hedron release workflow)

The evaluator consumes the portable conformance corpus retained by the 1.0 repository train.

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
