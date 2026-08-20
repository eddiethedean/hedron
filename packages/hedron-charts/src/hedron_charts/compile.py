"""ChartSpec → ChartPlan compiler (GRAMMAR-038 / DESIGN-038)."""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections.abc import Mapping, Sequence
from typing import Any, cast

from hedron_charts.operators import (
    ALLOWED_OPERATORS,
    SUPPORTED_ENCODINGS,
    SUPPORTED_MARKS,
    SUPPORTED_SCALES,
)
from hedron_charts.spec import (
    SCHEMA_ID,
    SCHEMA_VERSION,
    AccessibilityDef,
    AccessibilityPlan,
    ChartPlan,
    ChartSpec,
    DataRef,
    Encoding,
    ExportPolicy,
    FieldDef,
    GuideDef,
    InteractionDef,
    MarkDef,
    RendererDecision,
    ScaleDef,
    ThemeDef,
    TransformDef,
)
from hedron_core.diagnostics import HedronError, error
from hedron_core.visualization import DEFAULT_MAX_CHART_ROWS, DEFAULT_MAX_PAYLOAD_BYTES

# Stage 1 locked Canvas threshold (marks).
CANVAS_MARK_THRESHOLD = 2500

MAX_FIELDS = 64
MAX_TRANSFORMS = 32
MAX_FACETS = 16
MAX_MARKS = 10000
MAX_LABELS = 500
MAX_PAYLOAD_BYTES = DEFAULT_MAX_PAYLOAD_BYTES
MAX_ROWS = DEFAULT_MAX_CHART_ROWS
MAX_EXPORT_PX = 4096

__all__ = [
    "CANVAS_MARK_THRESHOLD",
    "beginner_to_spec",
    "compile_chart",
    "parse_chart_spec",
]


def _chart_error(code: str, title: str, explanation: str, remediation: str) -> HedronError:
    return error(code, title=title, explanation=explanation, remediation=remediation)


