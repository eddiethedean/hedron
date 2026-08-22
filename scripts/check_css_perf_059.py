#!/usr/bin/env python3
"""Executable phase 0.59 evidence entry point for PERF-059."""

import os

from _gate_059 import check_gate
from measure_css_059 import main as measure

code = check_gate("PERF-059")
if code:
    raise SystemExit(code)
if os.environ.get("HEDRON_GATE_VERIFY") == "1":
    raise SystemExit(measure())
