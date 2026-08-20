"""Typed action/workflow variant projected through a FeatureBundle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from hedron_core.bundles import FeatureBundle
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.models import Props
from hedron_core.plugins import PluginContext

VARIANT_ID = "workflow"
BUNDLE_ID = "hedron-sample-kit:workflow-feature"
NAMESPACE = "hedron.sample-kit.workflow"

__all__ = [
    "BUNDLE_ID",
    "NAMESPACE",
    "STEPS",
    "VARIANT_ID",
    "PublishNoteInput",
    "SampleAction",
    "WorkflowStep",
    "actions",
    "feature_bundle",
    "register",
]


class PublishNoteInput(Props):
    """Typed payload for the sample publish action."""

    note: str = "Sample kit note"
    audience: Literal["team", "everyone"] = "team"


@dataclass(frozen=True, slots=True)
class SampleAction:
    """Declared action; description only, the kit never executes it."""

    action_id: str
    title: str
    input_model: str
    idempotent: bool = True


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    """Ordered step naming a declared action."""

    step_id: str
    action_id: str
    on_failure: Literal["stop", "continue"] = "stop"


def actions() -> tuple[SampleAction, ...]:
    return (
        SampleAction(
            action_id="sample-kit.draft-note",
            title="Draft note",
            input_model="PublishNoteInput",
        ),
        SampleAction(
            action_id="sample-kit.publish-note",
            title="Publish note",
            input_model="PublishNoteInput",
            idempotent=False,
        ),
    )


STEPS: tuple[WorkflowStep, ...] = (
    WorkflowStep(step_id="draft", action_id="sample-kit.draft-note"),
    WorkflowStep(step_id="publish", action_id="sample-kit.publish-note"),
)


def feature_bundle(provider_version: str) -> FeatureBundle:
    declared = actions()
    return FeatureBundle(
        logical_id=BUNDLE_ID,
        provider="hedron-sample-kit",
        provider_version=provider_version,
        projections=(
            PackageProjection(
                namespace=NAMESPACE,
                provider="hedron-sample-kit",
                provider_version=provider_version,
                capabilities=tuple(
                    ProjectionCapability(name=action.action_id, support="supported")
                    for action in declared
                ),
                data={
                    "third_party": True,
                    "privileged": False,
                    "actions": [
                        {
                            "action_id": action.action_id,
                            "input_model": action.input_model,
                            "idempotent": action.idempotent,
                        }
                        for action in declared
                    ],
                    "steps": [
                        {
                            "step_id": step.step_id,
                            "action_id": step.action_id,
                            "on_failure": step.on_failure,
                        }
                        for step in STEPS
                    ],
                },
                limitations=("declaration only; the host owns execution and job state",),
            ),
        ),
        limitations=("no job backend is claimed; polling_only stays untouched",),
    )


def register(ctx: PluginContext) -> None:
    ctx.register_feature_bundle(feature_bundle(ctx.meta.version))
