"""DESCRIPTOR-051 ExtrasFeature authority."""

from __future__ import annotations

from hedron_extras.descriptor import ExtrasFeature, extras_features


def test_extras_feature_fields_and_no_core_fork() -> None:
    fields = set(ExtrasFeature.__dataclass_fields__)
    for required in (
        "name",
        "component_tag",
        "python_facade",
        "schemas",
        "events",
        "assets",
        "optional_dependencies",
        "fallback",
        "limits",
        "maturity",
        "accessibility_contract",
        "explorer_projection",
        "jinja_projection",
        "conformance_projection",
    ):
        assert required in fields
    import hedron_core

    assert not hasattr(hedron_core, "ExtrasFeature")
    workbench = next(f for f in extras_features() if f.name == "workbench")
    assert workbench.maturity == "beta"
    recipes = next(f for f in extras_features() if f.name == "recipes")
    assert recipes.maturity == "recipe"
