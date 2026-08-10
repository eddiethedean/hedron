from scripts.write_release_manifest import asset_record


def test_asset_record_contains_hash_size_and_name(tmp_path) -> None:
    path = tmp_path / "artifact.whl"
    path.write_bytes(b"hedron")
    record = asset_record(path, root=tmp_path)
    assert record == {
        "name": "artifact.whl",
        "source": "artifact.whl",
        "sha256": "4b99b3da56461c0d30c437791cc9194e9039e456f9aaed2d6b36f753fa4341ef",
        "size": 6,
    }
