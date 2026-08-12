"""Source-map records linking generated artifacts to Streamlit spans."""

from __future__ import annotations

import json
from typing import Any

from hedron.migrate.ir import StreamlitMigrationPlan


def build_source_map(
    plan: StreamlitMigrationPlan,
    *,
    generated_files: dict[str, str],
) -> dict[str, Any]:
    return {
        "schema_version": plan.schema_version,
        "mapping_catalog_version": plan.mapping_catalog_version,
        "sources": [
            {
                "path": u.relative_path,
                "content_hash": u.content_hash,
                "is_entrypoint": u.is_entrypoint,
            }
            for u in plan.source_units
        ],
        "operations": [
            {
                "op_id": c.op_id,
                "symbol": c.symbol,
                "disposition": c.disposition.value,
                "span": c.span.to_dict(),
                "generated": "app.py" if c.disposition.value in {"translated", "scaffolded"} else None,
            }
            for c in plan.calls
        ],
        "generated_files": generated_files,
    }


def dumps_source_map(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
