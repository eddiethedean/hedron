#!/usr/bin/env node
/**
 * Run published hedron-conformance fixtures with the Node experimental runtime.
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { runFixtures } from "../lib/runtime.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const fixturePath = join(
  __dirname,
  "..",
  "..",
  "hedron-conformance",
  "src",
  "hedron_conformance",
  "fixtures",
  "portable_v1.json",
);

const fixtures = JSON.parse(readFileSync(fixturePath, "utf8"));
const results = runFixtures(fixtures);
let failed = 0;
for (const r of results) {
  const status = r.passed ? "PASS" : "FAIL";
  console.log(`${status}\t${r.fixture_id}\t${r.capability}\t${r.contract_version}`);
  if (!r.passed) {
    failed += 1;
    console.log(`  ${r.detail}`);
  }
}
console.log(`${results.length - failed}/${results.length} fixtures passed`);
process.exit(failed === 0 ? 0 : 1);