def _fingerprint(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _reject_pollution(obj: object, path: str = "$") -> None:
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            key_s = str(key)
            if key_s in {"__proto__", "constructor", "prototype"}:
                raise _chart_error(
                    "HED-CHART-0070",
                    "Prototype-pollution key rejected",
                    f"Forbidden key {key_s!r} at {path}.",
                    "Remove prototype-pollution keys from ChartSpec payloads.",
                )
            _reject_pollution(value, f"{path}.{key_s}")
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            _reject_pollution(item, f"{path}[{i}]")


def parse_chart_spec(value: Mapping[str, object] | ChartSpec) -> ChartSpec:
    if isinstance(value, ChartSpec):
        return value
    _reject_pollution(value)
    version = value.get("schema_version", SCHEMA_VERSION)
    if version != SCHEMA_VERSION:
        raise _chart_error(
            "HED-CHART-0020",
            "Unsupported ChartSpec schema version",
            f"schema_version {version!r} is not supported; expected {SCHEMA_VERSION}.",
            "Upgrade the spec or pin hedron-charts to a compatible line.",
        )
    unknown = set(value) - {
        "schema_version",
        "data",
        "marks",
        "scales",
        "guides",
        "transforms",
        "composition",
        "annotations",
        "interaction",
        "theme",
        "export",
        "renderer",
        "accessibility",
    }
    if unknown:
        raise _chart_error(
            "HED-CHART-0021",
            "Unknown ChartSpec field",
            f"Unknown fields: {sorted(unknown)}.",
            "Remove unknown fields; ChartSpec is fail-closed.",
        )
    try:
        return ChartSpec.model_validate(value)
    except Exception as exc:
        raise _chart_error(
            "HED-CHART-0022",
            "Invalid ChartSpec",
            str(exc),
            "Fix field types and required accessibility title/description.",
        ) from exc


def _validate_operators(transforms: Sequence[TransformDef]) -> None:
    if len(transforms) > MAX_TRANSFORMS:
        raise _chart_error(
            "HED-CHART-0071",
            "Transform limit exceeded",
            f"Received {len(transforms)} transforms; max is {MAX_TRANSFORMS}.",
            "Reduce transforms or aggregate server-side.",
        )
    for tr in transforms:
        if tr.op not in ALLOWED_OPERATORS:
            raise _chart_error(
                "HED-CHART-0030",
                "Unknown transform operator",
                f"Operator {tr.op!r} is not in the closed catalog.",
                "Use only operators listed in CHART_SPEC.md.",
            )


def _validate_marks(marks: Sequence[MarkDef]) -> None:
    if not marks:
        raise _chart_error(
            "HED-CHART-0023",
            "ChartSpec requires marks",
            "At least one mark definition is required.",
            "Add a Supported mark such as line, bar, or point.",
        )
    for mark in marks:
        if mark.type not in SUPPORTED_MARKS:
            raise _chart_error(
                "HED-CHART-0024",
                "Unsupported mark type",
                f"Mark type {mark.type!r} is not Supported in 0.38.",
                f"Use one of: {sorted(SUPPORTED_MARKS)}.",
            )
        for enc_name, enc in mark.encodings.items():
            if enc_name not in SUPPORTED_ENCODINGS:
                raise _chart_error(
                    "HED-CHART-0025",
                    "Unsupported encoding channel",
                    f"Encoding {enc_name!r} is not Supported.",
                    f"Use one of: {sorted(SUPPORTED_ENCODINGS)}.",
                )
            if enc.aggregate and enc.aggregate not in ALLOWED_OPERATORS:
                raise _chart_error(
                    "HED-CHART-0031",
                    "Unknown aggregate operator",
                    f"Aggregate {enc.aggregate!r} is not allowed.",
                    "Use a closed aggregate operator.",
                )


def _validate_scales(scales: Sequence[ScaleDef]) -> None:
    for scale in scales:
        if scale.type not in SUPPORTED_SCALES:
            raise _chart_error(
                "HED-CHART-0026",
                "Unsupported scale type",
                f"Scale type {scale.type!r} is not Supported.",
                f"Use one of: {sorted(SUPPORTED_SCALES)}.",
            )


def _as_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _apply_filter(rows: list[dict[str, object]], tr: TransformDef) -> list[dict[str, object]]:
    field = tr.field
    if not field:
        return rows
    op = tr.params.get("compare", "is_not_null")
    target = tr.params.get("value")
    out: list[dict[str, object]] = []
    for row in rows:
        val = row.get(field)
        keep = True
        if op == "is_null":
            keep = val is None
        elif op == "is_not_null":
            keep = val is not None
        elif op == "eq":
            keep = val == target
        elif op == "ne":
            keep = val != target
        elif op == "gt":
            a, b = _as_number(val), _as_number(target)
            keep = a is not None and b is not None and a > b
        elif op == "ge":
            a, b = _as_number(val), _as_number(target)
            keep = a is not None and b is not None and a >= b
        elif op == "lt":
            a, b = _as_number(val), _as_number(target)
            keep = a is not None and b is not None and a < b
        elif op == "le":
            a, b = _as_number(val), _as_number(target)
            keep = a is not None and b is not None and a <= b
        elif op == "in":
            keep = val in cast(Any, target or ())
        elif op == "not_in":
            keep = val not in cast(Any, target or ())
        if keep:
            out.append(row)
    return out


def _apply_calculate(rows: list[dict[str, object]], tr: TransformDef) -> list[dict[str, object]]:
    op = tr.params.get("operator") or tr.op
    if op not in ALLOWED_OPERATORS:
        raise _chart_error(
            "HED-CHART-0030",
            "Unknown transform operator",
            f"Operator {op!r} is not in the closed catalog.",
            "Use only operators listed in CHART_SPEC.md.",
        )
    as_name = tr.as_ or f"{tr.field or 'value'}_{op}"
    raw_args = tr.params.get("args") or []
    args = cast(list[object], raw_args)
    out: list[dict[str, object]] = []
    for row in rows:
        values: list[object] = [row.get(a) if isinstance(a, str) else a for a in args]
        if tr.field and not values:
            values = [row.get(tr.field)]
        result: object = None
        nums = [_as_number(v) for v in values]
        if op == "add" and all(n is not None for n in nums):
            present: list[float] = [n for n in nums if n is not None]
            result = sum(present)
        elif op == "subtract" and len(nums) >= 2 and nums[0] is not None and nums[1] is not None:
            result = nums[0] - nums[1]
        elif op == "multiply" and all(n is not None for n in nums):
            present = [n for n in nums if n is not None]
            result = math.prod(present)
        elif op == "divide" and len(nums) >= 2 and nums[0] is not None and nums[1]:
            result = nums[0] / nums[1]
        elif op == "negate" and nums and nums[0] is not None:
            result = -nums[0]
        elif op == "abs" and nums and nums[0] is not None:
            result = abs(nums[0])
        elif op == "round" and nums and nums[0] is not None:
            result = round(nums[0])
        elif op == "floor" and nums and nums[0] is not None:
            result = math.floor(nums[0])
        elif op == "ceil" and nums and nums[0] is not None:
            result = math.ceil(nums[0])
        elif op == "min" and all(n is not None for n in nums):
            present = [n for n in nums if n is not None]
            result = min(present)
        elif op == "max" and all(n is not None for n in nums):
            present = [n for n in nums if n is not None]
            result = max(present)
        elif op == "coalesce":
            result = next((v for v in values if v is not None), None)
        elif op == "concat":
            result = "".join("" if v is None else str(v) for v in values)
        elif op == "lower" and values:
            result = None if values[0] is None else str(values[0]).lower()
        elif op == "upper" and values:
            result = None if values[0] is None else str(values[0]).upper()
        elif op == "length" and values:
            result = 0 if values[0] is None else len(str(values[0]))
        else:
            result = values[0] if values else None
        cloned = dict(row)
        cloned[as_name] = result
        out.append(cloned)
    return out


def _apply_aggregate(rows: list[dict[str, object]], tr: TransformDef) -> list[dict[str, object]]:
    group_by = cast(list[str], list(cast(Any, tr.params.get("groupby") or [])))
    metrics = cast(
        list[dict[str, object]], tr.params.get("metrics") or [{"op": "count", "as": "count"}]
    )
    buckets: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        key = tuple(row.get(g) for g in group_by)
        buckets.setdefault(key, []).append(row)
    out: list[dict[str, object]] = []
    for key, group in buckets.items():
        item: dict[str, object] = {g: key[i] for i, g in enumerate(group_by)}
        for metric in metrics:
            mop = metric.get("op", "count")
            field = metric.get("field")
            as_name = cast(str, metric.get("as") or f"{mop}_{field or 'all'}")
            field_name = field if isinstance(field, str) else None
            vals = [_as_number(r.get(field_name)) for r in group] if field_name else []
            nums = [v for v in vals if v is not None]
            if mop == "count":
                item[as_name] = len(group)
            elif mop == "count_distinct" and field_name:
                item[as_name] = len({r.get(field_name) for r in group})
            elif mop == "sum":
                item[as_name] = sum(nums)
            elif mop == "mean":
                item[as_name] = statistics.fmean(nums) if nums else None
            elif mop == "median":
                item[as_name] = statistics.median(nums) if nums else None
            elif mop == "min":
                item[as_name] = min(nums) if nums else None
            elif mop == "max":
                item[as_name] = max(nums) if nums else None
            elif mop == "stdev":
                item[as_name] = statistics.pstdev(nums) if len(nums) > 1 else 0.0
            elif mop == "first":
                item[as_name] = group[0].get(field_name) if group and field_name else None
            elif mop == "last":
                item[as_name] = group[-1].get(field_name) if group and field_name else None
            else:
                raise _chart_error(
                    "HED-CHART-0031",
                    "Unknown aggregate operator",
                    f"Aggregate {mop!r} is not allowed.",
                    "Use a closed aggregate operator.",
                )
        out.append(item)
    return out


def _apply_sort(rows: list[dict[str, object]], tr: TransformDef) -> list[dict[str, object]]:
    field = tr.field
    if not field:
        return rows
    reverse = bool(tr.params.get("descending") or tr.params.get("desc"))
    return sorted(rows, key=lambda r: (r.get(field) is None, r.get(field)), reverse=reverse)


def _apply_sample(rows: list[dict[str, object]], tr: TransformDef) -> list[dict[str, object]]:
    n = int(cast(Any, tr.params.get("n") or MAX_ROWS))
    if n < 1:
        raise _chart_error(
            "HED-CHART-0071",
            "Invalid sample size",
            f"sample n must be >= 1; got {n}.",
            "Pass a positive sample size.",
        )
    if len(rows) <= n:
        return rows
    step = max(1, len(rows) // n)
    return rows[::step][:n]


def _apply_stack(rows: list[dict[str, object]], tr: TransformDef) -> list[dict[str, object]]:
    field = tr.field or "y"
    group = cast(list[str], list(cast(Any, tr.params.get("groupby") or [])))
    as_y0 = tr.as_ or f"{field}_y0"
    as_y1 = cast(str, tr.params.get("as_y1") or f"{field}_y1")
    buckets: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        key = tuple(row.get(g) for g in group)
        buckets.setdefault(key, []).append(row)
    out: list[dict[str, object]] = []
    for group_rows in buckets.values():
        running = 0.0
        for row in group_rows:
            cloned = dict(row)
            val = _as_number(row.get(field)) or 0.0
            cloned[as_y0] = running
            running += val
            cloned[as_y1] = running
            out.append(cloned)
    return out


def _apply_bin(rows: list[dict[str, object]], tr: TransformDef) -> list[dict[str, object]]:
    field = tr.field
    if not field:
        return rows
    bins = int(cast(Any, tr.params.get("bins") or 10))
    if bins < 1:
        raise _chart_error(
            "HED-CHART-0032",
            "Invalid bin count",
            f"bins must be >= 1; got {bins}.",
            "Pass a positive bin count.",
        )
    nums = [_as_number(r.get(field)) for r in rows]
    present = [n for n in nums if n is not None]
    if not present:
        return rows
    lo, hi = min(present), max(present)
    width = (hi - lo) / bins if hi > lo else 1.0
    as_name = tr.as_ or f"{field}_bin"
    out: list[dict[str, object]] = []
    for row, num in zip(rows, nums, strict=True):
        cloned = dict(row)
        if num is None:
            cloned[as_name] = None
        else:
            idx = min(bins - 1, int((num - lo) / width)) if width else 0
            cloned[as_name] = lo + idx * width
        out.append(cloned)
    return out


def apply_transforms(
    rows: Sequence[Mapping[str, object]], transforms: Sequence[TransformDef]
) -> list[dict[str, object]]:
    current: list[dict[str, object]] = [dict(r) for r in rows]
    for tr in transforms:
        if tr.op == "filter":
            current = _apply_filter(current, tr)
        elif tr.op == "aggregate":
            current = _apply_aggregate(current, tr)
        elif tr.op == "sort":
            current = _apply_sort(current, tr)
        elif tr.op == "sample":
            current = _apply_sample(current, tr)
        elif tr.op == "stack":
            current = _apply_stack(current, tr)
        elif tr.op == "bin":
            current = _apply_bin(current, tr)
        elif tr.op == "fold":
            fields = cast(list[str], list(cast(Any, tr.params.get("fields") or [])))
            as_key = cast(str, tr.params.get("as_key") or "key")
            as_value = cast(str, tr.params.get("as_value") or "value")
            folded: list[dict[str, object]] = []
            for row in current:
                base = {k: v for k, v in row.items() if k not in fields}
                for f in fields:
                    item = dict(base)
                    item[as_key] = f
                    item[as_value] = row.get(f)
                    folded.append(item)
            current = folded
        elif tr.op in ALLOWED_OPERATORS:
            current = _apply_calculate(current, tr)
        else:
            raise _chart_error(
                "HED-CHART-0030",
                "Unknown transform operator",
                f"Operator {tr.op!r} is not in the closed catalog.",
                "Use only operators listed in CHART_SPEC.md.",
            )
    return current


def _infer_domain(
    rows: Sequence[Mapping[str, object]], field: str, scale_type: str
) -> list[object]:
    values = [row.get(field) for row in rows]
    if scale_type in {"ordinal", "point", "band"}:
        seen: list[object] = []
        for v in values:
            if v not in seen:
                seen.append(v)
        return seen
    nums = [_as_number(v) for v in values]
    present = [n for n in nums if n is not None]
    if not present:
        return [0, 1]
    lo, hi = min(present), max(present)
    if scale_type == "log":
        if lo <= 0:
            raise _chart_error(
                "HED-CHART-0033",
                "Log scale domain invalid",
                "Log scales require strictly positive domains.",
                "Filter non-positive values or use linear/symlog.",
            )
        return [lo, hi]
    if scale_type in {"linear", "power", "symlog", "quantized"} and lo > 0:
        # Bar charts prefer zero baseline when positive.
        return [0, hi]
    return [lo, hi]


def _encoding_explanation(spec: ChartSpec) -> str:
    parts: list[str] = []
    for mark in spec.marks:
        channels = ", ".join(
            f"{name}={enc.field or enc.value}" for name, enc in mark.encodings.items()
        )
        parts.append(f"{mark.type} mark with {channels or 'no encodings'}")
    return "; ".join(parts) if parts else "Chart with no encodings"


def _interaction_help(interaction: InteractionDef) -> str:
    enabled: list[str] = []
    if interaction.inspect:
        enabled.append("inspect")
    if interaction.focus_navigation:
        enabled.append("keyboard focus")
    if interaction.legend_filter:
        enabled.append("legend filter")
    if interaction.select:
        enabled.append("select")
    if interaction.brush:
        enabled.append("brush")
    if interaction.zoom_pan_reset:
        enabled.append("zoom/pan/reset")
    if interaction.crosshair:
        enabled.append("crosshair")
    if interaction.drill_intent:
        enabled.append(f"drill:{interaction.drill_intent}")
    return "Interactions: " + (", ".join(enabled) if enabled else "none")


def _choose_renderer(mark_count: int, preference: str) -> RendererDecision:
    if preference == "canvas" or mark_count >= CANVAS_MARK_THRESHOLD:
        reason = (
            f"mark_count {mark_count} >= threshold {CANVAS_MARK_THRESHOLD}"
            if mark_count >= CANVAS_MARK_THRESHOLD
            else "author requested canvas"
        )
        return RendererDecision(
            paint="canvas",
            reason=reason,
            mark_count=mark_count,
            canvas_threshold=CANVAS_MARK_THRESHOLD,
        )
    return RendererDecision(
        paint="svg",
        reason="default semantic SVG under mark threshold",
        mark_count=mark_count,
        canvas_threshold=CANVAS_MARK_THRESHOLD,
    )


def _build_mark_records(
    rows: Sequence[Mapping[str, object]], marks: Sequence[MarkDef]
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for mi, mark in enumerate(marks):
        for ri, row in enumerate(rows):
            identity = mark.identity or f"m{mi}-r{ri}"
            payload: dict[str, object] = {
                "identity": identity,
                "type": mark.type,
                "row_index": ri,
                "values": {
                    name: (row.get(enc.field) if enc.field else enc.value)
                    for name, enc in mark.encodings.items()
                },
            }
            records.append(payload)
            if len(records) > MAX_MARKS:
                raise _chart_error(
                    "HED-CHART-0072",
                    "Mark limit exceeded",
                    f"Mark count exceeds {MAX_MARKS}.",
                    "Aggregate, sample, or raise limits explicitly via inventory bounds.",
                )
    return records


def compile_chart(spec: ChartSpec | Mapping[str, object]) -> ChartPlan:
    parsed = parse_chart_spec(spec)
    _validate_operators(parsed.transforms)
    _validate_marks(parsed.marks)
    _validate_scales(parsed.scales)

    rows = list(parsed.data.rows)
    if len(rows) > MAX_ROWS:
        raise _chart_error(
            "HED-CHART-0002",
            "Chart row limit exceeded",
            f"Received {len(rows)} rows; max is {MAX_ROWS}.",
            "Aggregate server-side or raise VisualizationLimits.max_rows explicitly.",
        )
    if len(parsed.data.fields) > MAX_FIELDS:
        raise _chart_error(
            "HED-CHART-0071",
            "Field limit exceeded",
            f"Received {len(parsed.data.fields)} fields; max is {MAX_FIELDS}.",
            "Reduce fields.",
        )

    warnings: list[str] = []
    transformed = apply_transforms(rows, parsed.transforms)
    facets = parsed.composition.get("facet")
    if isinstance(facets, list) and len(facets) > MAX_FACETS:
        raise _chart_error(
            "HED-CHART-0071",
            "Facet limit exceeded",
            f"Received {len(facets)} facets; max is {MAX_FACETS}.",
            "Reduce facets.",
        )

    domains: dict[str, list[object]] = {}
    scales = list(parsed.scales)
    # Infer scales from encodings when authors omit them.
    for mark in parsed.marks:
        for channel, enc in mark.encodings.items():
            if not enc.field:
                continue
            scale_name = enc.scale or channel
            scale_type = next((s.type for s in scales if s.name == scale_name), None)
            if scale_type is None:
                scale_type = "ordinal" if enc.type in {"string", "boolean"} else "linear"
                if enc.type == "temporal":
                    scale_type = "time"
                scales.append(ScaleDef(name=scale_name, type=scale_type))
                warnings.append(f"inferred scale {scale_name}:{scale_type}")
            if scale_name not in domains:
                domains[scale_name] = _infer_domain(transformed, enc.field, scale_type)

    # Explicit author domains win.
    for scale in parsed.scales:
        if scale.domain is not None:
            domains[scale.name] = list(scale.domain)

    mark_records = _build_mark_records(transformed, parsed.marks)
    renderer = _choose_renderer(len(mark_records), parsed.renderer)

    # Bar zero-baseline disclosure
    for mark in parsed.marks:
        if mark.type == "bar":
            y_enc = mark.encodings.get("y")
            scale_name = (y_enc.scale if y_enc else None) or "y"
            domain = domains.get(scale_name) or []
            if domain and _as_number(domain[0]) not in {0}:
                warnings.append(
                    "bar_nonzero_baseline: explicit non-zero domain requires disclosure"
                )

    a11y = AccessibilityPlan(
        title=parsed.accessibility.title,
        description=parsed.accessibility.description,
        encoding_explanation=_encoding_explanation(parsed),
        summary=parsed.accessibility.summary or _encoding_explanation(parsed),
        interaction_help=_interaction_help(parsed.interaction),
        table_rows=tuple(transformed),
        include_table=parsed.accessibility.include_table,
    )

    guides = list(parsed.guides)
    if not guides:
        for name in domains:
            guides.append(GuideDef(kind="axis", scale=name, title=name))
        guides.append(GuideDef(kind="title", title=parsed.accessibility.title))

    density = parsed.theme.density
    layout: dict[str, object] = {
        "density": density,
        "margin": {"compact": 24, "ordinary": 40, "wide": 56}[density],
        "width_hint": {"compact": 320, "ordinary": 640, "wide": 960}[density],
        "height_hint": {"compact": 200, "ordinary": 360, "wide": 480}[density],
    }

    redacted_rows: list[dict[str, object]] = []
    for row in transformed:
        cleaned: dict[str, object] = {}
        for k, v in row.items():
            if "secret" in str(k).lower() or "password" in str(k).lower():
                cleaned[str(k)] = "***"
            else:
                cleaned[str(k)] = v
        redacted_rows.append(cleaned)

    spec_fp = _fingerprint(parsed.to_json_dict())
    data_fp = _fingerprint(redacted_rows)
    assets = (
        "hedron-charts:hedron-chart.mjs",
        "hedron-charts:hedron-chart.css",
    )

    return ChartPlan(
        schema_id=SCHEMA_ID,
        schema_version=SCHEMA_VERSION,
        spec_fingerprint=spec_fp,
        data_fingerprint=data_fp,
        domains=domains,
        guides=tuple(guides),
        marks=tuple(mark_records),
        mark_count=len(mark_records),
        renderer=renderer,
        accessibility=a11y,
        assets=assets,
        export=parsed.export,
        warnings=tuple(warnings),
        limits={
            "max_rows": MAX_ROWS,
            "max_fields": MAX_FIELDS,
            "max_transforms": MAX_TRANSFORMS,
            "max_facets": MAX_FACETS,
            "max_marks": MAX_MARKS,
            "max_labels": MAX_LABELS,
            "max_payload_bytes": MAX_PAYLOAD_BYTES,
            "max_export_px": MAX_EXPORT_PX,
            "canvas_mark_threshold": CANVAS_MARK_THRESHOLD,
        },
        theme=parsed.theme,
        interaction=parsed.interaction,
        layout=layout,
        transformed_rows=tuple(redacted_rows),
    )


def beginner_to_spec(
    *,
    kind: str,
    data: Sequence[Mapping[str, object]],
    x: str,
    y: str,
    title: str,
    description: str,
    color: str | None = None,
) -> ChartSpec:
    """Compile beginner Line/Area/Bar/Scatter signatures into ChartSpec."""
    mark_type = {
        "line": "line",
        "area": "area",
        "bar": "bar",
        "scatter": "point",
    }.get(kind)
    if mark_type is None:
        raise _chart_error(
            "HED-CHART-0024",
            "Unsupported beginner chart kind",
            f"kind {kind!r} is not a beginner chart.",
            "Use line, area, bar, or scatter.",
        )
    encodings: dict[str, Encoding] = {
        "x": Encoding(field=x, type="string" if kind == "bar" else "number"),
        "y": Encoding(field=y, type="number"),
    }
    if color:
        encodings["color"] = Encoding(field=color, type="string")
    fields = [
        FieldDef(name=x, type="string" if kind == "bar" else "number"),
        FieldDef(name=y, type="number"),
    ]
    if color:
        fields.append(FieldDef(name=color, type="string"))
    rows = tuple(dict(r) for r in data)
    return ChartSpec(
        data=DataRef(rows=rows, fields=tuple(fields)),
        marks=(MarkDef(type=mark_type, encodings=encodings),),
        accessibility=AccessibilityDef(title=title, description=description),
        export=ExportPolicy(),
        theme=ThemeDef(),
        interaction=InteractionDef(),
    )
