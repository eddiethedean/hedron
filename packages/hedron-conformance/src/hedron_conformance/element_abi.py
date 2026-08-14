"""Portable element ABI conformance fixtures (CONF-040)."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any

__all__ = ["load_element_abi_fixtures"]


def load_element_abi_fixtures() -> dict[str, Any]:
    target = resources.files("hedron_conformance").joinpath(
        "fixtures/element_abi/element_abi_v1.json"
    )
    return json.loads(target.read_text(encoding="utf-8"))
