# hedron-extras

Curated optional toolkit for specialized data-app interactions and analysis
workbenches (phase 0.16). Built on public Hedron plugin contracts — not a second
component runtime.

```bash
pip install "hedron[extras]"
# or feature-scoped:
pip install "hedron-extras[code_editor,data_explorer]"
```

Install isolation: absent extras add no core import, browser asset, startup, or
transitive dependency cost. Specialty surfaces (`TerminalView`, joystick/device
bridges) are **Experimental** and fail closed without explicit policy.

See the [roadmap](https://hedron.readthedocs.io/en/latest/guides/roadmap/) and
[what’s ready](https://hedron.readthedocs.io/en/latest/guides/whats-ready/).
