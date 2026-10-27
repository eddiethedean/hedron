"""Phase 1.2 release artifacts must cover the frozen package set reproducibly."""

from __future__ import annotations

import pytest

from scripts import verify_release_reproducibility as reproducibility


def test_expected_packages_follow_publish_order_and_exclude_native_lane() -> None:
    packages = reproducibility.expected_packages()

    assert len(packages) == 22
    assert "hedron-native" not in packages
    assert list(packages)[0] == "hedron-core"
    assert list(packages)[-1] == "edron-sim"


def test_reproducibility_requires_exact_wheel_and_sdist_set(tmp_path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    artifacts = {
        "hedron-1.2.0-py3-none-any.whl": b"wheel",
        "hedron-1.2.0.tar.gz": b"sdist",
    }
    for name, payload in artifacts.items():
        (first / name).write_bytes(payload)
        (second / name).write_bytes(payload)

    rows = reproducibility.compare_builds(first, second, packages={"hedron": "1.2.0"})

    assert [row["name"] for row in rows] == sorted(artifacts)
    (second / "hedron-1.2.0.tar.gz").write_bytes(b"changed")
    with pytest.raises(ValueError, match="non-reproducible artifact hashes"):
        reproducibility.compare_builds(first, second, packages={"hedron": "1.2.0"})


def test_reproducibility_rejects_missing_and_unexpected_artifacts(tmp_path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "hedron-1.2.0-py3-none-any.whl").write_bytes(b"wheel")
    (dist / "unapproved.whl").write_bytes(b"extra")

    with pytest.raises(ValueError, match="missing 1.2.0 source distribution"):
        reproducibility.artifact_inventory(dist, {"hedron": "1.2.0"})


def test_python310_evidence_is_bound_to_the_candidate_wheel() -> None:
    evidence = {
        "schema": "hedron.phase-120-python310-compatibility/1",
        "source_commit": "a" * 40,
        "python": "3.10.20",
        "candidate_install": "rejected by Requires-Python",
        "candidate_artifact": "hedron-1.2.0-py3-none-any.whl",
        "candidate_sha256": "b" * 64,
        "candidate_rejection_mentions_python_310_and_311": True,
        "unpinned_requirement": "hedron",
        "resolved_version": "1.1.3",
        "predecessor_version": "1.1.3",
        "platform": "Linux-6.8",
        "architecture": "x86_64",
    }
    artifacts: list[dict[str, str | int]] = [
        {
            "name": "hedron-1.2.0-py3-none-any.whl",
            "sha256": "b" * 64,
            "size": 10,
        }
    ]

    assert (
        reproducibility.validate_python310_evidence_data(
            evidence,
            source_commit="a" * 40,
            artifacts=artifacts,
            candidate_version="1.2.0",
        )
        == evidence
    )
    with pytest.raises(ValueError, match="not bound to the Hedron wheel"):
        reproducibility.validate_python310_evidence_data(
            {**evidence, "candidate_sha256": "c" * 64},
            source_commit="a" * 40,
            artifacts=artifacts,
            candidate_version="1.2.0",
        )


def test_upgrade_rollback_evidence_binds_candidate_wheels_and_restores_lock() -> None:
    evidence = {
        "schema": "hedron.phase-120-python311-upgrade-rollback/1",
        "source_commit": "a" * 40,
        "predecessor_version": "1.1.3",
        "candidate_version": "1.2.0",
        "python": "3.11.14",
        "platform": "Linux-6.8",
        "architecture": "x86_64",
        "baseline": {"result": "pass", "hedron": "1.1.3", "uv_lock_sha256": "c" * 64},
        "upgrade": {"result": "pass", "hedron": "1.2.0", "uv_lock_sha256": "d" * 64},
        "rollback": {
            "result": "pass",
            "hedron": "1.1.3",
            "uv_lock_sha256": "c" * 64,
            "restored_original_lock": True,
        },
        "candidate_artifacts": [
            {"name": "hedron-1.2.0-py3-none-any.whl", "sha256": "e" * 64},
            {"name": "hedron_core-1.2.0-py3-none-any.whl", "sha256": "f" * 64},
        ],
    }
    artifacts: list[dict[str, str | int]] = [
        {"name": "hedron-1.2.0-py3-none-any.whl", "sha256": "e" * 64, "size": 10},
        {"name": "hedron_core-1.2.0-py3-none-any.whl", "sha256": "f" * 64, "size": 10},
    ]

    assert (
        reproducibility.validate_upgrade_rollback_evidence_data(
            evidence,
            source_commit="a" * 40,
            artifacts=artifacts,
            predecessor_version="1.1.3",
            candidate_version="1.2.0",
        )
        == evidence
    )
    with pytest.raises(ValueError, match="does not show a candidate lock change"):
        reproducibility.validate_upgrade_rollback_evidence_data(
            {
                **evidence,
                "upgrade": {
                    **evidence["upgrade"],
                    "uv_lock_sha256": "c" * 64,
                },
            },
            source_commit="a" * 40,
            artifacts=artifacts,
            predecessor_version="1.1.3",
            candidate_version="1.2.0",
        )
