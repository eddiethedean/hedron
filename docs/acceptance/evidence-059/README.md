# Phase 0.59 entry evidence

These artifacts are the reproducible Stage 1 entry packet for the 0.59 modern-CSS
contract. They contain no secrets, absolute paths, or application data.

`gate-results-059.json` is the current 23-gate execution ledger. It records the distinction
between a passing implemented-scope check and a `Verified` release claim; the packet is not
release-ready while any gate remains `Implemented`.

- `baseline-0581.json` records the stylesheet baseline from commit `d399f25b`.
- `parser-recipe-059.json` records the in-tree parser corpus and explicit recipe probe.
- `capability-{chromium,firefox,webkit}-059.json` records the pinned Playwright capability
  results for Chromium `151.0.7922.34`/revision `1234`, Firefox `153.0`/revision `1538`,
  and WebKit `26.5`/revision `2336`.
- `performance-059.json` records the current stylesheet/compiler/render budget measurements.
- `package-059.json` records the built wheel/sdist inventory and package metadata checks.
- `consumer-059.json` records the Data Mover migration slice, dependency pins, removed legacy
  selectors, and focused UI/interaction/pipeline test result.
- `consumer-migration-059.patch` is the reviewable consumer diff used by that migration slice.

Regenerate the probe artifacts with:

```bash
python scripts/probe_css_059.py --output docs/acceptance/evidence-059/parser-recipe-059.json
for browser in chromium firefox webkit; do
  python scripts/probe_css_059.py --browser "$browser" \
    --output "docs/acceptance/evidence-059/capability-$browser-059.json"
done
```
