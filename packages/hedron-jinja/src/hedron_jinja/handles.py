"""Optional HDJ bridge from templates to registered 0.43 handles."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from hedron_core.catalog import compile_interaction_catalog
from hedron_core.codes import HED_PROJECTION_0005, HED_UPDATE_0003
from hedron_core.diagnostics import error
from hedron_core.updates import BaseHandleDescriptor, list_handle_descriptors

__all__ = [
    "catalog_command_form",
    "catalog_view",
    "coerce_interaction_target",
    "list_feature_bundles",
    "resolve_registered_handle",
]


def list_feature_bundles(*, app_id: str | None = None) -> tuple[object, ...]:
    """Reviewable FeatureBundle facts for HDJ; not a production workflow store."""
    from hedron_core.bundles import included_bundles

    return included_bundles(app_id=app_id)


def resolve_registered_handle(
    logical_id: str,
    *,
    app_id: str | None = None,
) -> BaseHandleDescriptor:
    """Return a registered handle descriptor. String-only implicit routes are refused."""
    token = str(logical_id).strip()
    if not token or "/" in token or token.startswith("http"):
        raise error(
            HED_UPDATE_0003,
            title="HDJ handle references must be registered logical ids",
            explanation=f"{logical_id!r} is not a registered handle id.",
            remediation="Pass a handle.logical_id from @app.refreshable / @app.command.",
        )
    matches = [
        item
        for item in list_handle_descriptors(app_id=app_id)
        if item.logical_id == token or item.name == token
    ]
    if len(matches) != 1:
        raise error(
            HED_UPDATE_0003,
            title="HDJ handle is not registered",
            explanation=f"No unique registered handle for {token!r}.",
            remediation="Register the view/command before referencing it from HDJ.",
        )
    return matches[0]


def coerce_interaction_target(target: Any, *, app_id: str | None = None) -> Any:
    """Accept a handle, BoundFragment, or catalog logical id. Never execute a manifest dict."""
    if isinstance(target, Mapping):
        raise error(
            HED_PROJECTION_0005,
            title="Manifest dictionaries are not executable in templates",
            explanation="Jinja helpers refuse arbitrary catalog/manifest mappings.",
            remediation="Pass a registered handle, BoundFragment, or logical id.",
        )
    if isinstance(target, str):
        catalog = compile_interaction_catalog(app_id=app_id)
        catalog.require(target)
        return resolve_registered_handle(target, app_id=app_id)
    if hasattr(target, "handle") and hasattr(target, "logical_id"):
        return target
    if hasattr(target, "bind") or hasattr(target, "form") or hasattr(target, "logical_id"):
        return target
    raise error(
        HED_UPDATE_0003,
        title="Unknown HDJ interaction target",
        explanation=f"{type(target).__name__} is not a registered handle or logical id.",
        remediation="Pass FragmentHandle.bind, ActionHandle.form(), or a catalog logical id.",
    )


def catalog_view(target: Any, **bind_kwargs: Any) -> Any:
    """Bind a view through FragmentHandle.bind. Does not evaluate annotations."""
    handle = coerce_interaction_target(target)
    bind = getattr(handle, "bind", None)
    if callable(bind) and bind_kwargs:
        return bind(**bind_kwargs)
    if hasattr(handle, "handle") and not bind_kwargs:
        return handle
    raise error(
        HED_PROJECTION_0005,
        title="Jinja view helper requires a FragmentHandle or BoundFragment",
        explanation="Logical ids resolve to descriptors, which cannot reconstruct bind kwargs.",
        remediation="Pass user_card.bind(user_id=...) from Python into the template.",
    )


def catalog_command_form(
    target: Any,
    *,
    fields: Sequence[Any] | None = None,
    **form_kwargs: Any,
) -> Any:
    """Opt-in ActionHandle.form() or explicit Form(action=handle)."""
    handle = coerce_interaction_target(target)
    form_fn = getattr(handle, "form", None)
    if callable(form_fn):
        if fields is not None:
            form_kwargs.setdefault("controls", {"fields": list(fields)})
        try:
            return form_fn(**form_kwargs)
        except TypeError:
            return form_fn()
    from hedron_core.builtins import Form

    return Form(action=handle, **form_kwargs)
