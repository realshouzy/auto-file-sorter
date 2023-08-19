"""Tests for ``auto-file-sorter.configs_handling``."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

# pylint: disable=C0116, W0611, W0621
from auto_file_sorter.configs_handling import read_from_configs, write_to_configs
from tests.fixtures import (
    empty_test_configs,
    invalid_json_data,
    invalid_test_configs,
    test_configs,
    valid_json_data,
)

if TYPE_CHECKING:
    from pathlib import Path

# pylint: disable=C0116, W0621


def test_read_from_configs(
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, test_configs_data = test_configs

    result: dict[str, str] = read_from_configs(configs=test_configs_file)
    assert result == test_configs_data

    assert caplog.record_tuples == [
        ("auto_file_sorter.configs_handling", 70, f"Read from {test_configs_file}"),
    ]


def test_read_from_configs_no_file(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file: Path = tmp_path / "nonexistent_configs.json"

    assert not test_configs_file.exists()

    with pytest.raises(SystemExit):
        read_from_configs(configs=test_configs_file)

    assert test_configs_file.exists()

    configs: dict[str, str] = json.loads(test_configs_file.read_text(encoding="utf-8"))
    assert configs == {}

    assert caplog.record_tuples == [
        (
            "auto_file_sorter.configs_handling",
            50,
            f"Unable to find '{test_configs_file}', falling back to an empty configuration",
        ),
        (
            "auto_file_sorter.configs_handling",
            70,
            f"Added new extension configuration {{}} to '{test_configs_file}'",
        ),
    ]


def test_read_from_configs_invalid_json(
    invalid_test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = invalid_test_configs

    with pytest.raises(SystemExit):
        read_from_configs(configs=test_configs_file)

    assert caplog.record_tuples == [
        (
            "auto_file_sorter.configs_handling",
            50,
            f"Given JSON file is not correctly formatted: '{test_configs_file}'",
        ),
    ]


def test_write_to_configs(
    empty_test_configs: Path,
    valid_json_data: dict[str, str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    write_to_configs(valid_json_data, configs=empty_test_configs)

    result = json.loads(empty_test_configs.read_text(encoding="utf-8"))
    assert result == valid_json_data

    assert caplog.record_tuples == [
        (
            "auto_file_sorter.configs_handling",
            70,
            f"Added new extension configuration {valid_json_data} to '{empty_test_configs}'",
        ),
    ]


def test_write_to_configs_invalid_json(
    empty_test_configs: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    unserializable_data: set[int] = {1, 2, 3}

    with pytest.raises(SystemExit):
        write_to_configs(unserializable_data, configs=empty_test_configs)  # type: ignore[arg-type]

    assert caplog.record_tuples == [
        (
            "auto_file_sorter.configs_handling",
            50,
            f"Given configs can not be serialized into a JSON formatted: {unserializable_data}",
        ),
    ]


def test_write_to_configs_nonexistent_configs(
    valid_json_data: dict[str, str],
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file: Path = tmp_path / "nonexistent_configs.json"

    assert not test_configs_file.exists()

    write_to_configs(valid_json_data, configs=test_configs_file)

    assert test_configs_file.exists()

    result: dict[str, str] = json.loads(test_configs_file.read_text(encoding="utf-8"))
    assert result == valid_json_data

    assert caplog.record_tuples == [
        (
            "auto_file_sorter.configs_handling",
            70,
            f"Added new extension configuration {valid_json_data} to '{test_configs_file}'",
        ),
    ]


def test_write_to_configs_file_not_found_error(
    valid_json_data: str,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file: Path = tmp_path / "nonexistent_dir/nonexistent_configs.json"

    with pytest.raises(SystemExit):
        write_to_configs(
            valid_json_data,  # type: ignore[arg-type]
            configs=test_configs_file,
        )

    assert caplog.record_tuples == [
        (
            "auto_file_sorter.configs_handling",
            50,
            f"Unable to find '{test_configs_file}'",
        ),
    ]
