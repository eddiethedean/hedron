# hedron-runtime-node

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)
[![Node](https://img.shields.io/badge/node-%3E%3D18-brightgreen.svg)](https://nodejs.org/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)

Experimental Node.js Hedron conformance runtime.

Minimal evaluator for the published [`hedron-conformance`](https://pypi.org/project/hedron-conformance/)
fixtures. **Not** a FastAPI port — only the portable IR capabilities required by
the kit. Lives outside the uv Python workspace and is **not** published to npm.

**Maturity:** Experimental / Alpha · monorepo package version `0.14.0`

## Requirements

- Node.js **≥ 18**
- Bundled fixtures from `hedron-conformance` (checked into this monorepo under
  `packages/hedron-conformance/`)

## Run

From the repository root:

```bash
node packages/hedron-runtime-node/bin/run-conformance.mjs
```

Or via the local bin name after linking in this tree:

```bash
node ./packages/hedron-runtime-node/bin/run-conformance.mjs
```

Failures print fixture id, contract version, and violated capability.

## What this is / is not

| Is | Is not |
|---|---|
| Conformance fixture evaluator | Application server |
| Portable IR parity check | Full Hedron component runtime |
| Monorepo-only experimental package | Published npm distribution |

## Links

- [`hedron-conformance`](https://pypi.org/project/hedron-conformance/)
- [Conformance docs](https://hedron.readthedocs.io/en/latest/conformance/)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-runtime-node)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- Sibling: [`hedron-runtime-java`](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-runtime-java)

## License

MIT. See [LICENSE](LICENSE).
