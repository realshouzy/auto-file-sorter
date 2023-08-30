"""Tests for ``auto-file-sorter.main``."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

# pylint: disable=C0116, W0611
from auto_file_sorter import __version__
from auto_file_sorter.args_handling import resolved_path_from_str
from auto_file_sorter.main import _parse_args

# valid_json_data and test_configs are indirectly used by test_configs_as_str, do not remove!
from tests.fixtures import (
    test_configs,
    test_configs_as_str,
    test_log_as_str,
    valid_json_data,
)

if TYPE_CHECKING:
    import argparse
    from pathlib import Path


@pytest.mark.parametrize(
    "argv",
    (
        pytest.param(["--version"], id="--version"),
        pytest.param(["-V"], id="-V"),
    ),
)
def test_parse_args_version(
    argv: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        _parse_args(argv)
    assert capsys.readouterr().out == f"auto-file-sorter {__version__}\n"


@pytest.mark.parametrize(
    "argv",
    (
        pytest.param(["--debug", "locations"], id="--debug"),
        pytest.param(["-d", "locations"], id="-d"),
    ),
)
def test_parse_args_debugging(argv: list[str]) -> None:
    args: argparse.Namespace = _parse_args(argv)
    assert args.debugging


@pytest.mark.parametrize(
    ("argv", "expected_verbosity_level"),
    (
        pytest.param(["--verbose", "locations"], 1, id="--verbose"),
        pytest.param(
            ["--verbose", "--verbose", "locations"],
            2,
            id="--verbose --verbose",
        ),
        pytest.param(
            ["--verbose", "--verbose", "--verbose", "locations"],
            3,
            id="--verbose --verbose --verbose",
        ),
        pytest.param(["-v", "locations"], 1, id="-v"),
        pytest.param(["-vv", "locations"], 2, id="-vv"),
        pytest.param(["-vvv", "locations"], 3, id="-vvv"),
        pytest.param(["-vvvv", "locations"], 4, id="-vvvv"),
    ),
)
def test_parse_args_verbosity_level(
    argv: list[str],
    expected_verbosity_level: int,
) -> None:
    args: argparse.Namespace = _parse_args(argv)
    assert args.verbosity_level == expected_verbosity_level


def test_parse_args_log_location(test_log_as_str: str) -> None:
    args: argparse.Namespace = _parse_args(
        ["--log-location", test_log_as_str, "locations"],
    )
    assert args.log_location == resolved_path_from_str(test_log_as_str)


def test_parse_args_configs_location(test_configs_as_str: str) -> None:
    args: argparse.Namespace = _parse_args(
        ["--configs-location", test_configs_as_str, "locations"],
    )
    assert args.configs_location == resolved_path_from_str(test_configs_as_str)


@pytest.mark.parametrize(
    ("argv", "get_log_location_val", "get_configs_location_val"),
    (
        pytest.param(["locations", "--log"], True, False, id="--log"),
        pytest.param(["locations", "-l"], True, False, id="-l"),
    ),
)
def test_parse_args_locations(
    argv: list[str],
    get_log_location_val: bool,
    get_configs_location_val: bool,
) -> None:
    args: argparse.Namespace = _parse_args(argv)
    assert args.get_log_location is get_log_location_val
    assert args.get_configs_location is get_configs_location_val
