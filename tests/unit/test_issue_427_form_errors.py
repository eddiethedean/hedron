"""#427: generate_form includes model-level validation errors."""

from hedron.type_authoring.forms import _error_map


def test_error_map_keeps_model_level_errors() -> None:
    field_errors, model_errors = _error_map([{"loc": (), "msg": "fields must match"}])
    assert field_errors == {}
    assert model_errors == ["fields must match"]
