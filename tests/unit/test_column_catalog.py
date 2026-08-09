from hedron_data.columns import Column, display_for_editor, write_policy


def test_display_catalog_and_write_policy() -> None:
    col = Column(name="url", editor="link", display="link", writable=False)
    schema = col.to_schema()
    assert schema.display == "link"
    assert write_policy(col) is False
    assert display_for_editor("progress") == "progress"
    # display never implies writable; unset writable denies by default
    shown = Column(name="img", display="image")
    assert write_policy(shown) is False
    assert write_policy(Column(name="img", display="image", writable=True)) is True
    assert write_policy(Column(name="s", secret=True, display="text")) is False
