"""#276: reconnecting Supported elements must not stack DOM listeners."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "packages/hedron-elements/src/hedron_elements/static/hedron-bridge.mjs"
DISCLOSURE = ROOT / "packages/hedron-elements/src/hedron_elements/static/hedron-disclosure.mjs"
ACTION = ROOT / "packages/hedron-elements/src/hedron_elements/static/hedron-action-async.mjs"


def test_track_aborts_previous_signal_on_reconnect() -> None:
    script = f"""
      import {{ track }} from {BRIDGE.as_uri()!r};
      const el = {{}};
      const first = track(el);
      let aborted = false;
      first.addEventListener("abort", () => {{ aborted = true; }});
      const second = track(el);
      if (!aborted) process.exit(2);
      if (second.aborted) process.exit(3);
      if (first === second) process.exit(4);
    """
    subprocess.run(["node", "--input-type=module", "-e", script], check=True)


def test_disclosure_and_action_bind_with_abort_signal() -> None:
    assert "{ signal }" in DISCLOSURE.read_text(encoding="utf-8")
    assert "{ signal }" in ACTION.read_text(encoding="utf-8")
