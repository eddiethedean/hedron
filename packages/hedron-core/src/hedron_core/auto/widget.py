"""Auto() component."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from hedron_core.auto.factories import is_tabular
from hedron_core.auto.inspect import inspect_data
from hedron_core.auto.registry import registered_renderers, set_last_auto_decision
from hedron_core.auto.spec import AutoDecision, RendererSpec
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.models import Props


class AutoProps(Props):
    as_: str | None = None


class Auto(Component[AutoProps]):
    """Select an appropriate component through the inspectable renderer registry."""

    props_type = AutoProps
    logical_name = "Auto"

    def __init__(self, value: object = None, *, as_: str | None = None, **kwargs: Any) -> None:
        super().__init__(AutoProps(as_=as_, **kwargs))
        self._value = value
        self._resolved: NodeLike | None = None
        self._decision: AutoDecision | None = None

    @property
    def decision(self) -> AutoDecision | None:
        return self._decision

    def resolve(self) -> NodeLike:
        value = self._value
        inspection: dict[str, object] = {}
        if is_tabular(value) or isinstance(value, Mapping):
            try:
                report = inspect_data(value)
                inspection = {
                    "row_count": report.row_count,
                    "columns": list(report.columns),
                    "cardinality": dict(report.cardinality),
                    "datetime_columns": list(report.datetime_columns),
                    "geospatial_columns": list(report.geospatial_columns),
                    "notes": list(report.notes),
                }
            except Exception as exc:  # noqa: BLE001
                inspection = {"error": str(exc)}

        candidates: list[str] = []
        rejected: list[tuple[str, str]] = []
        selected_spec: RendererSpec | None = None
        renderers = registered_renderers()

        if self.props.as_:
            for spec in renderers:
                if spec.name == self.props.as_:
                    selected_spec = spec
                    candidates.append(spec.name)
                    break
            if selected_spec is None:
                raise error(
                    "HED-AUTO-0001",
                    title="Unknown Auto renderer",
                    explanation=f"No renderer named {self.props.as_!r}.",
                    remediation=f"Known renderers: {[r.name for r in renderers]}",
                )
        else:
            for spec in renderers:
                candidates.append(spec.name)
                if spec.maturity == "experimental":
                    rejected.append(
                        (spec.name, "experimental renderer excluded from production Auto defaults")
                    )
                    continue
                matched = False
                if spec.predicate is not None:
                    try:
                        matched = bool(spec.predicate(value))
                    except Exception as exc:  # noqa: BLE001
                        rejected.append((spec.name, f"predicate error: {exc}"))
                        continue
                elif spec.types:
                    matched = isinstance(value, spec.types)
                if not matched:
                    rejected.append((spec.name, "type/predicate mismatch"))
                    continue
                selected_spec = spec
                break

        if selected_spec is None or selected_spec.factory is None:
            raise error(
                "HED-AUTO-0001",
                title="No Auto renderer matched",
                explanation=f"No renderer for value of type {type(value).__name__}.",
                remediation="Pass as_= explicitly or register a renderer.",
            )

        self._decision = AutoDecision(
            selected=selected_spec.name,
            candidates=tuple(candidates),
            rejected=tuple(rejected),
            inspection=inspection,
        )
        set_last_auto_decision(self._decision)
        self._resolved = selected_spec.factory(value)
        return self._resolved

    def render(self) -> NodeLike:
        # Return the resolved Component/NodeLike so the renderer owns identity,
        # cycle detection, and diagnostics (do not call child .render() here).
        return self.resolve()
