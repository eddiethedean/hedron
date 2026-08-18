"""#280: enhanceNavigation must not stack document listeners on re-call."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "packages/hedron-elements/src/hedron_elements/static/composition-041.mjs"


def test_enhance_navigation_is_idempotent() -> None:
    script = f"""
      import {{ enhanceNavigation }} from {MODULE.as_uri()!r};
      const calls = [];
      const root = {{ addEventListener(type) {{ calls.push(type); }} }};
      enhanceNavigation(root);
      enhanceNavigation(root);
      if (calls.length !== 2) process.exit(2);
      if (!calls.includes("click") || !calls.includes("htmx:afterSwap")) process.exit(3);
    """
    subprocess.run(["node", "--input-type=module", "-e", script], check=True)
