"""Tests for ``auto-file-sorter.main``."""
from __future__ import annotations

import argparse
import logging
import sys
from typing import TYPE_CHECKING

import pytest

# pylint: disable=C0116, W0611
from auto_file_sorter import __version__
from auto_file_sorter.args_handling import resolved_path_from_str
from auto_file_sorter.constants import (
    CONFIG_LOG_LEVEL,
    DEFAULT_CONFIGS_LOCATION,
    DEFAULT_LOG_LOCATION,
    MOVE_LOG_LEVEL,
)
from auto_file_sorter.main import (
    _check_specified_locations,
    _parse_args,
    _setup_logging,
)

# valid_json_data and test_configs are indirectly used by test_configs_as_str, do not remove!
from tests.fixtures import (
    info_caplog,
    test_configs,
    test_configs_as_str,
    test_log_as_str,
    valid_json_data,
)

if TYPE_CHECKING:
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


@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="logging.getLevelNamesMapping() added in Python 3.11",
)
def test_setup_logging_custom_log_level() -> None:  # pragma: >=3.11 cover
    args: argparse.Namespace = argparse.Namespace(
        log_location=resolved_path_from_str("test.log"),
        verbosity_level=0,
        debugging=False,
    )
    _setup_logging(args)

    # pylint: disable=E1101
    assert logging.getLevelNamesMapping().get("MOVE") == MOVE_LOG_LEVEL
    assert logging.getLevelNamesMapping().get("CONFIG") == CONFIG_LOG_LEVEL


@pytest.mark.parametrize(("log_location"), [0, 1, 2])
def test_setup_logging_no_warnings_no_debugging(
    log_location: int,
    info_caplog: pytest.LogCaptureFixture,
) -> None:
    test_log_location: Path = resolved_path_from_str("test.log")
    args: argparse.Namespace = argparse.Namespace(
        log_location=test_log_location,
        verbosity_level=log_location,
        debugging=False,
    )
    _setup_logging(args)

    assert info_caplog.record_tuples == [
        (
            "auto_file_sorter.main",
            20,
            f"Started logging at '{test_log_location}' with level 20",
        ),
    ]


@pytest.mark.parametrize(("log_location"), [0, 1, 2])
def test_setup_logging_no_warnings_debugging(
    log_location: int,
    info_caplog: pytest.LogCaptureFixture,
) -> None:
    test_log_location: Path = resolved_path_from_str("test.log")
    args: argparse.Namespace = argparse.Namespace(
        log_location=test_log_location,
        verbosity_level=log_location,
        debugging=True,
    )
    _setup_logging(args)

    assert info_caplog.record_tuples == [
        (
            "auto_file_sorter.main",
            20,
            f"Started logging at '{test_log_location}' with level 10",
        ),
    ]


def test_setup_logging_verbosity_debugging(
    info_caplog: pytest.LogCaptureFixture,
) -> None:
    test_log_location: Path = resolved_path_from_str("test.log")
    args: argparse.Namespace = argparse.Namespace(
        log_location=test_log_location,
        verbosity_level=4,
        debugging=True,
    )
    _setup_logging(args)

    assert info_caplog.record_tuples == [
        (
            "auto_file_sorter.main",
            30,
            "Maximum verbosity level exceeded. Using maximum level of 3.",
        ),
        (
            "auto_file_sorter.main",
            20,
            f"Started logging at '{test_log_location}' with level 10",
        ),
    ]


def test_setup_logging_verbosity_no_debugging(
    info_caplog: pytest.LogCaptureFixture,
) -> None:
    test_log_location: Path = resolved_path_from_str("test.log")
    args: argparse.Namespace = argparse.Namespace(
        log_location=test_log_location,
        verbosity_level=4,
        debugging=False,
    )
    _setup_logging(args)

    assert info_caplog.record_tuples == [
        (
            "auto_file_sorter.main",
            30,
            "Maximum verbosity level exceeded. Using maximum level of 3.",
        ),
        (
            "auto_file_sorter.main",
            30,
            "Using maximum verbosity level, but debugging is disabled. "
            "To get the full output add the '-d' flag to enable debugging",
        ),
        (
            "auto_file_sorter.main",
            20,
            f"Started logging at '{test_log_location}' with level 20",
        ),
    ]


def test_check_specified_locations_valid_file_types(
    caplog: pytest.LogCaptureFixture,
) -> None:
    args: argparse.Namespace = argparse.Namespace(
        log_location=resolved_path_from_str("test.log"),
        configs_location=resolved_path_from_str("configs.json"),
    )
    _check_specified_locations(args)

    assert caplog.record_tuples == []


def test_check_specified_locations_invalid_log_file_type(
    caplog: pytest.LogCaptureFixture,
) -> None:
    args: argparse.Namespace = argparse.Namespace(
        log_location=resolved_path_from_str("test.txt"),
        configs_location=resolved_path_from_str("configs.json"),
    )
    _check_specified_locations(args)

    assert caplog.record_tuples == [
        (
            "auto_file_sorter.main",
            30,
            "Given logging location is not a '.log' file. "
            f"Using default location: '{DEFAULT_LOG_LOCATION}'",
        ),
    ]


def test_check_specified_locations_invalid_configs_file_type(
    caplog: pytest.LogCaptureFixture,
) -> None:
    args: argparse.Namespace = argparse.Namespace(
        log_location=resolved_path_from_str("test.log"),
        configs_location=resolved_path_from_str("configs.yaml"),
    )
    _check_specified_locations(args)

    assert caplog.record_tuples == [
        (
            "auto_file_sorter.main",
            30,
            "Given configs location is not a '.json' file. "
            f"Using default location: '{DEFAULT_CONFIGS_LOCATION}'",
        ),
    ]


def test_check_specified_locations_both_invalid_file_types(
    caplog: pytest.LogCaptureFixture,
) -> None:
    args: argparse.Namespace = argparse.Namespace(
        log_location=resolved_path_from_str("test"),
        configs_location=resolved_path_from_str("configs"),
    )
    _check_specified_locations(args)

    assert caplog.record_tuples == [
        (
            "auto_file_sorter.main",
            30,
            "Given logging location is not a '.log' file. "
            f"Using default location: '{DEFAULT_LOG_LOCATION}'",
        ),
        (
            "auto_file_sorter.main",
            30,
            "Given configs location is not a '.json' file. "
            f"Using default location: '{DEFAULT_CONFIGS_LOCATION}'",
        ),
    ]
