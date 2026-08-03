"""Component base and NodeLike protocol."""

from __future__ import annotations

from typing import Any, ClassVar, Protocol, TypeVar, runtime_checkable

from pydantic import ValidationError

from hedron_core.diagnostics import error
from hedron_core.field import hedron_meta
from hedron_core.identifiers import component_type_id, instance_id
from hedron_core.models import Props
from hedron_core.security import Secret, redact_value

PropsT = TypeVar("PropsT", bound=Props)


@runtime_checkable
class ComponentNode(Protocol):
    """Opaque protocol implemented by components and native HTML nodes."""

    def __hedron_node__(self) -> Any: ...


NodeLike = Any


class Component[PropsT: Props]:
    """Base class for reusable server-rendered UI components."""

    props_type: ClassVar[type[Props]]
    logical_name: ClassVar[str | None] = None
    distribution: ClassVar[str] = "hedron-core"
    slots: ClassVar[dict[str, str]] = {}  # name -> cardinality: required|optional|many

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Infer props_type from Generic base if not set.
        if not hasattr(cls, "props_type") or cls.props_type is Component.__dict__.get(
            "props_type", None
        ):
            for base in getattr(cls, "__orig_bases__", ()):
                args = getattr(base, "__args__", ())
                if args and isinstance(args[0], type) and issubclass(args[0], Props):
                    cls.props_type = args[0]
                    break
            else:
                # Allow components with empty props via _EmptyProps
                pass
        if getattr(cls, "logical_name", None) is None:
            cls.logical_name = cls.__name__

    def __init__(self, props: PropsT | None = None, /, **kwargs: Any) -> None:
        props_cls = getattr(self.__class__, "props_type", None)
        if props_cls is None:
            raise error(
                "HED-RENDER-0002",
                title="Missing props type",
                explanation=f"{self.__class__.__name__} did not declare a Props type.",
                remediation="Subclass Component[YourProps] with a Props model.",
            )
        try:
            if props is not None and kwargs:
                raise error(
                    "HED-RENDER-0003",
                    title="Invalid component construction",
                    explanation="Pass either a Props instance or keyword fields, not both.",
                )
            if props is not None:
                if not isinstance(props, props_cls):
                    raise TypeError(f"Expected {props_cls.__name__}, got {type(props).__name__}")
                self._props: PropsT = props
            else:
                self._props = props_cls(**kwargs)  # type: ignore[assignment]
        except ValidationError as exc:
            raise error(
                "HED-MODEL-0004",
                title="Invalid component props",
                explanation=str(exc),
                remediation="Correct the props to match the declared Props model.",
                component_id=self.logical_id(),
            ) from exc
        self._children: tuple[Any, ...] = ()
        self._slot_values: dict[str, Any] = {}
        self._key: str | None = None

    @property
    def props(self) -> PropsT:
        return self._props

    def key(self, value: str) -> Component[PropsT]:
        object.__setattr__(self, "_key", value) if False else None
        self._key = value
        return self

    def children(self, *nodes: Any) -> Component[PropsT]:
        self._children = nodes
        return self

    def slot(self, name: str, value: Any) -> Component[PropsT]:
        cardinality = self.slots.get(name)
        if cardinality is None and self.slots:
            raise error(
                "HED-RENDER-0004",
                title="Unknown slot",
                explanation=f"Slot {name!r} is not declared on {self.__class__.__name__}.",
                remediation=f"Declared slots: {sorted(self.slots)}",
                component_id=self.logical_id(),
            )
        self._slot_values[name] = value
        return self

    def logical_id(self) -> str:
        module = self.__class__.__module__
        name = self.logical_name or self.__class__.__name__
        return component_type_id(self.distribution, module, name)

    def identity_fields(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for fname, finfo in self.props.__class__.model_fields.items():
            meta = hedron_meta(finfo)
            if meta.get("identity"):
                value = getattr(self.props, fname)
                if isinstance(value, Secret):
                    continue
                result[fname] = redact_value(value)
        if self._key is not None:
            result["key"] = self._key
        return result

    def compute_instance_id(self) -> str:
        return instance_id(
            {
                "logical_id": self.logical_id(),
                "identity": self.identity_fields(),
            }
        )

    def render(self) -> Any:
        raise error(
            "HED-RENDER-0005",
            title="render() not implemented",
            explanation=f"{self.__class__.__name__}.render() must be overridden.",
            component_id=self.logical_id(),
        )

    def __hedron_node__(self) -> Component[Any]:
        return self
