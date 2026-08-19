# FastAPI / Pydantic convergence sample

First-party FastAPI demo for **phase 0.49** lifetimes, native/expanded binding, and
non-granting scopes. Existing `ViewParams` / `FormBody` keep working. This example
targets the current **0.51.x** train (phase 0.49 contracts still apply).

## Run

From the repository root:

```bash
uv sync
uv run uvicorn app:app --app-dir examples/fastapi-pydantic --reload
```

Open <http://127.0.0.1:8000/items?q=ok>.

| Route | What it shows |
|---|---|
| `/items` | Query-only `ViewParams` (native-model eligible) |
| `/items/{item_id}` | Mixed path/query stays expanded-fields |
| `/save` | FormBody command with CSRF; JSON still 415 |

FailFast and pydantic-settings are not admitted on this sample.
