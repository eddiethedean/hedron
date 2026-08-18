"""Normalize handler annotations into TypeSchema + binding plans."""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import (
    Annotated,
    Any,
    Literal,
    TypeGuard,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)
from uuid import UUID

from pydantic import BaseModel, SecretStr
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from hedron.type_authoring.adapter import PydanticBindingAdapter
from hedron.type_authoring.markers import FormBody, Refreshes, Updates, ViewParams
from hedron.type_authoring.outcomes import OutcomeMap
from hedron_core.binding_plan import BoundaryBindingPlan
from hedron_core.codes import (
    HED_TYPE_0002,
    HED_TYPE_0003,
    HED_TYPE_0004,
    HED_TYPE_0005,
    HED_TYPE_0010,
)
from hedron_core.component import Component
from hedron_core.diagnostics import error
from hedron_core.field import hedron_meta
from hedron_core.schema_sanitizer import projections_from_model
from hedron_core.security import Secret, TrustedHtml
from hedron_core.type_schema import (
    MAX_MODEL_FIELDS,
    MAX_SCHEMA_DEPTH,
    MAX_UNION_VARIANTS,
    InstanceKey,
    Sensitive,
    TypeSchema,
    stable_fingerprint,
)
from hedron_core.typing_aliases import JsonObject, JsonValue
from hedron_core.updates import BindingPlan

__all__ = ["CompiledTypeHandler", "TypeNormalizer", "inspect_handler"]

_PATH_PARAM_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def _is_union(origin: object) -> bool:
    return origin is Union or str(origin) in {"typing.Union", "types.UnionType"}


@dataclass(frozen=True, slots=True)
class FieldRecord:
    name: str
    path: str
    annotation: object
    required: bool
    default: object
    location: str
    alias: str | None
    http_name: str
    disposition: str
    sensitive: bool
    identity: bool
    control_kind: str | None
    is_file: bool = False


@dataclass
class CompiledTypeHandler:
    modeled: bool
    kind: str
    param_name: str | None
    model_type: type[BaseModel] | None
    source: ViewParams | FormBody | None
    fields: tuple[FieldRecord, ...]
    binding_plan: BindingPlan
    injected_names: frozenset[str]
    declared_refresh_ids: tuple[str, ...]
    declared_update_ids: tuple[str, ...]
    outcomes: OutcomeMap[Any] | None
    adapter: PydanticBindingAdapter | None
    schema: TypeSchema | None
    form_encoding: str | None = None
    fastapi_parameters: tuple[inspect.Parameter, ...] = ()
    original: Callable[..., Any] | None = None
    boundary_plan: BoundaryBindingPlan | None = None

    def reconstruct(self, values: Mapping[str, object]) -> BaseModel:
        if self.adapter is None or self.model_type is None:
            raise error(
                HED_TYPE_0003,
                title="Handler is not modeled",
                explanation="Cannot reconstruct a boundary model for an unmodeled handler.",
                remediation="Mark a ViewParams or FormBody parameter.",
            )
        return self.adapter.validate(values)


