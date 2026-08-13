# What’s new in 0.31

!!! note "Living train is 0.32"

    Pin `hedron>=0.34.0,<0.35`. See [What’s new in 0.32](whats-new-0.32.md).

**Published** as `v0.31.0`. Historical pin: `hedron>=0.31.0,<0.32`.

Phase **0.31** (D-059 / RFC-0064 / RFC-0061) graduates developer and portable
conformance tooling and ships a reviewable Streamlit AST migration assistant.

## Highlights

- **Tooling-grade packages:** `hedron-conformance`, `hedron-sample-kit`, `hedron-sim`,
  and `hedron-notebook` for their stated development/conformance roles (not app
  production servers). Notebook preview **refuses** non-loopback binds.
- **Node/Java evaluators:** `hedron-runtime-node` `0.31.0` and `hedron-runtime-java`
  `0.31.0` run the portable fixture corpus offline with publish-ready packaging.
- **`hedron migrate streamlit`:** non-executing AST inventory and secure Hedron
  scaffold with text/JSON/SARIF findings; never overwrites the Streamlit source.

## Upgrade

```bash
python -m pip install -U "hedron>=0.34.0,<0.35"
# Optional tooling:
python -m pip install -U "hedron[conformance]>=0.32.0,<0.33"
python -m pip install -U "hedron-sample-kit>=0.1.10,<0.2"
hedron migrate streamlit streamlit_app.py --out hedron_app
```

Details: [RELEASE_0_31](../acceptance/RELEASE_0_31.md) · [upgrade guide](upgrade.md).
