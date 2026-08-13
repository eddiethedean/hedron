# Offline install rehearsal (SUPPLY-035)

Owning gate: `SUPPLY-035` / `SOLVER-035`. Goal: prove Supported fleet extras install from a
local wheelhouse without index access.

## Rehearsal outline

1. **Prepare a wheelhouse** on a networked machine:

   ```bash
   mkdir -p /tmp/hedron-offline-wheels
   pip download -d /tmp/hedron-offline-wheels \
     "hedron[data,jinja,charts,mcp,gradio,workbench,posit,extras]>=0.35.0,<0.36"
   ```

2. **Transfer** `/tmp/hedron-offline-wheels` to an air-gapped environment.

3. **Install offline**:

   ```bash
   pip install --no-index --find-links=/tmp/hedron-offline-wheels \
     "hedron[data,jinja,charts]>=0.35.0,<0.36"
   ```

4. **Smoke**:

   ```bash
   python -c "import hedron, hedron_data, hedron_charts; print(hedron.__version__)"
   ```

## Pass criteria

- Install succeeds with `--no-index` and a prepared wheelhouse
- Optional satellites may be omitted; absence adds no core startup cost
- Mixed-version pins that violate inventory floors fail closed at resolve time
