"""SECURITY-058 evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from hedron import AuthDenied, AuthSuccess, DesignSystem, RateLimitPolicy, SessionAuthFlow
from hedron_core.codes import HED_BRAND_0001
from hedron_core.diagnostics import HedronError
from hedron_core.feature_explanation import explain_feature


def test_brand_rejects_injection_accent() -> None:
    for accent in (
        "red",
        "#2f6fed;background:url(x)",
        "url(javascript:alert(1))",
        "#gg0000",
        "expression(alert(1))",
    ):
        with pytest.raises(HedronError) as exc:
            DesignSystem.brand("inject", accent=accent)
        assert exc.value.diagnostic.code == HED_BRAND_0001


def test_eject_refuses_outside_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from hedron.cli.commands.eject import _cmd_eject_feature

    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    outside = tmp_path / "outside-eject"
    args = argparse.Namespace(
        component="features:demo",
        out=str(outside),
        force=False,
        app=None,
        surface=None,
    )
    code = _cmd_eject_feature(args)
    assert code == 1
    assert not outside.exists()


def test_form_command_explanation_omits_secrets() -> None:
    secret = "super-secret-password-value-xyz"

    class Creds(BaseModel):
        username: str = Field(min_length=1, max_length=80)
        password: str = Field(min_length=1, max_length=80)

    flow = SessionAuthFlow(
        credentials=Creds,
        authenticate=lambda creds: (
            AuthSuccess(principal=creds.username) if creds.password == secret else AuthDenied()
        ),
        serialize_principal=lambda principal: principal,
        load_principal=lambda stored: stored,
        rate_limit=RateLimitPolicy(limit=5, window_seconds=30.0),
    )
    plan = explain_feature(flow)
    blob = json.dumps(plan, default=str)
    assert secret not in blob
    assert plan["security"].get("redacted") is True
