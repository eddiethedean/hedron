"""Component base and NodeLike protocol."""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from contextvars import ContextVar, Token
from typing import ClassVar, Generic, Protocol, TypeAlias, TypeVar, cast, runtime_checkable

from pydantic import ValidationError
from typing_extensions import Self

from hedron_core.diagnostics import error
from hedron_core.field import hedron_meta
from hedron_core.identifiers import component_type_id, instance_id
from hedron_core.models import Props
from hedron_core.security import Secret

PropsT = TypeVar("PropsT", bound=Props)

_render_identity: ContextVar[tuple[str, str] | None] = ContextVar(
    "hedron_render_identity", default=None
)


def push_render_identity(instance: str, render_key: str) -> Token[tuple[str, str] | None]:
    """Set request-local component identity for the duration of one render call."""
    return _render_identity.set((instance, render_key))


def pop_render_identity(token: Token[tuple[str, str] | None]) -> None:
    """Restore the identity context captured by :func:`push_render_identity`."""
    _render_identity.reset(token)


@runtime_checkable
class ComponentNode(Protocol):
    """Opaque protocol implemented by components and native HTML nodes."""

    def __hedron_node__(self) -> NodeLike: ...


class Component(Generic[PropsT]):
    """Base class for reusable server-rendered UI components."""

    props_type: ClassVar[type[Props]]
    logical_name: ClassVar[str | None] = None
    distribution: ClassVar[str] = "hedron-core"
    slots: ClassVar[dict[str, str]] = {}  # name -> cardinality: required|optional|many

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "props_type") or cls.props_type is Component.__dict__.get(
            "props_type", None
        ):
            for base in getattr(cls, "__orig_bases__", ()):
                args = getattr(base, "__args__", ())
                if args and isinstance(args[0], type) and issubclass(args[0], Props):
                    cls.props_type = args[0]
                    break
        if getattr(cls, "logical_name", None) is None:
            cls.logical_name = cls.__name__

    def __init__(self, props: PropsT | None = None, /, **kwargs: object) -> None:
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
                self._props = cast(PropsT, props_cls(**kwargs))
        except ValidationError as exc:
            # Redact potential secrets from validation messages.
            message = "Props validation failed."
            raise error(
                "HED-MODEL-0004",
                title="Invalid component props",
                explanation=message,
                remediation="Correct the props to match the declared Props model.",
                component_id=self.logical_id() if hasattr(self, "_props") else None,
            ) from exc
        self._children: tuple[NodeLike, ...] = ()
        self._slot_values: dict[str, NodeLike | list[NodeLike]] = {}
        self._key: str | None = None

    @property
    def props(self) -> PropsT:
        return self._props

    @property
    def child_nodes(self) -> tuple[NodeLike, ...]:
        """Return the configured child nodes without exposing mutation."""
        return self._children

    @property
    def slot_values(self) -> Mapping[str, NodeLike | list[NodeLike]]:
        """Return configured slot content through a read-only mapping contract."""
        return self._slot_values

    def key(self, value: str) -> Component[PropsT]:
        self._key = value
        return self

    def children(self, *nodes: NodeLike) -> Component[PropsT]:
        self._children = nodes
        return self

    def copy_with_props(self, props: Props) -> Self:
        """Return a shallow component copy with independently owned render state.

        Non-prop subclass state is retained, while children and slot mappings are
        copied so binding helpers cannot mutate the source component accidentally.
        """
        if not isinstance(props, self.props_type):
            raise TypeError(f"Expected {self.props_type.__name__}, got {type(props).__name__}")
        clone = copy.copy(self)
        clone._props = cast(PropsT, props)
        clone._children = tuple(self._children)
        clone._slot_values = dict(self._slot_values)
        return clone

    def slot(self, name: str, value: NodeLike) -> Component[PropsT]:
        cardinality = self.slots.get(name)
        if cardinality is None and self.slots:
            raise error(
                "HED-RENDER-0004",
                title="Unknown slot",
                explanation=f"Slot {name!r} is not declared on {self.__class__.__name__}.",
                remediation=f"Declared slots: {sorted(self.slots)}",
                component_id=self.logical_id(),
            )
        if cardinality == "many":
            existing = self._slot_values.get(name)
            if existing is None:
                self._slot_values[name] = [value]
            elif isinstance(existing, list):
                existing.append(value)
            else:
                self._slot_values[name] = [existing, value]
        else:
            self._slot_values[name] = value
        return self

    def validate_slots(self) -> None:
        for name, cardinality in self.slots.items():
            if cardinality == "required" and name not in self._slot_values:
                # body/children may be supplied via constructor children
                if name == "body" and self._children:
                    continue
                raise error(
                    "HED-RENDER-0014",
                    title="Required slot missing",
                    explanation=f"Required slot {name!r} was not provided.",
                    remediation=f"Call .slot({name!r}, ...) or pass the slot via constructor.",
                    component_id=self.logical_id(),
                )

    def logical_id(self) -> str:
        module = self.__class__.__module__
        name = self.logical_name or self.__class__.__name__
        return component_type_id(self.distribution, module, name)

    def identity_fields(self) -> dict[str, object]:
        result: dict[str, object] = {}
        for fname, finfo in self.props.__class__.model_fields.items():
            meta = hedron_meta(finfo)
            if not meta.get("identity"):
                continue
            if meta.get("secret"):
                continue
            value = getattr(self.props, fname)
            if isinstance(value, Secret):
                continue
            result[fname] = value
        if self._key is not None:
            result["key"] = self._key
        return result

    def compute_instance_id(self, *, auto_key: str | None = None) -> str:
        identity = dict(self.identity_fields())
        if "key" not in identity and auto_key is not None:
            identity["key"] = auto_key
        return instance_id(
            {
                "logical_id": self.logical_id(),
                "identity": identity,
            }
        )

    def render_instance_id(self) -> str:
        """Return this component's request-local ID while ``render()`` is running.

        Built-ins use this value to generate collision-free DOM relationships. Custom
        components may use it for the same purpose instead of inventing global IDs.
        """
        current = _render_identity.get()
        if current is not None:
            return current[0]
        return self.compute_instance_id()

    def render_key(self) -> str | None:
        """Return the explicit or renderer-assigned key during ``render()``."""
        current = _render_identity.get()
        return current[1] if current is not None else self._key

    def render(self) -> NodeLike:
        raise error(
            "HED-RENDER-0005",
            title="render() not implemented",
            explanation=f"{self.__class__.__name__}.render() must be overridden.",
            component_id=self.logical_id(),
        )

    async def prepare(self, ctx: object) -> None:
        """Optional async data preparation before sync ``render()``.

        Override to load request-owned data. Constructors must not perform hidden I/O.
        Default is a no-op so only explicit overrides participate in ``prepare_tree``.
        """
        del ctx

    def has_prepare_override(self) -> bool:
        """Return whether the concrete component implements async preparation."""
        for owner in type(self).__mro__:
            if "prepare" in vars(owner):
                return owner is not Component
        return False

    def __hedron_node__(self) -> Component[PropsT]:
        return self


# Shared public recursive alias (imported by rendering and package root).
NodeLike: TypeAlias = ComponentNode | str | int | float | bool | None | Sequence["NodeLike"]