class TypeNormalizer:
    """Single TypeSchema consumer path: inspect trusted imported handlers only."""

    def inspect(
        self,
        fn: Callable[..., Any],
        *,
        kind: str,
        path: str | None = None,
        handler_name: str = "",
        fallback: str | None = None,
        outcomes: OutcomeMap[Any] | None = None,
    ) -> CompiledTypeHandler:
        hints = _safe_hints(fn)
        signature = inspect.signature(fn)
        injected = _injected_names(signature, hints)
        view_hits: list[tuple[str, type[BaseModel], ViewParams]] = []
        form_hits: list[tuple[str, type[BaseModel], FormBody]] = []
        extra_plain: list[str] = []
        for name, parameter in signature.parameters.items():
            annotation = hints.get(name, parameter.annotation)
            base, metadata = _split_annotated(annotation)
            sources = [item for item in metadata if isinstance(item, (ViewParams, FormBody))]
            if len(sources) > 1:
                raise error(
                    HED_TYPE_0002,
                    title="Conflicting Hedron source markers",
                    explanation=f"Parameter {name!r} carries more than one source marker.",
                    remediation="Keep ViewParams and FormBody on distinct parameters.",
                )
            if not sources:
                if name not in injected and parameter.kind not in {
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                }:
                    extra_plain.append(name)
                continue
            if not _is_model(base):
                raise error(
                    HED_TYPE_0003,
                    title="Source marker on a non-model type",
                    explanation=f"Parameter {name!r} must be a Pydantic BaseModel.",
                    remediation="Annotate a BaseModel (or Hedron Model/FormModel) subclass.",
                )
            marker = sources[0]
            if isinstance(marker, ViewParams):
                if kind != "view":
                    raise error(
                        HED_TYPE_0002,
                        title="ViewParams on a command",
                        explanation="ViewParams is only valid on refreshable handlers.",
                        remediation="Use FormBody for command input.",
                    )
                view_hits.append((name, base, marker))
            else:
                if kind != "command":
                    raise error(
                        HED_TYPE_0002,
                        title="FormBody on a view",
                        explanation="FormBody is only valid on command handlers.",
                        remediation="Use ViewParams for refreshable bind models.",
                    )
                form_hits.append((name, base, marker))
        if len(view_hits) > 1 or len(form_hits) > 1:
            raise error(
                HED_TYPE_0002,
                title="Duplicate boundary parameter",
                explanation="A handler may have at most one ViewParams and one FormBody.",
                remediation="Collapse extra boundary models.",
            )
        if (view_hits or form_hits) and extra_plain:
            raise error(
                HED_TYPE_0002,
                title="Bindable parameter outside the boundary model",
                explanation=(
                    f"Parameters {extra_plain} are not injected and not part of the marked model."
                ),
                remediation="Move those fields onto the ViewParams/FormBody model.",
            )
        refreshes, updates = _return_effects(hints.get("return", signature.return_annotation))
        class_refresh, class_update = _class_effect_ids(fn)
        if (
            not view_hits
            and not form_hits
            and not refreshes
            and not updates
            and outcomes is None
            and not class_refresh
            and not class_update
        ):
            return CompiledTypeHandler(
                modeled=False,
                kind=kind,
                param_name=None,
                model_type=None,
                source=None,
                fields=(),
                binding_plan=BindingPlan(),
                injected_names=injected,
                declared_refresh_ids=tuple(
                    getattr(refreshes, "target_ids", ()) if refreshes else ()
                ),
                declared_update_ids=tuple(getattr(updates, "target_ids", ()) if updates else ()),
                outcomes=outcomes,
                adapter=None,
                schema=None,
                original=fn,
            )
        hit = view_hits[0] if view_hits else (form_hits[0] if form_hits else None)
        model_type = hit[1] if hit else None
        source = hit[2] if hit else None
        param_name = hit[0] if hit else None
        path_names = tuple(_PATH_PARAM_RE.findall(path or ""))
        fields: tuple[FieldRecord, ...] = ()
        disposition: dict[str, str] = {}
        sensitive: list[str] = []
        identity: list[str] = []
        encoding: str | None = None
        if model_type is not None:
            fields, disposition, sensitive, identity = _walk_model(
                model_type,
                source=source,
                path_names=path_names,
            )
            if isinstance(source, FormBody):
                encoding = _resolve_encoding(source, fields)
            plan = _plan_from_fields(fields)
            for record in fields:
                if record.sensitive and record.location in {"path", "query"}:
                    raise error(
                        HED_TYPE_0010,
                        title="Sensitive value cannot enter a public URL",
                        explanation=(
                            f"Field {record.path!r} is Sensitive and would be "
                            f"{record.location}-bound."
                        ),
                        remediation="Keep secrets on dependencies, not ViewParams URL fields.",
                    )
        else:
            plan = BindingPlan()
        adapter = None
        schema = None
        if model_type is not None:
            adapter = PydanticBindingAdapter(
                model_type,
                injected_names=injected,
                identity_fields=tuple(identity),
                sensitive_fields=tuple(sensitive),
            )
        declared_refresh = tuple(getattr(refreshes, "target_ids", ()) if refreshes else ()) + (
            class_refresh
        )
        declared_update = tuple(getattr(updates, "target_ids", ()) if updates else ()) + (
            class_update
        )
        effect: str = "declared" if (declared_refresh or declared_update) else "dynamic"
        if outcomes is not None:
            outcomes.validate_union(hints.get("return", signature.return_annotation))
        if model_type is not None or effect == "declared" or outcomes is not None:
            field_paths: list[Mapping[str, JsonValue]] = [
                {
                    "path": item.path,
                    "name": item.name,
                    "alias": item.alias,
                    "required": item.required,
                    "location": item.location,
                    "disposition": item.disposition,
                    "sensitive": item.sensitive,
                    "identity": item.identity,
                    "control_kind": item.control_kind,
                }
                for item in fields
            ]
            input_proj, output_proj, shared, write_only, read_only = projections_from_model(
                model_type,
                sensitive=tuple(sensitive),
            )
            schema = TypeSchema(
                handler_fingerprint=stable_fingerprint(
                    {
                        "name": handler_name or getattr(fn, "__name__", ""),
                        "qualname": getattr(fn, "__qualname__", ""),
                        "module": getattr(fn, "__module__", ""),
                    }
                ),
                model_fingerprint=stable_fingerprint(
                    _model_config(model_type) if model_type else {}
                ),
                handler_kind="command" if kind == "command" else "view",
                boundary_sources=tuple(
                    name
                    for name in (
                        "ViewParams" if view_hits else None,
                        "FormBody" if form_hits else None,
                    )
                    if name
                ),
                field_paths=tuple(field_paths),
                control_dispositions=disposition,
                sensitivity_flags=tuple(sensitive),
                identity_flags=tuple(identity),
                effect_knowledge="declared" if effect == "declared" else "dynamic",
                declared_target_ids=declared_refresh + declared_update,
                outcome_variant_ids=outcomes.variant_ids if outcomes else (),
                fallback_cache_projection={"fallback": fallback} if fallback else {},
                input_projection=input_proj,
                output_projection=output_proj,
                shared_fields=shared,
                write_only_fields=write_only,
                read_only_fields=read_only,
            )
        return CompiledTypeHandler(
            modeled=model_type is not None,
            kind=kind,
            param_name=param_name,
            model_type=model_type,
            source=source,
            fields=fields,
            binding_plan=plan,
            injected_names=injected,
            declared_refresh_ids=declared_refresh,
            declared_update_ids=declared_update,
            outcomes=outcomes,
            adapter=adapter,
            schema=schema,
            form_encoding=encoding,
            original=fn,
        )


