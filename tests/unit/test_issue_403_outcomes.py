"""#403: OutcomeMap.validate_union unwraps Annotated discriminators."""

from __future__ import annotations

from typing import Annotated, Literal

import pytest
from pydantic import BaseModel, Field

from hedron.type_authoring.outcomes import OutcomeMap, case
from hedron_core.builtins import Text
from hedron_core.codes import HED_TYPE_0007
from hedron_core.diagnostics import HedronError


class Saved(BaseModel):
    kind: Literal["saved"] = "saved"
    id: str


class Conflict(BaseModel):
    kind: Literal["conflict"] = "conflict"


SaveOutcome = Annotated[Saved | Conflict, Field(discriminator="kind")]


def test_annotated_union_incomplete_map_fails_closed() -> None:
    incomplete = OutcomeMap(case(Saved, render=lambda item: Text(item.id)))
    with pytest.raises(HedronError) as exc:
        incomplete.validate_union(SaveOutcome)
    assert exc.value.diagnostics[0].code == HED_TYPE_0007


def test_annotated_union_complete_map_passes() -> None:
    mapping = OutcomeMap(
        case(Saved, render=lambda item: Text(item.id)),
        case(Conflict, render=lambda item: Text("no"), status=409),
    )
    mapping.validate_union(SaveOutcome)
