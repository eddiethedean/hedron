# Single-file apps (pip evaluators)

Run these without cloning the monorepo. Requires Python 3.11+ and a working network for
`pip install`.

## Hello page

```bash
pip install "hedron>=0.18.0,<0.19" "uvicorn[standard]"
```

Save as `app.py`:

```python
from hedron import Hedron, Page, Text

app = Hedron(title="Demo", security="standard", session_secret="replace-me")


@app.page("/")
def home() -> Page:
    return Page(Text("Hello, Hedron"), title="Demo")
```

```bash
uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## CSRF form

Follow the pasteable app in [Minimal form POST](../guides/minimal-form.md).

## Live clock (polling)

Follow the pasteable app in [Live interaction](../guides/live-interaction.md)
(“poll a clock”).

## When you need the monorepo

Clone for Flask/Django reference apps, the team-admin reference app, and HDJ progressive
examples: [Runnable examples](runnable.md).