def inspect_handler(
    fn: Callable[..., Any],
    *,
    kind: str,
    path: str | None = None,
    handler_name: str = "",
    fallback: str | None = None,
    outcomes: OutcomeMap[Any] | None = None,
) -> CompiledTypeHandler:
    return TypeNormalizer().inspect(
        fn,
        kind=kind,
        path=path,
        handler_name=handler_name,
        fallback=fallback,
        outcomes=outcomes,
    )


def _safe_hints(fn: Callable[..., Any]) -> dict[str, Any]:
    namespace: dict[str, Any] = dict(fn.__globals__)
    if fn.__closure__:
        for name, cell in zip(fn.__code__.co_freevars, fn.__closure__, strict=True):
            try:
                namespace[name] = cell.cell_contents
            except ValueError:
                continue
    frame = inspect.currentframe()
    depth = 0
    while frame is not None and depth < 16:
        namespace.update(frame.f_locals)
        frame = frame.f_back
        depth += 1
    try:
        return get_type_hints(fn, globalns=namespace, localns=namespace, include_extras=True)
    except Exception:  # noqa: BLE001
        try:
            return get_type_hints(fn, include_extras=True)
        except Exception:  # noqa: BLE001
            return dict(getattr(fn, "__annotations__", {}) or {})


def _split_annotated(annotation: object) -> tuple[object, tuple[object, ...]]:
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        return args[0], tuple(args[1:])
    return annotation, ()


def _is_model(annotation: object) -> TypeGuard[type[BaseModel]]:
    return isinstance(annotation, type) and issubclass(annotation, BaseModel)


