"""Typed boundaries for reflection APIs whose standard stubs return ``Any``."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Mapping, Sequence
from typing import Protocol, cast, get_args, get_origin


class _ParameterValue(Protocol):
    annotation: object
    default: object


class _SignatureValue(Protocol):
    return_annotation: object


class _ClosureCellValue(Protocol):
    cell_contents: object


class _FieldDefault(Protocol):
    default: object


class _FieldAnnotation(Protocol):
    annotation: object


class _FieldMetadata(Protocol):
    metadata: Sequence[object] | None


class _ModelWithConfig(Protocol):
    model_config: Mapping[str, object]


class _ModelWithFields(Protocol):
    model_fields: Mapping[str, object]


class _TypeGetattribute(Protocol):
    def __call__(self, instance: type[object], name: str) -> object: ...


class _ModelWithDynamicFields(Protocol):
    def __getattr__(self, name: str) -> object: ...


class _FieldTitle(Protocol):
    title: object


class _RequiredField(Protocol):
    def is_required(self) -> bool: ...


class _TypeHintResolver(Protocol):
    def __call__(
        self,
        target: object,
        *,
        globalns: Mapping[str, object] | None = None,
        localns: Mapping[str, object] | None = None,
        include_extras: bool = False,
    ) -> dict[str, object]: ...


class _AwaitablePredicate(Protocol):
    def __call__(self, value: object, /) -> bool: ...


class _TypeOriginResolver(Protocol):
    def __call__(self, annotation: object, /) -> object: ...


class _ModelValidator(Protocol):
    @classmethod
    def model_validate(cls, value: object) -> object: ...


class _ModelDumper(Protocol):
    def model_dump(
        self,
        *,
        mode: str = "python",
        exclude_none: bool = False,
    ) -> dict[str, object]: ...


class _ObjectValidator(Protocol):
    def validate_python(self, value: object) -> object: ...


class _TypeAdapterFactory(Protocol):
    def __call__(self, target: object) -> _ObjectValidator: ...


class _AnnotatedFactory(Protocol):
    def __getitem__(self, item: tuple[object, ...]) -> object: ...


class _AstLiteralEvaluator(Protocol):
    def __call__(self, node: object, /) -> object: ...


class _DataclassDictConverter(Protocol):
    def __call__(self, instance: object, /) -> dict[str, object]: ...


class _ModuleGlobals(Protocol):
    def __call__(self) -> Mapping[str, object]: ...


class _SocketNameReader(Protocol):
    def getsockname(self) -> tuple[object, ...]: ...


class _ObjectNamespace(Protocol):
    def __getattribute__(self, name: str) -> object: ...


class _ObjectGetter(Protocol):
    def get(self, key: str, default: object = None) -> object: ...


class _ObjectContainer(Protocol):
    def __contains__(self, key: object, /) -> bool: ...


class _DynamicCaller(Protocol):
    def __call__(self, *args: object, **kwargs: object) -> object: ...


def parameter_annotation(parameter: object) -> object:
    """Read ``inspect.Parameter.annotation`` as an untrusted object."""
    return cast(_ParameterValue, parameter).annotation


def parameter_default(parameter: object) -> object:
    """Read ``inspect.Parameter.default`` as an untrusted object."""
    return cast(_ParameterValue, parameter).default


def resolved_type_hints(target: object, *, include_extras: bool = False) -> Mapping[str, object]:
    """Resolve annotations without exposing ``typing.get_type_hints``' Any values."""
    from typing import get_type_hints

    resolver = cast(_TypeHintResolver, get_type_hints)
    return resolver(target, include_extras=include_extras)


def awaitable_value(value: object) -> Awaitable[object] | None:
    """Narrow a dynamic callback result to an awaitable object when applicable."""
    is_awaitable = cast(_AwaitablePredicate, inspect.isawaitable)
    if is_awaitable(value):
        return cast(Awaitable[object], value)
    return None


def signature_return_annotation(signature: object) -> object:
    """Read ``inspect.Signature.return_annotation`` as an object."""
    return cast(_SignatureValue, signature).return_annotation


def closure_cell_value(cell: object) -> object:
    """Read a closure cell's dynamic contents without propagating ``Any``."""
    return cast(_ClosureCellValue, cell).cell_contents


def field_default(field_info: object) -> object:
    """Read Pydantic's dynamically typed ``FieldInfo.default`` as an object."""
    return cast(_FieldDefault, field_info).default


def field_annotation(field_info: object) -> object:
    """Read Pydantic's field annotation without propagating a dynamic type."""
    return cast(_FieldAnnotation, field_info).annotation


def field_metadata(field_info: object) -> tuple[object, ...]:
    """Read Pydantic's dynamically typed ``FieldInfo.metadata`` as objects."""
    return tuple(cast(_FieldMetadata, field_info).metadata or ())


