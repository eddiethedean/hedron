"""FLOW-058 evidence."""

from __future__ import annotations

from fastapi import Depends
from pydantic import BaseModel, Field

from hedron import (
    AuthDenied,
    AuthSuccess,
    RateLimitPolicy,
    SessionAuthFlow,
    Text,
    UploadFlow,
)
from hedron.upload import UploadBudget, UploadField
from hedron_core.bundles import FeatureBundle


def test_session_auth_flow_to_bundle() -> None:
    class Creds(BaseModel):
        username: str = Field(min_length=1, max_length=80)
        password: str = Field(min_length=1, max_length=80)

    flow = SessionAuthFlow(
        credentials=Creds,
        authenticate=lambda creds: (
            AuthSuccess(principal=creds.username) if creds.password == "x" else AuthDenied()
        ),
        serialize_principal=lambda principal: principal,
        load_principal=lambda stored: stored,
        login_path="/login",
        logout_path="/logout",
        after_login="/",
        rate_limit=RateLimitPolicy(limit=10, window_seconds=60.0),
        rotation="on_login",
    )
    bundle = flow.to_bundle()
    assert isinstance(bundle, FeatureBundle)
    assert bundle.logical_id


def test_upload_flow_to_bundle() -> None:
    def allow() -> None:
        return None

    flow = UploadFlow(
        name="docs",
        field=UploadField(name="file", budget=UploadBudget(maximum_size=1_000_000)),
        authorize=Depends(allow),
        store=lambda handle: handle.accept(),
        result=lambda stored: Text(str(stored)),
    )
    bundle = flow.to_bundle()
    assert isinstance(bundle, FeatureBundle)
    assert bundle.logical_id