def _injected_names(signature: inspect.Signature, hints: Mapping[str, Any]) -> frozenset[str]:
    names: set[str] = set()
    from fastapi.params import Depends as DependsParam
    from starlette.requests import Request

    for name, parameter in signature.parameters.items():
        if name in {"request", "websocket", "self", "cls"}:
            names.add(name)
            continue
        annotation = hints.get(name, parameter.annotation)
        if annotation is Request or (
            isinstance(annotation, type) and issubclass(annotation, Request)
        ):
            names.add(name)
            continue
        if isinstance(parameter.default, DependsParam):
            names.add(name)
            continue
        from hedron.type_authoring.depends import DependsOn

        if isinstance(parameter.default, DependsOn):
            names.add(name)
            continue
        _, metadata = _split_annotated(annotation)
        if any(isinstance(item, DependsParam) for item in metadata):
            names.add(name)
            continue
        if any(type(item).__name__ == "DependsOn" for item in metadata):
            names.add(name)
    return frozenset(names)


def _return_effects(annotation: object) -> tuple[Refreshes | None, Updates | None]:
    _, metadata = _split_annotated(annotation)
    refreshes = [item for item in metadata if isinstance(item, Refreshes)]
    updates = [item for item in metadata if isinstance(item, Updates)]
    if len(refreshes) > 1 or len(updates) > 1:
        raise error(
            HED_TYPE_0002,
            title="Duplicate effect markers",
            explanation="A command may declare at most one Refreshes and one Updates.",
            remediation="Collapse duplicate effect annotations.",
        )
    return (refreshes[0] if refreshes else None, updates[0] if updates else None)


