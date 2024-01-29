"""Custom ``pytest`` fixtures."""

from __future__ import annotations

__all__: list[str] = [
    "info_caplog",
    "valid_json_data",
    "invalid_json_data",
    "test_configs",
    "empty_test_configs",
    "invalid_test_configs",
    "extension_paths",
    "path_for_undefined_extensions",
    "test_log_as_str",
    "test_log",
]

import json
import logging
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture()
def info_caplog(caplog: pytest.LogCaptureFixture) -> pytest.LogCaptureFixture:
    """Return a ``pytest.caplog`` fixture with the logging level set to ``INFO`` / 10."""
    caplog.set_level(logging.INFO)
    return caplog


@pytest.fixture()
def test_configs(
    tmp_path: Path,
    valid_json_data: dict[str, str],
) -> tuple[Path, dict[str, str]]:
    """Return a temporary configs ``JSON`` file together with its content."""
    test_configs_file: Path = tmp_path / "test_configs.json"

    test_configs_file.write_text(json.dumps(valid_json_data), encoding="utf-8")

    return test_configs_file, valid_json_data


@pytest.fixture()
def test_configs_as_str(test_configs: tuple[Path, dict[str, str]]) -> str:
    """Return a temporary configs ``JSON`` file as a string."""
    return str(test_configs[0])


@pytest.fixture()
def empty_test_configs(tmp_path: Path) -> Path:
    """Return an empty temporary configs ``JSON`` file."""
    test_configs_file: Path = tmp_path / "test_configs.json"

    test_configs_file.write_text(json.dumps({}), encoding="utf-8")

    return test_configs_file


@pytest.fixture()
def invalid_test_configs(
    tmp_path: Path,
    invalid_json_data: str,
) -> tuple[Path, str]:
    """Return an temporary configs ``json`` file together with its invalid ``JSON`` content."""
    test_configs_file: Path = tmp_path / "test_configs.json"

    test_configs_file.write_text(invalid_json_data, encoding="utf-8")

    return test_configs_file, invalid_json_data


@pytest.fixture()
def test_log(tmp_path: Path) -> Path:
    """Return a temporary log file."""
    return tmp_path / "test.log"


@pytest.fixture()
def valid_json_data() -> dict[str, str]:
    """Return valid ``JSON`` data."""
    return {
        ".txt": "/path/to/txt",
        ".pdf": "/path/to/pdf",
    }


@pytest.fixture()
def invalid_json_data() -> str:
    """Return invalid ``JSON``."""
    return "invalid json data"


@pytest.fixture()
def extension_paths(tmp_path: Path) -> dict[str, Path]:
    """Return a a ``dict`` that binds file extensions to a temporary path."""
    return {
        ".txt": tmp_path / "txt",
        ".pdf": tmp_path / "pdf",
    }


@pytest.fixture()
def path_for_undefined_extensions(tmp_path: Path) -> Path:
    """Return a temporary path which will be the path for undefined extensions."""
    return tmp_path / "undefined"


@pytest.fixture()
def test_log_as_str(tmp_path: Path) -> str:
    """Return a temporary log file as a string."""
    return str(tmp_path / "auto-file-sorter.log")
