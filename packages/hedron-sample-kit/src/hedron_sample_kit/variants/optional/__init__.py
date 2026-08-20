"""Optional integration variant with missing-extra honesty.

The bundle is always described. When the optional extra is absent or the opt-in
environment flag is unset, the projected capability reports ``unsupported`` with
the remediation instead of silently disappearing.
"""

from __future__ import annotations

import importlib.util
import os

from hedron_core.bundles import FeatureBundle, FeatureRequirement
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.plugins import PluginContext

VARIANT_ID = "optional"
BUNDLE_ID = "hedron-sample-kit:optional-feature"
NAMESPACE = "hedron.sample-kit.optional"
ENV_FLAG = "HEDRON_SAMPLE_KIT_OPTIONAL"
OPTIONAL_DISTRIBUTION = "hedron-charts"
OPTIONAL_MODULE = "hedron_charts"

_TRUTHY = frozenset({"1", "true", "yes", "on"})

__all__ = [
    "BUNDLE_ID",
    "ENV_FLAG",
    "NAMESPACE",
    "OPTIONAL_DISTRIBUTION",
    "OPTIONAL_MODULE",
    "VARIANT_ID",
    "feature_bundle",
    "optional_status",
    "register",
]


def _extra_installed() -> bool:
    try:
        return importlib.util.find_spec(OPTIONAL_MODULE) is not None
    except (ImportError, ValueError):
        return False


def _env_enabled() -> bool:
    return os.environ.get(ENV_FLAG, "").strip().lower() in _TRUTHY


def optional_status() -> dict[str, bool | str]:
    """Report why the optional integration is or is not active."""
    installed = _extra_installed()
    enabled = _env_enabled()
    if not installed:
        reason = f"install the optional extra providing {OPTIONAL_DISTRIBUTION!r}"
    elif not enabled:
        reason = f"set {ENV_FLAG}=1 to opt in"
    else:
        reason = ""
    return {
        "extra_installed": installed,
        "env_enabled": enabled,
        "active": installed and enabled,
        "reason": reason,
    }


def feature_bundle(provider_version: str) -> FeatureBundle:
    status = optional_status()
    active = bool(status["active"])
    reason = str(status["reason"])
    return FeatureBundle(
        logical_id=BUNDLE_ID,
        provider="hedron-sample-kit",
        provider_version=provider_version,
        projections=(
            PackageProjection(
                namespace=NAMESPACE,
                provider="hedron-sample-kit",
                provider_version=provider_version,
                capabilities=(
                    ProjectionCapability(
                        name="optional-integration",
                        support="supported" if active else "unavailable",
                        limitation=reason,
                    ),
                ),
                data={
                    "third_party": True,
                    "privileged": False,
                    "env_flag": ENV_FLAG,
                    "optional_distribution": OPTIONAL_DISTRIBUTION,
                    "extra_installed": bool(status["extra_installed"]),
                    "env_enabled": bool(status["env_enabled"]),
                    "active": active,
                },
                limitations=(
                    ("opt-in integration is active",) if active else (f"inactive: {reason}",)
                ),
            ),
        ),
        requirements=(FeatureRequirement(name=OPTIONAL_DISTRIBUTION, required=False),),
        optional_capabilities=("optional-integration",),
    )


def register(ctx: PluginContext) -> None:
    ctx.register_feature_bundle(feature_bundle(ctx.meta.version))