def model_config(model_type: object) -> Mapping[str, object]:
    """Read a Pydantic model config through its object-valued mapping surface."""
    return cast(_ModelWithConfig, model_type).model_config


def model_fields(model_type: object) -> Mapping[str, object]:
    """Read Pydantic model fields as object-valued entries."""
    return cast(_ModelWithFields, model_type).model_fields


def class_namespace(class_type: object) -> Mapping[str, object]:
    """Read a class namespace as object-valued entries."""
    get_type_attribute = cast(_TypeGetattribute, type.__getattribute__)
    namespace = get_type_attribute(cast(type[object], class_type), "__dict__")
    return cast(Mapping[str, object], namespace)


def model_field_value(instance: object, name: str, default: object = None) -> object:
    """Read a dynamic Pydantic field while preserving the supplied fallback."""
    try:
        return cast(_ModelWithDynamicFields, instance).__getattr__(name)
    except AttributeError:
        return default


def field_title(field_info: object) -> str | None:
    """Return a Pydantic field title when one is declared."""
    title = cast(_FieldTitle, field_info).title
    return title if isinstance(title, str) else None


def field_is_required(field_info: object) -> bool:
    """Query a Pydantic field's required status through its typed method."""
    return cast(_RequiredField, field_info).is_required()


def dynamic_attribute(value: object, name: str, default: object = None) -> object:
    """Read an optional dynamic attribute as ``object`` instead of ``Any``."""
    try:
        return cast(object, getattr(value, name))
    except AttributeError:
        return default


def set_dynamic_attribute(value: object, name: str, attribute: object) -> None:
    """Set a dynamic framework attribute without a broad ``Any`` target."""
    setattr(value, name, attribute)


def type_arguments(annotation: object) -> tuple[object, ...]:
    """Return typing arguments as objects instead of the typeshed ``Any`` tuple."""
    return cast(tuple[object, ...], get_args(annotation))


def type_origin(annotation: object) -> object:
    """Return a typing origin as an object instead of the typeshed ``Any`` value."""
    resolver = cast(_TypeOriginResolver, get_origin)
    return resolver(annotation)


def validate_model(model_type: object, value: object) -> object:
    """Validate data through Pydantic without leaking its dynamic return type."""
    return cast(_ModelValidator, model_type).model_validate(value)


def dump_model(
    instance: object,
    *,
    mode: str = "python",
    exclude_none: bool = False,
) -> dict[str, object]:
    """Dump a Pydantic model through an object-valued mapping surface."""
    return cast(_ModelDumper, instance).model_dump(mode=mode, exclude_none=exclude_none)


def validate_value(annotation: object, value: object) -> object:
    """Validate a value with Pydantic while exposing only an object result."""
    from pydantic import TypeAdapter

    adapter_factory = cast(_TypeAdapterFactory, cast(object, TypeAdapter))
    return adapter_factory(annotation).validate_python(value)


def annotated_type(base: object, *metadata: object) -> object:
    """Build a runtime Annotated type without treating its dynamic base as a type alias."""
    from typing import Annotated

    factory = cast(_AnnotatedFactory, cast(object, Annotated))
    return factory[(base, *metadata)]


def ast_literal_value(node: object) -> object:
    """Evaluate an AST literal without exposing ``ast.literal_eval``'s Any result."""
    from ast import literal_eval

    evaluator = cast(_AstLiteralEvaluator, literal_eval)
    return evaluator(node)


def dataclass_values(instance: object) -> dict[str, object]:
    """Convert a dataclass to an object-valued mapping."""
    from dataclasses import asdict

    converter = cast(_DataclassDictConverter, asdict)
    return converter(instance)


def module_globals() -> Mapping[str, object]:
    """Expose the current module globals through an object-valued mapping."""
    values = cast(_ModuleGlobals, globals)
    return values()


def bound_socket_port(sock: object) -> int:
    """Read a bound TCP port without inheriting ``socket.getsockname`` Any."""
    address = cast(_SocketNameReader, sock).getsockname()
    port = address[1]
    if isinstance(port, int) and not isinstance(port, bool):
        return port
    raise OSError("socket did not report an integer port")


def object_namespace(value: object) -> Mapping[str, object]:
    """Expose an instance namespace with object-valued entries."""
    namespace = cast(_ObjectNamespace, value).__getattribute__("__dict__")
    return cast(Mapping[str, object], namespace)


def object_get(value: object, key: str, default: object = None) -> object:
    """Read a string-keyed dynamic mapping through an object-valued ``get``."""
    return cast(_ObjectGetter, value).get(key, default)


def object_contains(value: object, key: object) -> bool:
    """Check membership on a dynamic container without its Any return surface."""
    return cast(_ObjectContainer, value).__contains__(key)


def call_dynamic(
    callback: object,
    *args: object,
    **kwargs: object,
) -> object:
    """Call a framework callback without leaking its dynamic return annotation."""
    return cast(_DynamicCaller, callback)(*args, **kwargs)
