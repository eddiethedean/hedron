#!/usr/bin/env bash
# Run published hedron-conformance fixtures with the Java experimental runtime.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SRC="$ROOT/packages/hedron-runtime-java/src/main/java"
OUT="$ROOT/packages/hedron-runtime-java/build/classes"
FIXTURE="$ROOT/packages/hedron-conformance/src/hedron_conformance/fixtures/portable_v1.json"
mkdir -p "$OUT"
javac --release 11 -d "$OUT" "$SRC/io/hedron/runtime/ConformanceRuntime.java"
java -cp "$OUT" io.hedron.runtime.ConformanceRuntime "$FIXTURE"
