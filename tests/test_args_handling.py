"""Module testing ``auto_file_sorter.args_handling.py``."""
from __future__ import annotations

import argparse
import platform
from pathlib import Path

import pytest

# pylint: disable=C0116, W0611
from auto_file_sorter.args_handling import (
    _FILE_EXTENSION_PATTERN,
    _add_to_startup,
    handle_locations_args,
    resolved_path_from_str,
)


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
def test_file_valid_extension_pattern(extension: str) -> None:
    assert _FILE_EXTENSION_PATTERN.fullmatch(extension) is not None


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
def test_file_invalid_extension_pattern(extension: str) -> None:
    assert _FILE_EXTENSION_PATTERN.fullmatch(extension) is None


@pytest.mark.parametrize(
    ("path_as_str", "expected_path"),
    (
        pytest.param(
            "/path/to/some/file.txt",
            Path("C:/path/to/some/file.txt"),
            id="regular-str",
        ),
        pytest.param(
            "  /path/to/some/file.txt  ",
            Path("C:/path/to/some/file.txt"),
            id="trailing-whitespaces-str",
        ),
    ),
)
def test_resolved_path_from_str(path_as_str: str, expected_path: Path) -> None:
    assert resolved_path_from_str(path_as_str) == expected_path


@pytest.mark.skip(reason="Test not written yet")
@pytest.mark.skipif(
    platform.system() != "Windows",
    reason="Test behavior on windows-systems",
)
def test_add_to_startup_windows() -> None:
    ...


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Test behavior on non-windows systems",
)
@pytest.mark.parametrize(
    ("argv"),
    (
        pytest.param(["track", "--autostart", "path/to/some/dir"], id="--autostart"),
        pytest.param(["track", "-A", "path/to/some/dir"], id="-A"),
    ),
)
def test_add_to_startup_non_windows(
    argv: list[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    _add_to_startup(argv)
    assert (
        "Adding 'auto-file-sorter' to startup is only supported on Windows."
        in caplog.text
    )


@pytest.mark.skip(reason="Test not written yet")
def test_handle_write_args() -> None:
    ...


@pytest.mark.skip(reason="Test not written yet")
def test_handle_read_args() -> None:
    ...


@pytest.mark.skip(reason="Test not written yet")
def test_handle_track_args() -> None:
    ...


def test_handle_locations_args_get_log_location(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    test_log_file: Path = tmp_path / "auto-file-sorter.log"

    args = argparse.Namespace(
        log_location=test_log_file,
        get_log_location=True,
        get_config_location=False,
    )

    exit_code: int = handle_locations_args(args)

    out, _ = capsys.readouterr()

    assert out == f"{test_log_file}\n"

    assert exit_code == 0


def test_handle_locations_args_get_configs_location(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    test_configs_file: Path = tmp_path / "configs.json"

    args = argparse.Namespace(
        configs_location=test_configs_file,
        get_log_location=False,
        get_config_location=True,
    )

    exit_code: int = handle_locations_args(args)

    out, _ = capsys.readouterr()

    assert out == f"{test_configs_file}\n"

    assert exit_code == 0


def test_handle_locations_args_both(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    test_log_file: Path = tmp_path / "auto-file-sorter.log"
    test_configs_file: Path = tmp_path / "configs.json"

    args = argparse.Namespace(
        log_location=test_log_file,
        configs_location=test_configs_file,
        get_log_location=True,
        get_config_location=True,
    )

    exit_code: int = handle_locations_args(args)

    out, _ = capsys.readouterr()

    assert out == f"{test_log_file}\n{test_configs_file}\n"

    assert exit_code == 0
