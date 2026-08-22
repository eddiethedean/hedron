#!/usr/bin/env python3
"""Measure the phase 0.59 CSS and representative render budgets."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import statistics
import time
from pathlib import Path

from hedron_core import Stack, Text, compile_css, render

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "packages/hedron-core/src/hedron_core/static/hedron-default.css"
BASELINE = ROOT / "docs/acceptance/evidence-059/baseline-0581.json"


def timed_samples(function: object, count: int = 7) -> list[float]:
    samples: list[float] = []
    for _ in range(count):
        start = time.perf_counter()
        function()  # type: ignore[operator]
        samples.append((time.perf_counter() - start) * 1000)
    return samples


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = CSS.read_bytes()
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    source = ".root { color: red; } .title { animation: none 1s; }"
    tree = Stack(*[Text(f"item-{i}") for i in range(200)])
    compiler = timed_samples(lambda: compile_css(source, component_id="perf059"))
    renderer = timed_samples(lambda: render(tree))
    result = {
        "schema": "hedron.css-performance/1",
        "stylesheet_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_bytes": len(raw),
        "gzip_9_bytes": len(gzip.compress(raw, compresslevel=9, mtime=0)),
        "required_styling_javascript_bytes": 0,
        "additional_required_stylesheet_requests": 0,
        "compiler_cold_ms_median": round(statistics.median(compiler), 3),
        "representative_render_ms_median": round(statistics.median(renderer), 3),
        "baseline": {
            "raw_bytes": baseline["raw_bytes"],
            "gzip_9_bytes": baseline["gzip_9_bytes"],
            "compiler_cold_ms": baseline["compiler_cold_ms"],
            "representative_render_ms": baseline["representative_render_ms"],
        },
    }
    result["budgets"] = {
        "raw_bytes_pass": result["raw_bytes"] <= 90000,
        "gzip_9_bytes_pass": result["gzip_9_bytes"] <= 13000,
        "compiler_ratio_pass": result["compiler_cold_ms_median"]
        <= baseline["compiler_cold_ms"] * 1.25,
        "render_ratio_pass": result["representative_render_ms_median"]
        <= baseline["representative_render_ms"] * 1.10,
    }
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if all(result["budgets"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
