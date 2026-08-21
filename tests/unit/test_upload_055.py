"""UPLOAD-055 evidence."""

from __future__ import annotations

import pytest

from hedron.upload import UploadBudget, cleanup_upload, materialize_upload


def test_issue_549_limits_and_cleanup() -> None:
    handle = materialize_upload(
        filename="notes.txt",
        content=b"hello",
        budget=UploadBudget(maximum_size=100, allowed_extensions=(".txt",)),
    )
    path = handle.path
    assert path.is_file()
    cleanup_upload(handle)
    assert not path.exists()

    with pytest.raises(ValueError):
        materialize_upload(
            filename="../etc/passwd",
            content=b"x",
            budget=UploadBudget(),
        )

    with pytest.raises(ValueError):
        materialize_upload(
            filename="big.bin",
            content=b"x" * 10,
            budget=UploadBudget(maximum_size=5),
        )
