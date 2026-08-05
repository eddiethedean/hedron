"""Backend-neutral chart annotation overlays."""

from __future__ import annotations

from collections.abc import Sequence

from hedron_core.visualization import ChartAnnotation, ChartOutput, validate_annotation

__all__ = ["apply_annotations"]


def apply_annotations(
    output: ChartOutput,
    annotations: Sequence[ChartAnnotation],
) -> ChartOutput:
    validated = tuple(validate_annotation(ann) for ann in annotations)
    meta = dict(output.metadata)
    existing = list(meta.get("annotations") or [])
    existing.extend(
        {
            "kind": ann.kind,
            "label": ann.label,
            "trace_id": ann.trace_id,
            "description": ann.description,
            "payload": dict(ann.payload),
        }
        for ann in validated
    )
    meta["annotations"] = existing
    return ChartOutput(
        kind=output.kind,
        body=output.body,
        accessibility=output.accessibility,
        media_type=output.media_type,
        assets=output.assets,
        metadata=meta,
        payload_bytes=output.payload_bytes,
    )
