# hedron-runtime-java

Tooling-grade Java evaluator for the Hedron portable conformance corpus.

**Maturity:** Beta (tooling-grade evaluator — not an application server)  
**Version:** `0.32.0` · **Runtime matrix:** JDK 11 / 17 / 21 (`--release 11` bytecode)  
**Coordinates:** `io.hedron:hedron-runtime-java:0.32.0`

## Run

```bash
bash packages/hedron-runtime-java/scripts/run-conformance.sh
# or after mvn package:
java -jar target/hedron-runtime-java-0.32.0.jar path/to/portable_v1.json
```

## Non-goals

- Full Hedron port
- Application production server
