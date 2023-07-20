"""Module testing ``auto-file-sorter.configs_handling.py``."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from auto_file_sorter.configs_handling import read_from_configs, write_to_configs

if TYPE_CHECKING:
    from pathlib import Path

# pylint: disable=C0116, W0621


@pytest.fixture()  # type: ignore[misc]
def valid_json_data() -> dict[str, str]:
    return {
        ".txt": "test/path/for/txt",
        ".jpeg": "test/path/for/jpeg",
    }


@pytest.fixture()  # type: ignore[misc]
def invalid_json_data() -> str:
    return "invalid_json_data"


def test_read_from_configs(
    valid_json_data: dict[str, str],
    tmp_path: Path,
) -> None:
    test_configs: Path = tmp_path / "test_configs.json"
    test_configs.write_text(json.dumps(valid_json_data), encoding="utf-8")
    result: dict[str, str] = read_from_configs(configs=test_configs)
    assert result == valid_json_data


def test_read_from_configs_no_file(
    tmp_path: Path,
) -> None:
    test_configs: Path = tmp_path / "nonexistent_configs.json"

    assert not test_configs.exists()

    with pytest.raises(SystemExit):
        read_from_configs(configs=test_configs)

    assert test_configs.exists()

    with test_configs.open(mode="r", encoding="utf-8") as json_file:
        configs: dict[str, str] = json.load(json_file)
    assert configs == {}


def test_read_from_configs_permission_error(tmp_path: Path) -> None:
    restricted_configs: Path = tmp_path / "restricted_configs.json"
    restricted_configs.touch()
    restricted_configs.chmod(0000)

    with pytest.raises(SystemExit):
        read_from_configs(configs=restricted_configs)


def test_read_from_configs_invalid_json(invalid_json_data: str, tmp_path: Path) -> None:
    test_configs: Path = tmp_path / "invalid_configs.json"
    test_configs.write_text(invalid_json_data)

    with pytest.raises(SystemExit):
        read_from_configs(configs=test_configs)


def test_write_to_configs(valid_json_data: dict[str, str], tmp_path: Path) -> None:
    test_configs: Path = tmp_path / "test_configs.json"

    write_to_configs(valid_json_data, configs=test_configs)

    with test_configs.open(mode="r", encoding="utf-8") as json_file:
        result: dict[str, str] = json.load(json_file)
    assert result == valid_json_data


def test_write_to_configs_nonexistent_configs(
    valid_json_data: dict[str, str],
    tmp_path: Path,
) -> None:
    test_configs: Path = tmp_path / "nonexistent_configs.json"

    assert not test_configs.exists()

    write_to_configs(valid_json_data, configs=test_configs)

    assert test_configs.exists()

    with test_configs.open(mode="r", encoding="utf-8") as json_file:
        result: dict[str, str] = json.load(json_file)
    assert result == valid_json_data


def test_write_to_configs_permission_error(
    valid_json_data: dict[str, str],
    tmp_path: Path,
) -> None:
    restricted_configs: Path = tmp_path / "restricted_configs.json"
    restricted_configs.touch()
    restricted_configs.chmod(0000)

    with pytest.raises(SystemExit):
        write_to_configs(valid_json_data, configs=restricted_configs)


def test_write_to_configs_file_not_found_error(
    valid_json_data: str,
    tmp_path: Path,
) -> None:
    with pytest.raises(SystemExit):
        write_to_configs(
            valid_json_data,  # type: ignore[arg-type]
            configs=tmp_path / "nonexistent_dir/nonexistent_configs.json",
        )
