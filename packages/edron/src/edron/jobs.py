from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from hedron import TaskFlow
from hedron.jobs.scope import JobScope
from hedron_core.jobs import JobBackend

__all__ = ["JobBackend", "JobFlow", "JobScope"]


class JobFlow:
    """Thin Edron constructor for native Hedron task flows."""

    def __init__(
        self,
        *,
        name: str,
        input_model: type[Any],
        job_type: str,
        payload: Callable[[Any], Mapping[str, Any]],
        backend: Any,
        scope: Any,
        result: Callable[..., Any],
        authorize_submit: Any = None,
        authorize_cancel: Any = None,
        poll_interval_ms: int = 2000,
    ) -> None:
        self.name = name
        self.input_model = input_model
        self.job_type = job_type
        self.payload = payload
        self.backend = backend
        self.scope = scope
        self.result = result
        self.authorize_submit = authorize_submit
        self.authorize_cancel = authorize_cancel
        self.poll_interval_ms = poll_interval_ms

    def to_bundle(self) -> Any:
        native = TaskFlow(
            name=self.name,
            input_model=self.input_model,
            job_type=self.job_type,
            payload=self.payload,
            scope=self.scope,
            authorize_submit=self.authorize_submit,
            authorize_cancel=self.authorize_cancel,
            result=self.result,
        )
        return native.to_bundle()
