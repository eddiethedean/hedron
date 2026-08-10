#!/usr/bin/env python3
"""FLASK-027 smoke: import hedron_flask without FastAPI; flask-reference factory."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []

    if "fastapi" in sys.modules:
        # Prefer proving the adapter works even if FastAPI is installed in the
        # workspace; the critical check is that hedron_flask itself does not
        # require FastAPI imports to load.
        pass

    try:
        flask_mod = importlib.import_module("hedron_flask")
    except Exception as exc:  # noqa: BLE001
        print(f"import hedron_flask failed: {exc}", file=sys.stderr)
        return 1

    src = (ROOT / "packages" / "hedron-flask" / "src" / "hedron_flask").rglob("*.py")
    for path in src:
        text = path.read_text(encoding="utf-8")
        if "import fastapi" in text or "from fastapi" in text:
            errors.append(f"{path.relative_to(ROOT)} imports FastAPI")

    ref = ROOT / "examples" / "flask-reference" / "app.py"
    if not ref.is_file():
        errors.append("missing examples/flask-reference/app.py")
    else:
        sys.path.insert(0, str(ref.parent))
        try:
            from app import create_app  # type: ignore[import-not-found]

            app = create_app()
            client = app.test_client()
            home = client.get("/")
            if home.status_code != 200:
                errors.append(f"flask-reference / returned {home.status_code}")
            frag = client.get(
                "/fragment",
                headers={"HX-Request": "true", "HX-Target": "panel"},
            )
            if frag.status_code != 200:
                errors.append(f"flask-reference /fragment returned {frag.status_code}")
            body = frag.get_data(as_text=True)
            if "fragment" not in body.lower():
                errors.append("flask-reference fragment body missing expected text")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"flask-reference smoke failed: {exc}")
        finally:
            if str(ref.parent) in sys.path:
                sys.path.remove(str(ref.parent))

    if not hasattr(flask_mod, "HedronFlask"):
        errors.append("hedron_flask.HedronFlask missing")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: smoke_flask_027")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
