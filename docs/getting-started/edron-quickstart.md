---
description: Scaffold, run, and edit a complete Edron application in about five minutes.
search:
  boost: 2
---

# Build your first Edron app

This path takes about five minutes with Python **3.10–3.14** and
[`uv`](https://docs.astral.sh/uv/). Node.js is not required.

<!-- hedron-release-status -->

## 1. Scaffold and run

```bash
uvx --from "edron>=1.0.0,<1.1" edron new my-app --template minimal
cd my-app
uv sync
uv run edron run app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The generated project is an
ordinary ASGI application and can also run with `uv run uvicorn app:app --reload`.

## 2. Understand the page

The generated `app.py` follows this shape:

```python
import edron as ed

app = ed.App(title="Sales", security="standard")


@app.page("/", title="Sales dashboard")
class Home(ed.Page):
    def render(self) -> None:
        self.metric("Orders", 128, delta="+12")
        self.text("A useful page rendered entirely on the server.")
```

`App` owns the native application and registrations. A fresh `Page` instance handles each
request. Calls such as `metric()` and `text()` append components to that request's page tree;
the page instance is not durable user state.

Change `128` to `129`, save the file, and refresh the browser.

## 3. Add a bounded interaction

Add these methods inside `Home`:

```diff
     @ed.fragment
     def status(self) -> None:
         self.text("All systems operational")

     @ed.action
     def refresh_status(self) -> ed.Outcome:
         return ed.refresh(self.status)
```

Then call them from `render()`:

```diff
         self.status()
         self.button("Refresh status", action=self.refresh_status)
```

The button posts to a declared action. The outcome refreshes only the registered fragment,
while Edron preserves Hedron's CSRF and target policies.

## 4. Verify the application

```bash
uv run edron check app.py
uv run edron explain app:app
uv run edron doctor app:app --profile local
```

`check` is static and does not execute the application. `explain` and `doctor` import only
source you trust.

## If something fails

| Symptom | Fix |
|---|---|
| No matching Edron distribution | Confirm the version and index in [Installation](installation.md) |
| `edron: command not found` | Use `uv run edron` or `python -m edron` in the project environment |
| Reload requires an import target | Use `app:app`, not a bare `.py` filename, with `--reload` |
| Port 8000 is busy | Add `--port 8001` and open that port |
| A POST returns 403 | Load the page first, then review the security profile and CSRF guidance |

## Continue

- [Edron user guide](../guides/edron-user-guide.md)
- [Edron API by task](../api/EDRON_REFERENCE.md)
- [Edron examples](../examples/edron.md)
- [Deployment](../guides/deployment.md)
