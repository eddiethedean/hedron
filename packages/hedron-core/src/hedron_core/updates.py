"""Portable refresh intents, typed fragment patches, and handle descriptors (0.43)."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Generic, Literal, Protocol, TypeVar, cast, runtime_checkable
from urllib.parse import quote

from hedron_core.codes import (
    HED_UPDATE_0001,
    HED_UPDATE_0002,
    HED_UPDATE_0003,
    HED_UPDATE_0004,
    HED_UPDATE_0005,
    HED_UPDATE_0006,
    HED_UPDATE_0007,
    HED_UPDATE_0008,
    HED_UPDATE_0009,
    HED_VIEW_0001,
    HED_VIEW_0003,
    HED_VIEW_0004,
)
from hedron_core.component import NodeLike
from hedron_core.diagnostics import error
from hedron_core.htmx.policy import (
    CacheHint,
    FragmentRegion,
    InteractionPolicy,
    InteractionResult,
    OobUpdate,
)
from hedron_core.identifiers import instance_id
from hedron_core.mount import prefix_local_path
from hedron_core.security import Secret, is_secret, redact_secret_like, redact_value
from hedron_core.typing_aliases import JsonValue

__all__ = [
    "BASE_DESCRIPTOR_VERSION",
    "IDENTITY_ALGO_VERSION",
    "MAX_EVENT_BYTES",
    "MAX_PATCH_TARGETS",
    "MAX_REFRESH_TARGETS",
    "SUPPORTED_SWAPS",
    "BaseHandleDescriptor",
    "BindingAdapter",
    "BindingPlan",
    "BoundValues",
    "HandleKind",
    "Patch",
    "PatchSet",
    "PortableTarget",
    "RefreshIntent",
    "StructuralBindingAdapter",
    "UpdateTarget",
    "compile_to_interaction",
    "descriptor_fingerprint",
    "handle_graph_payload",
    "matches_declared_host",
    "generated_command_path",
    "generated_view_path",
    "list_handle_descriptors",
    "normalize_logical_id",
    "refresh_event_name",
    "register_handle_descriptor",
    "reset_handles_for_tests",
    "unregister_handle_descriptor",
    "safe_dom_id",
    "structural_bind",
    "validate_explicit_key",
]

IDENTITY_ALGO_VERSION = 1
BASE_DESCRIPTOR_VERSION = 1
MAX_REFRESH_TARGETS = 16
MAX_PATCH_TARGETS = 16
MAX_EVENT_BYTES = 8192
SUPPORTED_SWAPS = frozenset({"outerHTML", "innerHTML"})
_LOGICAL_RE = re.compile(r"^[a-z][a-z0-9-]{0,62}$")
_KEY_RE = re.compile(r"^[A-Za-z][\w:-]{0,63}$")
# Bound instance suffix from ``instance_id(...)[2:]`` (20 lowercase RFC 4648 base32).
_INSTANCE_TOKEN_RE = re.compile(r"^[a-z2-7]{20}$")

HandleKind = Literal["view", "command"]
EffectKnowledge = Literal["dynamic", "observed", "declared"]
ContentT = TypeVar("ContentT")

_DESCRIPTORS: dict[tuple[str, str], BaseHandleDescriptor] = {}
_KEYS: dict[tuple[str, str], str] = {}


def normalize_logical_id(name: str) -> str:
    """Return a stable, URL-safe logical id derived from ``name``."""
    slug = re.sub(r"[^a-z0-9]+", "-", str(name).strip().lower()).strip("-")
    if not slug or not _LOGICAL_RE.match(slug):
        raise error(
            HED_VIEW_0001,
            title="Invalid view or command identity",
            explanation=f"Could not derive a safe logical id from {name!r}.",
            remediation="Pass an explicit key= using a letter-leading HTML-safe token.",
        )
    return slug


def validate_explicit_key(key: str) -> str:
    if not _KEY_RE.match(key) or any(ord(ch) < 32 for ch in key):
        raise error(
            HED_VIEW_0001,
            title="Unsafe or duplicate explicit key",
            explanation=f"Explicit key {key!r} is not a safe HTML identity token.",
            remediation="Use a letter-leading key of letters, digits, '_', ':' or '-'.",
        )
    return key


def safe_dom_id(logical_id: str, *, instance_token: str | None = None) -> str:
    base = f"h-view-{logical_id}" if not logical_id.startswith("h-") else logical_id
    if instance_token:
        return f"{base}-{instance_token}"
    return base


def refresh_event_name(dom_id: str) -> str:
    token = re.sub(r"[^a-z0-9-]+", "-", dom_id.lower()).strip("-")
    return f"hedron:refresh-{token}"


def matches_declared_host(region: FragmentRegion, target: str | None) -> bool:
    """Return True when ``target`` is this host or a bound instance of it.

    Bound instances are ``{canonical}-{instance_token}`` where the token is the
    20-character lowercase base32 suffix from ``instance_id``. A sibling view whose
    logical id extends this one (``user`` vs ``user-admin``) must not match.
    """
    if not target:
        return True
    if target.startswith("##"):
        return False
    needle = target[1:] if target.startswith("#") else target
    if not needle or "#" in needle:
        return False
    canonical = region.id if region.id.startswith("h-") else safe_dom_id(region.id)
    if needle == canonical:
        return True
    prefix = f"{canonical}-"
    if not needle.startswith(prefix):
        return False
    return _INSTANCE_TOKEN_RE.fullmatch(needle[len(prefix) :]) is not None


def generated_view_path(
    logical_id: str,
    path_params: Sequence[str] = (),
    *,
    mount_path: str = "",
) -> str:
    tail = f"/_hedron/views/{logical_id}"
    for name in path_params:
        tail += f"/{{{name}}}"
    return prefix_local_path(tail, mount_path)


def generated_command_path(
    logical_id: str,
    path_params: Sequence[str] = (),
    *,
    mount_path: str = "",
) -> str:
    tail = f"/_hedron/commands/{logical_id}"
    for name in path_params:
        tail += f"/{{{name}}}"
    return prefix_local_path(tail, mount_path)


@dataclass(frozen=True, slots=True)
class BindingPlan:
    path_params: tuple[str, ...] = ()
    query_params: tuple[str, ...] = ()
    required: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class BoundValues:
    parameters: Mapping[str, object]
    instance_token: str
    path: str
    query: Mapping[str, str]


@runtime_checkable
class UpdateTarget(Protocol):
    logical_id: str
    dom_id: str
    path: str
    app_id: str
    region: FragmentRegion
    bound: bool
    selector: str


@dataclass(frozen=True, slots=True)
class PortableTarget:
    """Framework-neutral registered update target used by adapters and fixtures."""

    logical_id: str
    dom_id: str
    path: str
    app_id: str
    region: FragmentRegion
    bound: bool = True
    selector: str = ""

    def __post_init__(self) -> None:
        if not self.selector:
            object.__setattr__(self, "selector", f"#{self.dom_id}")


@dataclass(frozen=True, slots=True)
class BaseHandleDescriptor:
    version: int = BASE_DESCRIPTOR_VERSION
    kind: HandleKind = "view"
    app_id: str = ""
    logical_id: str = ""
    name: str = ""
    path: str = ""
    method: str = "GET"
    host_tag: str = "div"
    swap: str = "outerHTML"
    fallback: str | None = None
    include_in_schema: bool = False
    binding: BindingPlan = field(default_factory=BindingPlan)
    effect: EffectKnowledge = "dynamic"
    limits: Mapping[str, int] = field(
        default_factory=lambda: {
            "max_refresh_targets": MAX_REFRESH_TARGETS,
            "max_patch_targets": MAX_PATCH_TARGETS,
        }
    )
    extensions: Mapping[str, Mapping[str, JsonValue]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        frozen_limits = dict(self.limits)
        object.__setattr__(self, "limits", frozen_limits)
        object.__setattr__(self, "extensions", dict(self.extensions))
        _assert_extensions_cannot_override(self.extensions)


def _assert_extensions_cannot_override(extensions: Mapping[str, Mapping[str, JsonValue]]) -> None:
    reserved = {
        "path",
        "method",
        "app_id",
        "logical_id",
        "host",
        "target",
        "fallback",
        "limits",
        "swap",
        "region",
    }
    for namespace, payload in extensions.items():
        if not namespace or "/" in namespace or " " in namespace:
            raise error(
                HED_UPDATE_0005,
                title="Invalid handle descriptor extension namespace",
                explanation=f"Extension namespace {namespace!r} is not a bounded name.",
                remediation="Use a short namespaced token such as 'hedron.type'.",
            )
        overlap = reserved.intersection(payload)
        if overlap:
            raise error(
                HED_UPDATE_0003,
                title="Descriptor extension cannot override base fields",
                explanation=f"Namespace {namespace!r} attempted to override {sorted(overlap)}.",
                remediation=(
                    "Attach type/tooling metadata only; do not replace routing or identity."
                ),
            )


def descriptor_fingerprint(descriptor: BaseHandleDescriptor) -> str:
    payload = {
        "v": descriptor.version,
        "kind": descriptor.kind,
        "app_id": descriptor.app_id,
        "logical_id": descriptor.logical_id,
        "name": descriptor.name,
        "path": descriptor.path,
        "method": descriptor.method,
        "host_tag": descriptor.host_tag,
        "swap": descriptor.swap,
        "fallback": descriptor.fallback,
        "include_in_schema": descriptor.include_in_schema,
        "binding": {
            "path_params": list(descriptor.binding.path_params),
            "query_params": list(descriptor.binding.query_params),
            "required": list(descriptor.binding.required),
        },
        "limits": dict(descriptor.limits),
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return digest[:32]


def register_handle_descriptor(descriptor: BaseHandleDescriptor, *, key: str | None = None) -> None:
    slot = (descriptor.app_id, descriptor.logical_id)
    existing = _DESCRIPTORS.get(slot)
    if existing is not None and descriptor_fingerprint(existing) != descriptor_fingerprint(
        descriptor
    ):
        raise error(
            HED_VIEW_0001,
            title="Unsafe or duplicate explicit key",
            explanation=f"Handle {descriptor.logical_id!r} is already registered on this app.",
            remediation="Use a distinct name or explicit key=.",
        )
    _DESCRIPTORS[slot] = descriptor
    if key:
        key_slot = (descriptor.app_id, key)
        owner = _KEYS.get(key_slot)
        if owner not in {None, descriptor.logical_id}:
            raise error(
                HED_VIEW_0001,
                title="Unsafe or duplicate explicit key",
                explanation=f"Explicit key {key!r} is already owned by {owner!r}.",
                remediation="Choose a unique key= for this handle.",
            )
        _KEYS[key_slot] = descriptor.logical_id


def unregister_handle_descriptor(logical_id: str, *, app_id: str) -> None:
    """Drop a handle descriptor. Used by FeatureBundle rollback/eject."""
    _DESCRIPTORS.pop((app_id, logical_id), None)
    stale = [key for key, owner in _KEYS.items() if key[0] == app_id and owner == logical_id]
    for key in stale:
        _KEYS.pop(key, None)


def list_handle_descriptors(*, app_id: str | None = None) -> tuple[BaseHandleDescriptor, ...]:
    rows = list(_DESCRIPTORS.values())
    if app_id is not None:
        rows = [item for item in rows if item.app_id == app_id]
    return tuple(sorted(rows, key=lambda item: (item.kind, item.logical_id)))


def handle_graph_payload(*, app_id: str | None = None) -> dict[str, object]:
    """View-command-output graph. Effects are dynamic, observed, or declared."""
    from hedron_core.type_schema import TYPE_SCHEMA_NAMESPACE

    nodes: list[dict[str, object]] = []
    any_declared = False
    for descriptor in list_handle_descriptors(app_id=app_id):
        view = redacted_descriptor_view(descriptor)
        if descriptor.effect == "declared":
            any_declared = True
        type_payload = descriptor.extensions.get(TYPE_SCHEMA_NAMESPACE)
        nodes.append(
            {
                "id": descriptor.logical_id,
                "kind": descriptor.kind,
                "effect": descriptor.effect,
                "path": descriptor.path,
                "method": descriptor.method,
                "fingerprint": view["fingerprint"],
                "type_schema": type_payload if isinstance(type_payload, dict) else None,
            }
        )
    return {
        "kind": "view-command-output",
        "effects": "declared" if any_declared else "dynamic/observed",
        "nodes": nodes,
        "edges": [],
    }


def reset_handles_for_tests() -> None:
    _DESCRIPTORS.clear()
    _KEYS.clear()
    from hedron_core.catalog import reset_catalog_for_tests

    reset_catalog_for_tests()
    from hedron_core.bundles import reset_bundles_for_tests

    reset_bundles_for_tests()


def _canonical_params(parameters: Mapping[str, object]) -> dict[str, object]:
    redacted = redact_value(dict(parameters))
    if not isinstance(redacted, dict):
        return {}
    return {str(key): redacted[key] for key in sorted(redacted)}


def structural_bind(plan: BindingPlan, values: Mapping[str, object], *, path: str) -> BoundValues:
    names = set(plan.path_params) | set(plan.query_params)
    extra = sorted(set(values) - names)
    if extra:
        raise error(
            HED_VIEW_0004,
            title="Unknown bind parameter",
            explanation=f"Bind received unexpected names {extra}.",
            remediation="Pass only registered path and query parameter names.",
        )
    missing = [name for name in plan.required if name not in values]
    if missing:
        raise error(
            HED_VIEW_0004,
            title="Missing bind parameter",
            explanation=f"Bind is missing required names {missing}.",
            remediation="Supply every required path/query parameter.",
        )
    encoded: dict[str, str] = {}
    path_values: dict[str, str] = {}
    for name, value in values.items():
        if is_secret(value) or isinstance(value, Secret):
            raise error(
                HED_VIEW_0004,
                title="Secret cannot be bound into a URL or identity",
                explanation=f"Parameter {name!r} is a Secret and cannot appear in ids or URLs.",
                remediation="Keep secrets on the GET route via dependencies, not bind().",
            )
        text = str(value)
        if any(ord(ch) < 32 for ch in text) or "\x00" in text:
            raise error(
                HED_VIEW_0004,
                title="Unsafe bind value",
                explanation=f"Parameter {name!r} contains unsafe control characters.",
                remediation="Pass printable scalar values only.",
            )
        if name in plan.path_params:
            if not text or any(ch in text for ch in "/?#") or ".." in text:
                raise error(
                    HED_VIEW_0004,
                    title="Unsafe bind path value",
                    explanation=(
                        f"Parameter {name!r} cannot contain empty, '/', '?', '#', or '..' values."
                    ),
                    remediation="Pass a single path segment without reserved URL characters.",
                )
            path_values[name] = quote(text, safe="")
        else:
            encoded[name] = text
    rendered = path
    for name in plan.path_params:
        if name in path_values:
            rendered = rendered.replace("{" + name + "}", path_values[name])
    if "{" in rendered and "}" in rendered:
        raise error(
            HED_VIEW_0003,
            title="Unbound parameterized handle",
            explanation="A path parameter remains unsubstituted after bind().",
            remediation="Supply every path parameter declared on the handle.",
        )
    token = instance_id(
        {
            "v": IDENTITY_ALGO_VERSION,
            "path": rendered,
            "params": _canonical_params(values),
        }
    )[2:]
    return BoundValues(
        parameters=dict(values),
        instance_token=token,
        path=rendered,
        query=encoded,
    )


class BindingAdapter(Protocol):
    def bind(
        self, plan: BindingPlan, values: Mapping[str, object], *, path: str
    ) -> BoundValues: ...


class StructuralBindingAdapter:
    """Default 0.43 adapter: route/query structure and safe encoding only."""

    def bind(self, plan: BindingPlan, values: Mapping[str, object], *, path: str) -> BoundValues:
        return structural_bind(plan, values, path=path)


@dataclass(frozen=True, slots=True)
class Patch(Generic[ContentT]):
    target: UpdateTarget
    content: ContentT
    swap: Literal["outerHTML", "innerHTML"] = "outerHTML"

    def __post_init__(self) -> None:
        if self.swap not in SUPPORTED_SWAPS:
            raise error(
                HED_UPDATE_0005,
                title="Unsafe or unknown swap",
                explanation=f"Patch swap {self.swap!r} is outside the closed Supported set.",
                remediation="Use replace() (outerHTML) or update() (innerHTML).",
            )
        if not self.target.bound:
            raise error(
                HED_UPDATE_0007,
                title="Unbound parameterized patch target",
                explanation=f"Handle {self.target.logical_id!r} must be bound before patching.",
                remediation="Call bind(...) before replace/update.",
            )


@dataclass(frozen=True, slots=True)
class PatchSet:
    primary: Patch[object]
    secondary: tuple[Patch[object], ...] = ()
    status_code: int = 200
    toast: NodeLike | str | None = None
    cache: CacheHint | None = "vary-htmx"

    def __post_init__(self) -> None:
        if self.primary is None:
            raise error(
                HED_UPDATE_0008,
                title="Missing primary patch",
                explanation="PatchSet requires one primary patch.",
                remediation="Pass the primary update as the first positional patch.",
            )
        targets = [self.primary, *self.secondary]
        if len(targets) > MAX_PATCH_TARGETS:
            raise error(
                HED_UPDATE_0004,
                title="Patch target limit exceeded",
                explanation=f"PatchSet has {len(targets)} targets; max is {MAX_PATCH_TARGETS}.",
                remediation="Split the update or reduce fan-out.",
            )
        seen: set[tuple[str, str]] = set()
        for item in targets:
            key = (item.target.app_id, item.target.dom_id)
            if key in seen:
                raise error(
                    HED_UPDATE_0002,
                    title="Duplicate patch target",
                    explanation=f"Target {item.target.logical_id!r} appears more than once.",
                    remediation="Emit one mechanism per target.",
                )
            seen.add(key)
        if self.status_code == 204 and (self.secondary or self.toast is not None):
            raise error(
                HED_UPDATE_0006,
                title="OOB content with status 204",
                explanation="A 204 patch cannot carry secondary updates or toast.",
                remediation="Use status 200 when returning out-of-band content.",
            )


@dataclass(frozen=True, slots=True)
class RefreshIntent:
    targets: tuple[UpdateTarget, ...]
    toast_content: NodeLike | str | None = None

    def toast(self, message: NodeLike | str) -> RefreshIntent:
        return replace(self, toast_content=message)

    def __post_init__(self) -> None:
        seen: dict[tuple[str, str], UpdateTarget] = {}
        ordered: list[UpdateTarget] = []
        for target in self.targets:
            if not target.bound:
                raise error(
                    HED_UPDATE_0007,
                    title="Unbound parameterized refresh target",
                    explanation=f"Handle {target.logical_id!r} must be bound before refresh.",
                    remediation="Call bind(...) before refresh(...).",
                )
            key = (target.app_id, target.dom_id)
            if key in seen:
                continue
            seen[key] = target
            ordered.append(target)
        object.__setattr__(self, "targets", tuple(ordered))
        if len(self.targets) > MAX_REFRESH_TARGETS:
            raise error(
                HED_UPDATE_0004,
                title="Refresh target limit exceeded",
                explanation=(
                    f"refresh() received {len(self.targets)} targets; max is {MAX_REFRESH_TARGETS}."
                ),
                remediation="Coalesce or reduce fan-out; fan-out is not atomic.",
            )


def _target_app(targets: Sequence[UpdateTarget]) -> str | None:
    apps = {item.app_id for item in targets if item.app_id}
    if len(apps) > 1:
        raise error(
            HED_UPDATE_0003,
            title="Foreign or unregistered handle",
            explanation="Refresh/patch targets must belong to one application.",
            remediation="Pass handles from the active app only.",
        )
    return next(iter(apps), None)


def _toast_oob(toast: NodeLike | str | None) -> tuple[OobUpdate, ...]:
    if toast is None:
        return ()
    if isinstance(toast, str):
        from hedron_core.builtins import Toast

        content: NodeLike = Toast(toast)
    else:
        content = toast
    return (OobUpdate(content=content, element_id="hedron-toast", swap="innerHTML"),)


def _ensure_ownership(target: UpdateTarget, expected_app_id: str | None) -> None:
    if expected_app_id is None or not target.app_id:
        return
    if target.app_id != expected_app_id:
        raise error(
            HED_UPDATE_0003,
            title="Foreign or unregistered handle",
            explanation="Patch/refresh target is not owned by the active application.",
            remediation="Use handles registered on this app; do not forge metadata.",
        )


def _compile_refresh(intent: RefreshIntent, expected_app_id: str | None) -> InteractionResult:
    _target_app(intent.targets)
    trigger: dict[str, JsonValue] = {}
    for target in intent.targets:
        _ensure_ownership(target, expected_app_id)
        trigger[refresh_event_name(target.dom_id)] = {}
    encoded = json.dumps(trigger, separators=(",", ":"), sort_keys=True)
    if len(encoded.encode("utf-8")) > MAX_EVENT_BYTES:
        raise error(
            HED_UPDATE_0009,
            title="Refresh event payload too large",
            explanation=(
                f"Serialized refresh events are {len(encoded)} bytes; max is {MAX_EVENT_BYTES}."
            ),
            remediation="Reduce target count or logical id length.",
        )
    return InteractionResult(
        content=None,
        status_code=200,
        trigger=trigger,
        oob=_toast_oob(intent.toast_content),
        policy=InteractionPolicy(allow_undeclared_targets=True),
        explanation="refresh intent; follow-up GETs are not an atomic transaction",
    )


def _compile_patches(bundle: PatchSet, expected_app_id: str | None) -> InteractionResult:
    all_targets = (bundle.primary.target, *(item.target for item in bundle.secondary))
    _target_app(all_targets)
    for target in all_targets:
        _ensure_ownership(target, expected_app_id)
    primary = bundle.primary
    oob: list[OobUpdate] = list(_toast_oob(bundle.toast))
    for item in bundle.secondary:
        oob.append(
            OobUpdate(
                content=cast(NodeLike, item.content),
                element_id=item.target.dom_id,
                swap=item.swap,
            )
        )
    return InteractionResult(
        content=cast(NodeLike, primary.content),
        status_code=bundle.status_code,
        retarget=primary.target.selector,
        swap=primary.swap,
        oob=tuple(oob),
        cache=bundle.cache,
        policy=InteractionPolicy(allow_undeclared_targets=True),
    )


def compile_to_interaction(value: object, *, expected_app_id: str | None = None) -> object:
    """Compile 0.43 update values into ``InteractionResult``; pass other values through."""
    if isinstance(value, InteractionResult):
        has_refresh = False
        if isinstance(value.trigger, dict):
            has_refresh = any(str(key).startswith("hedron:refresh-") for key in value.trigger)
        mixed = has_refresh and any(
            getattr(item, "element_id", None) != "hedron-toast" for item in value.oob
        )
        if mixed:
            raise error(
                HED_UPDATE_0001,
                title="Mixed refresh and patch",
                explanation="A response cannot combine refresh intents with patch targets.",
                remediation="Return refresh(...) or patches(...), not both.",
            )
        return value
    if isinstance(value, RefreshIntent) and isinstance(value, PatchSet):
        raise error(
            HED_UPDATE_0001,
            title="Mixed refresh and patch",
            explanation="A value cannot be both a refresh intent and a PatchSet.",
            remediation="Return one update mode.",
        )
    if isinstance(value, RefreshIntent):
        return _compile_refresh(value, expected_app_id)
    if isinstance(value, Patch):
        return _compile_patches(PatchSet(primary=value), expected_app_id)
    if isinstance(value, PatchSet):
        return _compile_patches(value, expected_app_id)
    return value


def redacted_descriptor_view(descriptor: BaseHandleDescriptor) -> dict[str, object]:
    from hedron_core.type_schema import TYPE_SCHEMA_NAMESPACE

    payload: dict[str, object] = {
        "kind": descriptor.kind,
        "logical_id": descriptor.logical_id,
        "name": descriptor.name,
        "path": descriptor.path,
        "method": descriptor.method,
        "fallback": descriptor.fallback,
        "effect": descriptor.effect,
        "fingerprint": descriptor_fingerprint(descriptor),
        "binding": {
            "path_params": list(descriptor.binding.path_params),
            "query_params": list(descriptor.binding.query_params),
        },
    }
    type_payload = descriptor.extensions.get(TYPE_SCHEMA_NAMESPACE)
    if isinstance(type_payload, dict):
        payload["type_schema"] = type_payload
    return redact_secret_like(payload)
