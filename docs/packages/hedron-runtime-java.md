# hedron-runtime-java

Tooling-grade Java evaluator for the Hedron portable conformance corpus.

**Maturity:** Beta (tooling-grade evaluator — not an application server)  
**Version:** `0.52.0` · **Runtime matrix:** JDK 11 / 17 / 21 (`--release 11` bytecode)  
**Coordinates:** `io.hedron:hedron-runtime-java:0.52.0`

Living Hedron train `0.52.x` (checkout tip `v0.52.0`; PyPI Python packages still pin
`>=0.51.0,<0.52` while deferred).

## Run

```bash
bash packages/hedron-runtime-java/scripts/run-conformance.sh
# or after mvn package:
java -jar target/hedron-runtime-java-0.52.0.jar path/to/portable_v1.json
```

## Non-goals

- Full Hedron port
- Application production server
