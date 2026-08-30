"""Phase 0.8 Edron deployment, host, edge, artifact, and recovery contracts."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

import edron as ed
from edron.cli import main
from edron.deployment import DeploymentError, artifact_manifest, check_deployment


def test_edron_run_preserves_import_target_for_reload(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    cli_module = importlib.import_module("edron.cli.main")
    calls: list[tuple[object, dict[str, object]]] = []
    monkeypatch.setattr("uvicorn.run", lambda target, **kwargs: calls.append((target, kwargs)))
    monkeypatch.setattr(
        cli_module,
        "load_application",
        lambda target: pytest.fail(f"reload unexpectedly imported {target}"),
    )

    assert main(["run", "app:app", "--reload"]) == 0
    assert calls == [("app:app", {"host": "127.0.0.1", "port": 8000, "reload": True})]

    assert main(["run", "app.py", "--reload"]) == 1
    assert "--reload requires an import target such as app:app" in capsys.readouterr().err


def test_profiles_are_explicit_and_aliases_are_canonical() -> None:
    assert ed.resolve_deployment_profile("proxy", environ={}).profile.name == "reverse-proxy"
    assert ed.resolve_deployment_profile(profile="local", environ={}).profile.name == "local"
    assert ed.DeploymentProfile.from_name("local").name == "local"
    container = ed.DeploymentProfile.for_name("container")
    assert container.bind == "0.0.0.0"
    assert container.allow_external_bind is True
    assert container.to_mapping()["schema"] == "edron.deployment-profile/1"


def test_profile_conflicts_fail_closed_without_importing_an_app() -> None:
    report = check_deployment(
        "local",
        environ={"EDRON_DEPLOYMENT_PROFILE": "container"},
    )
    assert not report.ok
    assert any(item.code == "EDR-08-PROFILE-CONFLICT" for item in report.diagnostics.diagnostics)


def test_proxy_and_public_url_boundaries_are_validated(tmp_path: Path) -> None:
    with pytest.raises(DeploymentError, match="credentials"):
        ed.DeploymentProfile.for_name(
            "reverse-proxy",
            root_path="/sales",
            external_url="https://user:pass@example.test/sales",
        )
    build = tmp_path / ".hedron" / "build"
    build.mkdir(parents=True)
    (build / "manifest.json").write_text('{"digest":"abc"}', encoding="utf-8")
    report = check_deployment(
        "reverse-proxy",
        environ={
            "HEDRON_SESSION_SECRET": "runtime-only",
            "HEDRON_ROOT_PATH": "/sales",
            "HEDRON_EXTERNAL_BASE_URL": "https://apps.example.test/sales",
            "HEDRON_TRUST_PROXY": "10.0.0.10,10.0.0.0/24",
        },
        cwd=tmp_path,
    )
    assert report.profile.root_path == "/sales"
    assert report.profile.trust_proxy == ("10.0.0.10", "10.0.0.0/24")
    assert not any(item.severity == "error" for item in report.diagnostics.diagnostics)


def test_production_requires_manifest_and_secret_but_local_does_not(tmp_path: Path) -> None:
    local = check_deployment("local", environ={}, cwd=tmp_path)
    assert local.ok
    production = check_deployment(
        "single-process",
        environ={},
        cwd=tmp_path,
    )
    codes = {item.code for item in production.diagnostics.diagnostics}
    assert {"EDR-08-BUILD-0001", "EDR-08-SECURITY-0001"} <= codes

    build = tmp_path / ".hedron" / "build"
    build.mkdir(parents=True)
    (build / "manifest.json").write_text('{"digest":"abc"}', encoding="utf-8")
    ready = check_deployment(
        "single-process",
        environ={"HEDRON_SESSION_SECRET": "runtime-only"},
        cwd=tmp_path,
    )
    assert ready.ok, ready.to_mapping()
    platform_secret = check_deployment(
        "single-process",
        environ={},
        cwd=tmp_path,
        overrides={"secret_source": "vault://edron/session"},
    )
    assert platform_secret.ok, platform_secret.to_mapping()


def test_multi_worker_profiles_require_shared_native_backends() -> None:
    report = check_deployment(
        "orchestrated",
        environ={"HEDRON_SESSION_SECRET": "runtime-only"},
        overrides={"workers": 2},
    )
    codes = {item.code for item in report.diagnostics.diagnostics}
    assert {"EDR-08-BUILD-0001", "EDR-08-OPS-0001", "EDR-08-OPS-0002"} <= codes

    shared = check_deployment(
        "orchestrated",
        environ={"HEDRON_SESSION_SECRET": "runtime-only"},
        overrides={
            "workers": 2,
            "state_backend": "shared",
            "job_backend": "shared",
        },
    )
    assert not any(item.code.startswith("EDR-08-OPS-") for item in shared.diagnostics.diagnostics)


def test_app_deployment_report_is_inert_and_redacted() -> None:
    app = ed.App(title="phase08", session_secret="test-secret")
    report = app.deployment(environ={}, cwd=Path.cwd())
    assert report.profile.name == "local"
    assert "test-secret" not in json.dumps(report.to_mapping())
    assert app.operations()["deployment"]["schema"] == "edron.deployment-report/1"


def test_artifact_manifest_is_bounded_deterministic_and_root_contained(tmp_path: Path) -> None:
    first = tmp_path / "a.whl"
    second = tmp_path / "b.tar.gz"
    first.write_bytes(b"wheel")
    second.write_bytes(b"sdist")
    manifest = artifact_manifest([second, first], version="0.8.0", root=tmp_path)
    assert manifest["schema"] == "edron.artifact-manifest/1"
    assert [row["name"] for row in manifest["artifacts"]] == ["a.whl", "b.tar.gz"]
    assert len(manifest["fingerprint"]) == 32
    outside = tmp_path.parent / "outside.whl"
    outside.write_bytes(b"outside")
    with pytest.raises(DeploymentError, match="beneath"):
        artifact_manifest([outside], version="0.8.0", root=tmp_path)


def test_deploy_check_cli_is_json_and_does_not_import_an_application(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["deploy-check", "--profile", "local", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"] == "edron.deployment-report/1"
    assert payload["profile"]["name"] == "local"
    assert payload["ok"] is True
