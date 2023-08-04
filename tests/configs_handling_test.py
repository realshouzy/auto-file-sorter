"""Module testing ``auto-file-sorter.configs_handling.py``."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

# pylint: disable=C0116, W0611, W0621
from auto_file_sorter.configs_handling import read_from_configs, write_to_configs
from tests.fixtures import (
    empty_test_configs,
    info_caplog,
    invalid_json_data,
    restricted_test_configs,
    test_configs,
    valid_json_data,
)

if TYPE_CHECKING:
    from pathlib import Path

# pylint: disable=C0116, W0621


def test_read_from_configs(test_configs: tuple[Path, dict[str, str]]) -> None:
    test_configs_file, test_configs_data = test_configs
    result: dict[str, str] = read_from_configs(configs=test_configs_file)
    assert result == test_configs_data


def test_read_from_configs_no_file(tmp_path: Path) -> None:
    test_configs_file: Path = tmp_path / "nonexistent_configs.json"

    assert not test_configs_file.exists()

    with pytest.raises(SystemExit):
        read_from_configs(configs=test_configs_file)

    assert test_configs_file.exists()

    configs: dict[str, str] = json.loads(test_configs_file.read_text(encoding="utf-8"))
    assert configs == {}


def test_read_from_configs_permission_error1(restricted_test_configs: Path) -> None:
    with pytest.raises(SystemExit):
        read_from_configs(configs=restricted_test_configs)


def test_read_from_configs_invalid_json(
    empty_test_configs: Path,
    invalid_json_data: str,
) -> None:
    empty_test_configs.write_text(invalid_json_data)

    with pytest.raises(SystemExit):
        read_from_configs(configs=empty_test_configs)


def test_write_to_configs(
    empty_test_configs: Path,
    valid_json_data: dict[str, str],
) -> None:
    write_to_configs(valid_json_data, configs=empty_test_configs)

    result = json.loads(empty_test_configs.read_text(encoding="utf-8"))
    assert result == valid_json_data


def test_write_to_configs_nonexistent_configs(
    valid_json_data: dict[str, str],
    tmp_path: Path,
) -> None:
    test_configs: Path = tmp_path / "nonexistent_configs.json"

    assert not test_configs.exists()

    write_to_configs(valid_json_data, configs=test_configs)

    assert test_configs.exists()

    result: dict[str, str] = json.loads(test_configs.read_text(encoding="utf-8"))
    assert result == valid_json_data


def test_write_to_configs_permission_error(
    restricted_test_configs: Path,
    valid_json_data: dict[str, str],
) -> None:
    with pytest.raises(SystemExit):
        write_to_configs(valid_json_data, configs=restricted_test_configs)


def test_write_to_configs_file_not_found_error(
    valid_json_data: str,
    tmp_path: Path,
) -> None:
    with pytest.raises(SystemExit):
        write_to_configs(
            valid_json_data,  # type: ignore[arg-type]
            configs=tmp_path / "nonexistent_dir/nonexistent_configs.json",
        )
