# hedron-runtime-java

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)
[![JDK](https://img.shields.io/badge/JDK-11%2B-brightgreen.svg)](https://openjdk.org/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)

Experimental Java Hedron conformance runtime.

Minimal evaluator for the published [`hedron-conformance`](https://pypi.org/project/hedron-conformance/)
fixtures. Compiles a single Java source with `javac --release 11` and runs the
bundled portable fixture. Lives outside the uv Python workspace and is **not**
published to Maven Central.

**Maturity:** Experimental / Alpha

## Requirements

- JDK **11+** (`javac` and `java` on `PATH`)
- Bundled fixtures from `hedron-conformance` (checked into this monorepo under
  `packages/hedron-conformance/`)

## Run

From the repository root:

```bash
bash packages/hedron-runtime-java/scripts/run-conformance.sh
```

The script:

1. Compiles `src/main/java/io/hedron/runtime/ConformanceRuntime.java` with
   `--release 11`
2. Invokes `io.hedron.runtime.ConformanceRuntime` against
   `packages/hedron-conformance/src/hedron_conformance/fixtures/portable_v1.json`

Failures print fixture id, contract version, and violated capability.

## What this is / is not

| Is | Is not |
|---|---|
| Conformance fixture evaluator | Application server |
| Portable IR parity check | Full Hedron component runtime |
| Monorepo-only experimental package | Published Maven artifact |

## Links

- [`hedron-conformance`](https://pypi.org/project/hedron-conformance/)
- [Conformance docs](https://hedron.readthedocs.io/en/latest/conformance/INDEX/)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-runtime-java)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- Sibling: [`hedron-runtime-node`](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-runtime-node)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
