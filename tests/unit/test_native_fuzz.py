"""Memory-safety / adversarial fuzz-style coverage for native escaping."""

from __future__ import annotations

import random

from hedron_native import escape_attr, escape_attr_python, escape_text, escape_text_python


def test_fuzz_escape_parity_random_strings() -> None:
    rng = random.Random(14)
    alphabet = "<>&\"'\x00abcXYZ /\\"
    for _ in range(200):
        sample = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 64)))
        assert escape_text(sample) == escape_text_python(sample)
        assert escape_attr(sample) == escape_attr_python(sample)
