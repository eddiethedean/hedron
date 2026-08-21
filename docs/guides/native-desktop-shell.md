# Native desktop shell recipe (Experimental, phase 0.16 / RFC-0038)

This is **packaging guidance only** — not a second UI runtime and not a Supported
multi-window application model. The same HTML/HTMX ASGI app runs under uvicorn;
pywebview (or similar) embeds the local origin.

## Minimal recipe

```bash
pip install "hedron[extras]>=0.56.0,<0.57" "uvicorn[standard]" pywebview
```

```python
# native_shell.py — Experimental packaging recipe
import threading

import uvicorn
import webview

from app import app  # your Hedron FastAPI app


def _serve() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")


if __name__ == "__main__":
    threading.Thread(target=_serve, daemon=True).start()
    webview.create_window("Hedron", "http://127.0.0.1:8765/")
    webview.start()
```

## Policy

- Do not relax CSP or auto-enable DevTools escape hatches in production recipes.
- Multi-worker correctness is unchanged: native shell does not imply single-worker-only apps.
- Specialty maturity remains **Experimental** in what’s-ready / STABILITY.
- Deliberate non-parity with NiceGUI native/Vue/`run_javascript` stacks.