def _class_effect_ids(fn: Callable[..., Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    extra = getattr(fn, "__hedron_effects__", None)
    if extra is None:
        return (), ()
    items = extra if isinstance(extra, (tuple, list)) else (extra,)
    refresh_ids: list[str] = []
    update_ids: list[str] = []
    for item in items:
        ids = tuple(getattr(item, "target_ids", ()) or ())
        if isinstance(item, Updates):
            update_ids.extend(ids)
        else:
            refresh_ids.extend(ids)
    return tuple(refresh_ids), tuple(update_ids)


def _walk_model(
    model_type: type[BaseModel],
    *,
    source: ViewParams | FormBody | None,
    path_names: Sequence[str],
    prefix: str = "",
    depth: int = 0,
    seen: set[int] | None = None,
) -> tuple[tuple[FieldRecord, ...], dict[str, str], list[str], list[str]]:
    if depth > MAX_SCHEMA_DEPTH:
        raise error(
            HED_TYPE_0004,
            title="TypeSchema depth limit exceeded",
            explanation=f"Nested models exceeded {MAX_SCHEMA_DEPTH} levels.",
            remediation="Flatten the boundary model.",
        )
    seen = set() if seen is None else seen
    ident = id(model_type)
    if ident in seen:
        raise error(
            HED_TYPE_0005,
            title="Recursive model rejected",
            explanation="Recursive models cannot be used as form/bind boundaries.",
            remediation="Break the cycle or mark the field override-only with an explicit control.",
        )
    seen.add(ident)
    records: list[FieldRecord] = []
    disposition: dict[str, str] = {}
    sensitive: list[str] = []
    identity: list[str] = []
    aliases: dict[str, str] = {}
    for name, info in model_type.model_fields.items():
        path = f"{prefix}{name}"
        annotation = info.annotation
        field_sensitive, field_identity, control = _field_markers(info)
        disp, is_file = _inventory_disposition(annotation, depth=depth)
        if len(records) >= MAX_MODEL_FIELDS:
            raise error(
                HED_TYPE_0004,
                title="TypeSchema field limit exceeded",
                explanation=f"More than {MAX_MODEL_FIELDS} fields.",
                remediation="Split the model.",
            )
        variants = _union_count(annotation)
        if variants > MAX_UNION_VARIANTS:
            raise error(
                HED_TYPE_0004,
                title="Union variant limit exceeded",
                explanation=f"Field {path!r} has {variants} variants; max is {MAX_UNION_VARIANTS}.",
                remediation="Narrow the union.",
            )
        if field_sensitive and field_identity:
            raise error(
                HED_TYPE_0010,
                title="Sensitive field cannot be an InstanceKey",
                explanation=f"Field {path!r} cannot be both Sensitive and InstanceKey.",
                remediation="Choose redaction or identity, not both.",
            )
        location = _location_for(name, info, source, path_names)
        alias = info.alias if info.alias and info.alias != name else None
        http_name = _http_name(name, alias, location, path_names)
        route_name = alias or name
        if route_name in aliases and aliases[route_name] != path:
            raise error(
                HED_TYPE_0003,
                title="Ambiguous field alias",
                explanation=(
                    f"Alias {route_name!r} maps to both {aliases[route_name]!r} and {path!r}."
                ),
                remediation="Use distinct aliases for path/query/form names.",
            )
        aliases[route_name] = path
        if field_sensitive:
            sensitive.append(path)
        if field_identity:
            identity.append(path)
        if disp == "rejected" and source is not None:
            raise error(
                HED_TYPE_0005,
                title="Rejected field shape",
                explanation=f"Field {path!r} is not in the 0.44 form/bind inventory.",
                remediation="Remove the field or provide an explicit full-form override.",
            )
        required = info.is_required()
        if not required and info.default is not PydanticUndefined:
            default = info.default
        else:
            default = inspect.Parameter.empty
        kind = getattr(control, "kind", None) if control is not None else None
        records.append(
            FieldRecord(
                name=name,
                path=path,
                annotation=annotation,
                required=required,
                default=default,
                location=location,
                alias=alias,
                http_name=http_name,
                disposition=disp,
                sensitive=field_sensitive,
                identity=field_identity,
                control_kind=kind,
                is_file=is_file,
            )
        )
        disposition[path] = disp
        nested = _nested_model_type(annotation)
        if nested is not None:
            _, _, nested_sensitive, nested_identity = _walk_model(
                nested,
                source=None,
                path_names=(),
                prefix=f"{path}.",
                depth=depth + 1,
                seen=seen,
            )
            sensitive.extend(nested_sensitive)
            identity.extend(nested_identity)
    return tuple(records), disposition, sensitive, identity


def _nested_model_type(annotation: object) -> type[BaseModel] | None:
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        if args:
            return _nested_model_type(args[0])
        return None
    if _is_model(annotation):
        return annotation
    if _is_union(origin) or str(type(annotation)) == "<class 'types.UnionType'>":
        for item in get_args(annotation):
            if item is not type(None) and _is_model(item):
                return item
    return None


def _field_markers(info: FieldInfo) -> tuple[bool, bool, object]:
    from hedron.type_authoring.markers import Control

    metadata = tuple(info.metadata or ())
    sensitive = any(isinstance(item, Sensitive) for item in metadata)
    identity = any(isinstance(item, InstanceKey) and item.include for item in metadata)
    controls = [item for item in metadata if isinstance(item, Control)]
    control = controls[0] if controls else None
    meta = hedron_meta(info)
    if meta.get("secret") is True:
        sensitive = True
    if meta.get("identity") is True:
        identity = True
    if meta.get("secret") is True and meta.get("identity") is True:
        raise error(
            HED_TYPE_0010,
            title="Field secret and identity contradiction",
            explanation="Field(secret=True) cannot also be identity=True.",
            remediation="Remove one of the contradictory Field flags.",
        )
    return sensitive, identity, control


def _location_for(
    name: str,
    info: FieldInfo,
    source: ViewParams | FormBody | None,
    path_names: Sequence[str],
) -> str:
    if isinstance(source, FormBody):
        return "form"
    # Path placeholders own the field when either the Python name or alias
    # matches. Prefer the Python name so Path() params stay aligned with the
    # route template (Field.alias is not a second path segment).
    matched_path = name in path_names or (info.alias is not None and info.alias in path_names)
    if (
        not path_names
        and isinstance(source, ViewParams)
        and source.source != "query"
        and info.is_required()
        and source.source in {"path", "path_query"}
    ):
        return "path"
    if matched_path:
        if isinstance(source, ViewParams) and source.source == "query":
            raise error(
                HED_TYPE_0003,
                title="Path field forbidden by ViewParams.source",
                explanation=f"Field {name!r} matches a path placeholder but source='query'.",
                remediation="Rename the field or use source='path_query'.",
            )
        return "path"
    if isinstance(source, ViewParams) and source.source == "path":
        raise error(
            HED_TYPE_0003,
            title="Query field forbidden by ViewParams.source",
            explanation=f"Field {name!r} would bind as query while source='path'.",
            remediation="Add a path placeholder or use source='path_query'.",
        )
    return "query"


def _http_name(
    name: str,
    alias: str | None,
    location: str,
    path_names: Sequence[str],
) -> str:
    """Public HTTP name: path placeholders, otherwise Field.alias or the field name."""
    if location == "path":
        if name in path_names:
            return name
        if alias is not None and alias in path_names:
            return alias
        return name
    return alias or name


def _plan_from_fields(fields: Sequence[FieldRecord]) -> BindingPlan:
    path_params = tuple(item.http_name for item in fields if item.location == "path")
    query_params = tuple(item.http_name for item in fields if item.location == "query")
    required = tuple(
        item.http_name for item in fields if item.required and item.location in {"path", "query"}
    )
    return BindingPlan(path_params=path_params, query_params=query_params, required=required)


def _resolve_encoding(source: FormBody, fields: Sequence[FieldRecord]) -> str:
    has_file = any(item.is_file for item in fields)
    if source.encoding == "urlencoded" and has_file:
        raise error(
            HED_TYPE_0005,
            title="File fields require multipart encoding",
            explanation="FormBody(encoding='urlencoded') cannot carry file fields.",
            remediation="Use encoding='multipart' or encoding='auto'.",
        )
    if source.encoding == "auto":
        return "multipart" if has_file else "urlencoded"
    return source.encoding


def _union_count(annotation: object) -> int:
    origin = get_origin(annotation)
    if _is_union(origin) or isinstance(annotation, type(int | str)):
        args = [item for item in get_args(annotation) if item is not type(None)]
        return len(args)
    return 0


def _inventory_disposition(annotation: object, *, depth: int) -> tuple[str, bool]:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is Annotated:
        return _inventory_disposition(args[0], depth=depth)
    if annotation is Any:
        return "rejected", False
    if annotation is dict or origin is dict:
        return "rejected", False
    if _is_union(origin) or str(type(annotation)) == "<class 'types.UnionType'>":
        non_none = [item for item in args if item is not type(None)]
        if any(getattr(item, "discriminator", None) for item in (origin,) if False):
            return "override_only", False
        if any(isinstance(item, type) and issubclass(item, BaseModel) for item in non_none):
            if len(non_none) > 1:
                return "override_only", False
            return _inventory_disposition(non_none[0], depth=depth)
        if len(non_none) == 1:
            return _inventory_disposition(non_none[0], depth=depth)
        if all(_is_supported_scalar(item) for item in non_none):
            return "supported", False
        return "override_only", False
    if origin is list or origin is set or origin is tuple:
        inner = args[0] if args else Any
        if _is_model(inner):
            return "override_only", False
        disp, is_file = _inventory_disposition(inner, depth=depth)
        return disp, is_file
    if origin is Literal:
        return "supported", False
    if _is_supported_scalar(annotation):
        return "supported", False
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return "supported", False
    if isinstance(annotation, type) and issubclass(annotation, (Secret, SecretStr)):
        return "supported", False
    if _is_upload(annotation):
        return "supported", True
    if isinstance(annotation, type) and issubclass(annotation, TrustedHtml):
        return "rejected", False
    if isinstance(annotation, type) and issubclass(annotation, Component):
        return "rejected", False
    if callable(annotation) and not isinstance(annotation, type):
        return "rejected", False
    if _is_model(annotation):
        return "override_only", False
    return "rejected", False


_SCALARS: frozenset[type[Any]] = frozenset(
    {str, int, float, bool, Decimal, date, time, datetime, UUID}
)


def _is_supported_scalar(annotation: object) -> bool:
    return isinstance(annotation, type) and annotation in _SCALARS


def _is_upload(annotation: object) -> bool:
    name = getattr(annotation, "__name__", "")
    return name in {"UploadFile", "FileUpload"}


def _model_config(model_type: type[BaseModel]) -> JsonObject:
    fields: dict[str, JsonValue] = {}
    for name, info in model_type.model_fields.items():
        fields[name] = {
            "annotation": str(info.annotation),
            "required": info.is_required(),
            "alias": info.alias,
        }
    config = getattr(model_type, "model_config", {}) or {}
    return {
        "qualname": getattr(model_type, "__qualname__", model_type.__name__),
        "extra": str(config.get("extra", "")),
        "fields": fields,
    }
