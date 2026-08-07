# hedron-extras

Curated optional toolkit for specialized data-app interactions and analysis
workbenches (phase 0.16). Built on public Hedron plugin contracts — not a second
component runtime.

```bash
pip install "hedron[extras]>=0.19.0,<0.20"
# or feature-scoped:
pip install "hedron-extras[code_editor,data_explorer]>=0.19.0,<0.20"
```

Ready to cut on `main` as **`0.19.0`** (last published PyPI/git = `v0.18.0`).

Install isolation: absent extras add no core import, browser asset, startup, or
transitive dependency cost. Specialty surfaces (`TerminalView`, joystick/device
bridges) are **Experimental** and fail closed without explicit policy.

See the [roadmap](https://hedron.readthedocs.io/en/latest/guides/roadmap/) and
[what’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).
