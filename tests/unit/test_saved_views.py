from hedron_data.views import SavedView


def test_saved_view_roundtrip() -> None:
    view = SavedView(
        name="default",
        scope="user",
        columns=("id", "name"),
        filters={"status": "open"},
        sort=(("name", "asc"),),
        selection=("1",),
        owner_id="u1",
    ).validated()
    data = view.serialize()
    restored = SavedView.deserialize(data)
    assert restored.name == "default"
    assert restored.columns == ("id", "name")
