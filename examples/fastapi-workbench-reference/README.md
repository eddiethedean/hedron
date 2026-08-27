# Plain FastAPI Workbench reference

Run behind Posit Workbench with only `fastapi-workbench` installed:

```bash
uv sync
cd examples/fastapi-workbench-reference
fastapi-workbench run app:app
```

Local:

```bash
cd examples/fastapi-workbench-reference
uvicorn app:app --reload
```

This app is exercised by the REALWB-030 Docker smoke matrix alongside
`examples/workbench-reference/app_facade.py` (hedron-posit) and
`examples/workbench-reference/app_posit.py` (hedron-posit), including the
Workbench **2025.05.1** floor probe.
