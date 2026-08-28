from __future__ import annotations

import warnings
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast, overload

import pytest
from fastapi import FastAPI

from hedron import Hedron
from hedron.app.bootstrap import (
    HedronBootstrapConfig,
    HedronBootstrapContext,
    HedronBootstrapper,
    HedronBootstrapStep,
)
from hedron.security.policy import SecurityPolicy


def _config() -> HedronBootstrapConfig:
    return HedronBootstrapConfig(
        security="standard",
        explorer="off",
        session_secret="test-secret",
        enable_sessions=True,
        explorer_dependencies=(),
        theme="default",
        design_system=None,
        default_styles=True,
        build_dir=None,
        production=False,
        root_path=None,
    )


@dataclass
class _RecordingStep:
    name: str
    calls: list[str]

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        self.calls.append(self.name)
        app.state.last_bootstrap_step = self.name
        if self.name == "second":
            assert context.config.security == "standard"
            assert app.state.last_bootstrap_step == "second"


def test_bootstrapper_runs_injected_steps_in_order() -> None:
    calls: list[str] = []
    steps: tuple[HedronBootstrapStep, ...] = (
        _RecordingStep("first", calls),
        _RecordingStep("second", calls),
    )
    app = FastAPI()

    context = HedronBootstrapper(extension_steps=steps).bootstrap(app, _config())

    assert calls == ["first", "second"]
    assert context.config.security == "standard"
    assert context.policy is not None
    assert hasattr(app, "_root_router")
    assert app.state.last_bootstrap_step == "second"
    assert app.__dict__["_hedron_bootstrap_context"] is context


def test_empty_extension_pipeline_keeps_core_invariants() -> None:
    app = FastAPI()

    context = HedronBootstrapper(extension_steps=()).bootstrap(app, _config())

    assert context.policy is not None
    assert app.state.hedron_security is context.policy
    assert hasattr(app.state, "hedron_app_id")
    assert hasattr(app, "_root_router")


class _FalsySteps(Sequence[HedronBootstrapStep]):
    def __init__(self, step: HedronBootstrapStep) -> None:
        self.step = step

    def __bool__(self) -> bool:
        return False

    def __len__(self) -> int:
        return 1

    @overload
    def __getitem__(self, index: int) -> HedronBootstrapStep: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[HedronBootstrapStep]: ...

    def __getitem__(
        self, index: int | slice
    ) -> HedronBootstrapStep | Sequence[HedronBootstrapStep]:
        return (self.step,)[index]


def test_hedron_runs_falsy_extension_sequences_after_core_setup() -> None:
    calls: list[str] = []
    steps = _FalsySteps(_RecordingStep("extension", calls))

    app = Hedron(
        explorer="off",
        session_secret="test-secret",
        bootstrap_steps=steps,
    )

    assert calls == ["extension"]
    policy = cast(SecurityPolicy, app.__dict__["hedron_policy"])
    assert policy.profile.value == "standard"
    assert hasattr(app, "_root_router")


class _RemoveRouterStep:
    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        del context
        delattr(app, "_root_router")


def test_bootstrapper_rejects_extensions_that_break_core_invariants() -> None:
    with pytest.raises(RuntimeError, match="_root_router"):
        Hedron(
            explorer="off",
            session_secret="test-secret",
            bootstrap_steps=(_RemoveRouterStep(),),
        )


def test_constructor_warnings_point_to_application_call_site() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        Hedron(explorer="off")

    default_secret = next(
        warning
        for warning in caught
        if "default development session_secret" in str(warning.message)
    )
    assert Path(default_secret.filename).resolve() == Path(__file__).resolve()
