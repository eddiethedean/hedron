"""Positive typing fixture: modeled bind overloads without a plugin."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel

from hedron import BoundFragment, FragmentHandle, Text, ViewParams


class Params(BaseModel):
    user_id: UUID


def accept_handle(handle: FragmentHandle[Params, Text]) -> BoundFragment[Text]:
    return handle.bind(Params(user_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")))


def accept_fields(handle: FragmentHandle[Params, Text]) -> BoundFragment[Text]:
    return handle.bind(user_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"))


def annotated_ok(params: Annotated[Params, ViewParams()]) -> Params:
    return params
