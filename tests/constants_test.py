"""Tests for ``auto-file-sorter.constants``."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from auto_file_sorter.constants import (
    CONFIG_LOG_LEVEL,
    DEFAULT_CONFIGS_LOCATION,
    DEFAULT_LOG_LOCATION,
    EXIT_FAILURE,
    EXIT_SUCCESS,
    FILE_EXTENSION_PATTERN,
    LOG_FORMAT,
    MAX_VERBOSITY_LEVEL,
    MOVE_LOG_LEVEL,
    PROGRAM_LOCATION,
    STREAM_HANDLER_FORMATTER,
    VERBOSE_OUTPUT_LEVELS,
)

if TYPE_CHECKING:
    from pathlib import Path

# pylint: disable=C0116, W0212


@pytest.mark.parametrize(
    ("constant", "expected_value"),
    (
        pytest.param(CONFIG_LOG_LEVEL, 70, id="CONFIG_LOG_LEVEL"),
        pytest.param(MOVE_LOG_LEVEL, 60, id="MOVE_LOG_LEVEL"),
        pytest.param(
            LOG_FORMAT,
            "%(name)s [%(levelname)s] %(asctime)s - %(message)s",
            id="LOG_FORMAT",
        ),
        pytest.param(MAX_VERBOSITY_LEVEL, 3, id="MAX_VERBOSITY_LEVEL"),
        pytest.param(EXIT_SUCCESS, 0, id="EXIT_SUCCESS"),
        pytest.param(EXIT_FAILURE, 1, id="EXIT_FAILURE"),
        pytest.param(
            STREAM_HANDLER_FORMATTER._fmt,
            "[%(levelname)s] %(message)s",
            id="STREAM_HANDLER_FORMATTER",
        ),
        pytest.param(
            VERBOSE_OUTPUT_LEVELS,
            {1: 30, 2: 20, 3: 10},
            id="VERBOSE_OUTPUT_LEVELS",
        ),
    ),
)
def test_value_of_constant(
    constant: int | str | dict[int, int],
    expected_value: int | str | dict[int, int],
) -> None:
    assert constant == expected_value


@pytest.mark.parametrize(
    "location",
    (
        pytest.param(PROGRAM_LOCATION, id="PROGRAM_LOCATION"),
        pytest.param(DEFAULT_CONFIGS_LOCATION, id="CONFIGS_LOCATION"),
        pytest.param(DEFAULT_LOG_LOCATION, id="DEFAULT_LOG_LOCATION"),
    ),
)
def test_location_is_absolute(location: Path) -> None:
    assert location.is_absolute()


@pytest.mark.parametrize(
    "default_file",
    (
        pytest.param(DEFAULT_CONFIGS_LOCATION, id="CONFIGS_LOCATION"),
        pytest.param(DEFAULT_LOG_LOCATION, id="DEFAULT_LOG_LOCATION"),
    ),
)
def test_default_file_is_under_program_location(default_file: Path) -> None:
    assert default_file.relative_to(PROGRAM_LOCATION)


def test_default_files_common_parent_is_program() -> None:
    assert (
        DEFAULT_CONFIGS_LOCATION.parent
        == DEFAULT_LOG_LOCATION.parent
        == PROGRAM_LOCATION
    )


@pytest.mark.parametrize(
    ("default_file", "file_name"),
    (
        pytest.param(DEFAULT_CONFIGS_LOCATION, "configs.json", id="CONFIGS_LOCATION"),
        pytest.param(
            DEFAULT_LOG_LOCATION,
            "auto-file-sorter.log",
            id="DEFAULT_LOG_LOCATION",
        ),
    ),
)
def test_default_file_name(default_file: Path, file_name: str) -> None:
    assert default_file.name == file_name


@pytest.mark.parametrize(
    "extension",
    (
        pytest.param(".TXT"),
        pytest.param(".zip"),
        pytest.param(".7z"),
        pytest.param(".123"),
        pytest.param(".PnG"),
        pytest.param(".Jp2"),
    ),
)
def test_file_extension_pattern_valid_extension(extension: str) -> None:
    assert FILE_EXTENSION_PATTERN.fullmatch(extension) is not None


@pytest.mark.parametrize(
    "extension",
    (
        pytest.param("TXT"),
        pytest.param("zip"),
        pytest.param("_7z_"),
        pytest.param("-123"),
        pytest.param(".PnG!"),
        pytest.param(".Jp2@"),
        pytest.param("/doc"),
        pytest.param(""),
    ),
)
def test_file_extension_pattern_invalid_extension(extension: str) -> None:
    assert FILE_EXTENSION_PATTERN.fullmatch(extension) is None
