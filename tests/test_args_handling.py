"""Module testing ``auto_file_sorter.args_handling.py``."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

import pytest

# pylint: disable=C0116, W0611
from auto_file_sorter.args_handling import handle_locations_args

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.skip(reason="Test needs to be written")
def test_handle_write_args() -> None:
    ...


@pytest.mark.skip(reason="Test needs to be written")
def test_handle_read_args() -> None:
    ...


@pytest.mark.skip(reason="Test needs to be written")
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
