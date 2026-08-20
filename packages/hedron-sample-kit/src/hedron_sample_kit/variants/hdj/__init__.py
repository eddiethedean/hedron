"""HDJ binding marker variant.

Metadata only: the marker template ships with the kit and is described through a
FeatureBundle projection. Nothing here imports or requires ``hedron-jinja``, so
the variant stays installable without the HDJ extra.
"""

from __future__ import annotations

from pathlib import Path

from hedron_core.bundles import FeatureBundle, FeatureRequirement
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginContext

VARIANT_ID = "hdj"
BUNDLE_ID = "hedron-sample-kit:hdj-feature"
NAMESPACE = "hedron.sample-kit.hdj"
BINDING_MARKER = "---hdj"
TEMPLATE_ASSET_ID = "hedron-sample-kit:hdj.template"

_TEMPLATES = Path(__file__).resolve().parent / "templates"
TEMPLATE_PATH = _TEMPLATES / "sample_kit_callout.hdj"

__all__ = [
    "BINDING_MARKER",
    "BUNDLE_ID",
    "NAMESPACE",
    "TEMPLATE_ASSET_ID",
    "TEMPLATE_PATH",
    "VARIANT_ID",
    "binding_marker_present",
    "feature_bundle",
    "register",
]


def binding_marker_present() -> bool:
    """Return True when the shipped template carries the HDJ v1 prologue."""
    if not TEMPLATE_PATH.is_file():
        return False
    return TEMPLATE_PATH.read_text(encoding="utf-8").startswith(f"{BINDING_MARKER}\n")


def feature_bundle(provider_version: str) -> FeatureBundle:
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
                        name="hdj-binding-marker",
                        support="supported" if binding_marker_present() else "unavailable",
                        limitation="" if binding_marker_present() else "marker template missing",
                    ),
                ),
                data={
                    "third_party": True,
                    "privileged": False,
                    "binding": "hdj",
                    "marker": BINDING_MARKER,
                    "template": TEMPLATE_PATH.name,
                },
                limitations=("metadata only; rendering requires the hedron-jinja HDJ loader",),
            ),
        ),
        requirements=(FeatureRequirement(name="hedron-jinja", required=False),),
        optional_capabilities=("hdj-render",),
        limitations=("no HDJ environment is created by this variant",),
    )


def register(ctx: PluginContext) -> None:
    if TEMPLATE_PATH.is_file():
        ctx.register_asset(
            logical_id=TEMPLATE_ASSET_ID,
            kind="file",
            path=str(TEMPLATE_PATH),
            digest=content_digest(TEMPLATE_PATH.read_bytes()),
            content_type="text/plain",
        )
    ctx.register_feature_bundle(feature_bundle(ctx.meta.version))
