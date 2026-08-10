#!/usr/bin/env python3
"""HDJ-027 smoke: parse/render progressive HDJ templates."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    progressive = ROOT / "examples" / "hdj-progressive"
    if not (progressive / "app.py").is_file():
        print("missing examples/hdj-progressive/app.py", file=sys.stderr)
        return 1

    sys.path.insert(0, str(progressive))
    try:
        from app import bind  # type: ignore[import-not-found]

        hj = bind()
        # Minimal template must render without a view model.
        result = hj.render("01_minimal.hdj", {})
        html = result.html if hasattr(result, "html") else str(result)
        if "Hello from a minimal HDJ template" not in html:
            errors.append("01_minimal.hdj render missing expected text")
        # Prologue version remains 1.
        for name in ("01_minimal.hdj", "02_jinja.hdj", "03_components.hdj"):
            text = (progressive / "templates" / name).read_text(encoding="utf-8")
            if "version = 1" not in text:
                errors.append(f"{name} missing version = 1")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"hdj-progressive smoke failed: {exc}")
    finally:
        if str(progressive) in sys.path:
            sys.path.remove(str(progressive))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: smoke_hdj_027")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
