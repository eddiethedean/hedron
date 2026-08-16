"""Flask TypeSchema disposition (TA-QUAL-003): bounded exception, no FastAPI DI."""

from __future__ import annotations

from hedron_core.codes import HED_TYPE_0009
from hedron_core.diagnostics import error

__all__ = ["refuse_fastapi_type_authoring"]


def refuse_fastapi_type_authoring(*, feature: str = "ViewParams/FormBody") -> None:
    """Fail closed when FastAPI-only type-driven request parsing is requested."""
    raise error(
        HED_TYPE_0009,
        title="Type-driven authoring is not emulated on Flask",
        explanation=(
            f"{feature} request binding requires FastAPI DI; hedron-flask does not emulate it."
        ),
        remediation="Consume portable TypeSchema/results or run the FastAPI flagship.",
    )
