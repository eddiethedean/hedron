"""Optional HDJ bridge from templates to registered 0.43 handles."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from hedron_core.catalog import compile_interaction_catalog
from hedron_core.codes import HED_PROJECTION_0005, HED_UPDATE_0003
from hedron_core.diagnostics import error
from hedron_core.updates import BaseHandleDescriptor, list_handle_descriptors

if TYPE_CHECKING:
    from hedron_jinja.binding import JinjaBinding

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
            remediation="Pass a handle.logical_id from @app.view / @app.action.",
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


def coerce_interaction_target(
    target: Any,
    *,
    app_id: str | None = None,
    binding: JinjaBinding | None = None,
) -> Any:
    """Accept a handle, BoundFragment, or catalog logical id. Never execute a manifest dict."""
    if isinstance(target, Mapping):
        raise error(
            HED_PROJECTION_0005,
            title="Manifest dictionaries are not executable in templates",
            explanation="Jinja helpers refuse arbitrary catalog/manifest mappings.",
            remediation="Pass a registered handle, BoundFragment, or logical id.",
        )
    if isinstance(target, str):
        if binding is not None:
            return binding.resolve_handle(target)
        catalog = compile_interaction_catalog(app_id=app_id)
        catalog.require(target)
        return resolve_registered_handle(target, app_id=app_id)
    if binding is not None:
        logical_id = getattr(target, "logical_id", None)
        if not isinstance(logical_id, str):
            raise error(
                HED_UPDATE_0003,
                title="HDJ app-bound interaction target is not registered",
                explanation="An app-bound target has no canonical logical_id.",
                remediation="Pass a logical ID present in JinjaBinding.handles.",
            )
        return binding.resolve_handle(logical_id)
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


def catalog_view(
    target: Any,
    *,
    binding: JinjaBinding | None = None,
    app_id: str | None = None,
    **bind_kwargs: Any,
) -> Any:
    """Bind a view through FragmentHandle.bind. Does not evaluate annotations."""
    handle = coerce_interaction_target(target, app_id=app_id, binding=binding)
    bind = getattr(handle, "bind", None)
    if callable(bind) and bind_kwargs:
        return bind(**bind_kwargs)
    if hasattr(handle, "handle") and not bind_kwargs:
        return handle
    binding_plan = getattr(handle, "binding_plan", None)
    if callable(handle) and not bind_kwargs and not getattr(binding_plan, "required", ()):
        return handle
    raise error(
        HED_PROJECTION_0005,
        title="Jinja view helper requires a FragmentHandle or BoundFragment",
        explanation="The selected view requires explicit binding parameters.",
        remediation="Pass the required named parameters to h_view(...).",
    )


def catalog_command_form(
    target: Any,
    *,
    fields: Sequence[Any] | None = None,
    binding: JinjaBinding | None = None,
    app_id: str | None = None,
    **form_kwargs: Any,
) -> Any:
    """Opt-in ActionHandle.form() or explicit Form(action=handle)."""
    handle = coerce_interaction_target(target, app_id=app_id, binding=binding)
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
