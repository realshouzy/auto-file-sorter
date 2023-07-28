"""Module testing the Module Level Dunder Names in ``auto_file_sorter.__init__.py``."""
from __future__ import annotations

import pytest

from auto_file_sorter import __author__, __copyright__, __license__, __title__

# pylint: disable=C0116


@pytest.mark.parametrize(
    ("module_dunder_names", "expected_value"),
    (
        pytest.param(__author__, "realshouzy", id="author"),
        pytest.param(
            __copyright__,
            "Copyright (c) 2022-present realshouzy",
            id="copyright",
        ),
        pytest.param(
            __license__,
            "MIT",
            id="license",
        ),
        pytest.param(__title__, "auto-file-sorter", id="title"),
    ),
)
def test_constants(module_dunder_names: str, expected_value: str) -> None:
    assert module_dunder_names == expected_value
