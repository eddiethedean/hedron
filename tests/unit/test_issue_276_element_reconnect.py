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


def test_disclosure_and_action_reconnect_without_duplicate_listeners() -> None:
    script = f"""
      const registry = new Map();
      class FakeElement extends EventTarget {{
        constructor() {{
          super();
          this.details = new EventTarget();
          this.button = new EventTarget();
          this.attributes = new Map();
          this.details.open = false;
        }}
        querySelector(selector) {{
          return selector === "details" ? this.details : this.button;
        }}
        setAttribute(name, value) {{ this.attributes.set(name, String(value)); }}
        getAttribute(name) {{ return this.attributes.get(name) || null; }}
      }}
      globalThis.HTMLElement = FakeElement;
      globalThis.customElements = {{
        get(name) {{ return registry.get(name); }},
        define(name, ctor) {{ registry.set(name, ctor); }},
      }};

      await import({DISCLOSURE.as_uri()!r});
      const Disclosure = registry.get("hedron-disclosure");
      const disclosure = new Disclosure();
      let disclosureChanges = 0;
      disclosure.addEventListener("hedron-disclosure-change", () => disclosureChanges++);
      disclosure.connectedCallback();
      disclosure.connectedCallback();
      disclosure.details.dispatchEvent(new Event("toggle"));
      if (disclosureChanges !== 1) process.exit(2);

      await import({ACTION.as_uri()!r});
      const Action = registry.get("hedron-action-async");
      const action = new Action();
      let actionChanges = 0;
      action.addEventListener("hedron-action-change", () => actionChanges++);
      action.connectedCallback();
      action.connectedCallback();
      action.button.dispatchEvent(new Event("click"));
      if (actionChanges !== 1) process.exit(3);
    """
    subprocess.run(["node", "--input-type=module", "-e", script], check=True)
