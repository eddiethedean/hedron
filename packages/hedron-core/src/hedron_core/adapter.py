"""Portable adapter protocols and capability records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

__all__ = [
    "AdapterCapability",
    "AuthSignal",
    "CapabilityClass",
    "CapabilityRecord",
    "FASTAPI_CAPABILITIES",
    "FLASK_CAPABILITIES",
    "DJANGO_CAPABILITIES",
    "LifecycleResource",
    "UrlReverseRequest",
    "capability_matrix",
]


class CapabilityClass(StrEnum):
    PORTABLE = "portable"
    ASGI = "asgi"
    WSGI = "wsgi"
    FRAMEWORK = "framework"


@dataclass(frozen=True, slots=True)
class AdapterCapability:
    name: str
    classification: CapabilityClass
    supported: bool
    evidence_id: str = ""
    notes: str = ""


@dataclass(frozen=True, slots=True)
class CapabilityRecord:
    adapter: str
    stability: str  # supported | experimental | deferred
    capabilities: tuple[AdapterCapability, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "adapter": self.adapter,
            "stability": self.stability,
            "capabilities": [
                {
                    "name": c.name,
                    "classification": c.classification.value,
                    "supported": c.supported,
                    "evidence_id": c.evidence_id,
                    "notes": c.notes,
                }
                for c in self.capabilities
            ],
        }


@dataclass(frozen=True, slots=True)
class AuthSignal:
    """Authenticated-state signal without session contents."""

    authenticated: bool
    subject_id: str | None = None
    scopes: tuple[str, ...] = ()
    tenant_id: str | None = None


@dataclass(frozen=True, slots=True)
class UrlReverseRequest:
    name: str
    args: tuple[Any, ...] = ()
    kwargs: Mapping[str, Any] = field(default_factory=dict)
    root_path: str = ""
    script_name: str = ""


@dataclass(frozen=True, slots=True)
class LifecycleResource:
    name: str
    order: int = 100
    description: str = ""


@runtime_checkable
class UrlReverser(Protocol):
    def reverse(self, request: UrlReverseRequest) -> str: ...


def _caps(*items: AdapterCapability) -> tuple[AdapterCapability, ...]:
    return items


FASTAPI_CAPABILITIES = CapabilityRecord(
    adapter="fastapi",
    stability="supported",
    capabilities=_caps(
        AdapterCapability("safe_html_render", CapabilityClass.PORTABLE, True, "ADP-002"),
        AdapterCapability("htmx_headers", CapabilityClass.PORTABLE, True, "ADP-002"),
        AdapterCapability("url_reverse", CapabilityClass.PORTABLE, True, "ADP-004"),
        AdapterCapability("disconnect_cancellation", CapabilityClass.ASGI, True, "OPS-005"),
        AdapterCapability("lifespan", CapabilityClass.FRAMEWORK, True),
        AdapterCapability("background_tasks", CapabilityClass.FRAMEWORK, True, "JOB-005"),
        AdapterCapability("dependency_injection", CapabilityClass.FRAMEWORK, True),
    ),
)

FLASK_CAPABILITIES = CapabilityRecord(
    adapter="flask",
    stability="supported",
    capabilities=_caps(
        AdapterCapability("safe_html_render", CapabilityClass.PORTABLE, True, "ADP-002"),
        AdapterCapability("htmx_headers", CapabilityClass.PORTABLE, True, "ADP-002"),
        AdapterCapability("url_reverse", CapabilityClass.PORTABLE, True, "ADP-004"),
        AdapterCapability("disconnect_cancellation", CapabilityClass.WSGI, False, "ADP-FLK-002"),
        AdapterCapability("lifespan", CapabilityClass.WSGI, False, "ADP-FLK-002"),
        AdapterCapability("url_for", CapabilityClass.FRAMEWORK, True, "ADP-FLK-001"),
        AdapterCapability("cookie_sessions", CapabilityClass.FRAMEWORK, True, "ADP-FLK-001"),
    ),
)

DJANGO_CAPABILITIES = CapabilityRecord(
    adapter="django",
    stability="supported",
    capabilities=_caps(
        AdapterCapability("safe_html_render", CapabilityClass.PORTABLE, True, "ADP-002"),
        AdapterCapability("htmx_headers", CapabilityClass.PORTABLE, True, "ADP-002"),
        AdapterCapability("url_reverse", CapabilityClass.PORTABLE, True, "ADP-004"),
        AdapterCapability("asgi_mode", CapabilityClass.ASGI, True, "ADP-DJG-002"),
        AdapterCapability("wsgi_mode", CapabilityClass.WSGI, True, "ADP-DJG-002"),
        AdapterCapability(
            "django_forms",
            CapabilityClass.FRAMEWORK,
            False,
            "ADP-DJG-001",
            notes=(
                "Apps may use Django-native forms; Hedron does not ship a verified "
                "forms subsystem (deferred/experimental)."
            ),
        ),
        AdapterCapability(
            "queryset_datasource",
            CapabilityClass.FRAMEWORK,
            False,
            "ADP-DJG-002",
            notes="Deferred (D-036)",
        ),
    ),
)


def capability_matrix() -> tuple[CapabilityRecord, ...]:
    return (FASTAPI_CAPABILITIES, FLASK_CAPABILITIES, DJANGO_CAPABILITIES)
