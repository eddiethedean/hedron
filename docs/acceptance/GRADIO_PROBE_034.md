# Phase 0.34 Gradio contract probe (recorded fixtures)

**Owner:** phase 0.34 / [#90](https://github.com/eddiethedean/hedron/issues/90)  
**Gates:** `COMPAT-034`, `VENDOR-034`  
**Implements:** [HEDRON_GRADIO_034](../implementation/HEDRON_GRADIO_034.md) Stage 0

## Purpose

Sanitized recorded upstream shapes for gate checkers without requiring live Gradio/HF endpoints
during CI.

## Fixtures

| File | Role |
|---|---|
| `view_api_minimal.json` | Minimal `gradio_client` discovery shape |
| `view_api_stream.json` | Endpoint with streaming metadata |
| `hf_space_cold_start.json` | Queue/cold-start status sequence |
| `hf_quota_error.json` | Provider quota/outage translation |

## Redaction rules

Never commit real HF tokens, Space secrets, or live hostnames tied to private deployments.
Use `example.invalid` hosts and synthetic ids only.

## Commands

```bash
python scripts/check_compat_034.py
python scripts/check_vendor_034.py
```

Optional live smoke (maintainer-only):

```bash
bash scripts/realgradio_034_probe.sh
```

Live smoke output belongs in `docs/acceptance/realgradio-034/RESULT.log` with secrets redacted.
