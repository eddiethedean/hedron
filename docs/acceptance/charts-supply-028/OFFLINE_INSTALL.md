# Offline install rehearsal (SUPPLY-028)

Owning gate: `SUPPLY-028`. Goal: prove Supported chart + native workflows install
without CDN fetches.

## Rehearsal outline

1. **Prepare a wheelhouse** on a networked machine:

   ```bash
   mkdir -p /tmp/hedron-offline-wheels
   pip download -d /tmp/hedron-offline-wheels \
     "hedron[charts,native]>=0.28.2,<0.29" \
     "matplotlib"
   ```

2. **Transfer** `/tmp/hedron-offline-wheels` (and optional `hedron-native` sdist)
   to an air-gapped / network-restricted environment.

3. **Install offline**:

   ```bash
   pip install --no-index --find-links=/tmp/hedron-offline-wheels \
     "hedron[charts,native]>=0.28.2,<0.29"
   ```

4. **Smoke**:

   ```bash
   python -c "from hedron_charts import BarChart; from hedron_native import escape_text; print(escape_text('<x>'))"
   ```

5. Confirm chart HTML contains **no** `cdn.` / remote `script src` for Supported
   static paths (see `tests/browser/test_charts_028_matrix.py` when
   `HEDRON_BROWSER=1`).

## Pass criteria

- Install succeeds with `--no-index`
- Beginner static charts render with local matplotlib / SVG fallback
- `HEDRON_NATIVE_DISABLE=1` still renders correctly (native never required for
  correctness)
- Experimental interactive hosts remain opt-in and locally pinned when used
