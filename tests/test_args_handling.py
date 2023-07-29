"""Module testing ``auto_file_sorter.args_handling.py``."""
from __future__ import annotations

import argparse
import platform
from pathlib import Path

import pytest

# pylint: disable=C0116, W0611
from auto_file_sorter.args_handling import (
    _add_to_startup,
    handle_locations_args,
    resolved_path_from_str,
)


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


@pytest.mark.skipif(
    platform.system() != "Windows",
    reason="Test behavior on windows-systems",
)
@pytest.mark.parametrize(
    ("argv", "clean_argv"),
    (
        pytest.param(
            ["track", "--autostart", "path/to/some/dir"],
            "track path/to/some/dir",
            id="normal_autostart",
        ),
        pytest.param(
            ["--verbose", "track", "--autostart", "path/to/some/dir"],
            "track path/to/some/dir",
            id="one_verbose_flag",
        ),
        pytest.param(
            ["--verbose", "--verbose", "track", "--autostart", "path/to/some/dir"],
            "track path/to/some/dir",
            id="more_verbose_flag",
        ),
        pytest.param(
            ["--debug", "--verbose", "track", "--autostart", "path/to/some/dir"],
            "--debug track path/to/some/dir",
            id="debug_verbose_flag",
        ),
        pytest.param(
            ["-v", "track", "--autostart", "path/to/some/dir"],
            "track path/to/some/dir",
            id="v_flag",
        ),
        pytest.param(
            ["-vv", "track", "--autostart", "path/to/some/dir"],
            "track path/to/some/dir",
            id="vv_flag",
        ),
        pytest.param(
            ["-vvvv", "track", "--autostart", "path/to/some/dir"],
            "track path/to/some/dir",
            id="vvvv_flag",
        ),
        pytest.param(
            ["-d", "-vvv", "track", "--autostart", "path/to/some/dir"],
            "-d track path/to/some/dir",
            id="debug_vvv_flag",
        ),
        pytest.param(
            [
                "-vvv",
                "track",
                "--autostart",
                "path/to/some/dir",
                "path/to/some/other/dir",
            ],
            "track path/to/some/dir path/to/some/other/dir",
            id="vvv_flag_two_tracked_paths",
        ),
    ),
)
def test_add_to_startup_windows(
    argv: list[str],
    clean_argv: str,
    tmp_path: Path,
) -> None:
    path_to_vbs: Path = tmp_path / "auto-file-sorter.vbs"
    vbs_file_contents: str = (
        'Set objShell = WScript.CreateObject("WScript.Shell")\n'
        f'objShell.Run "{clean_argv}", 0, True\n'
    )

    _add_to_startup(argv=argv, startup_folder=tmp_path)

    assert tmp_path.exists()
    assert path_to_vbs.exists()
    assert path_to_vbs.read_text() == vbs_file_contents


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Test behavior on non-windows systems",
)
@pytest.mark.parametrize(
    ("argv"),
    (
        pytest.param(
            ["track", "--autostart", "path/to/some/dir"],
            id="normal_autostart",
        ),
        pytest.param(
            ["--verbose", "track", "--autostart", "path/to/some/dir"],
            id="one_verbose_flag",
        ),
        pytest.param(
            ["--verbose", "--verbose", "track", "--autostart", "path/to/some/dir"],
            id="more_verbose_flag",
        ),
        pytest.param(
            ["--debug", "--verbose", "track", "--autostart", "path/to/some/dir"],
            id="debug_verbose_flag",
        ),
        pytest.param(
            ["-v", "track", "--autostart", "path/to/some/dir"],
            id="v_flag",
        ),
        pytest.param(
            ["-vv", "track", "--autostart", "path/to/some/dir"],
            id="vv_flag",
        ),
        pytest.param(
            ["-vvvv", "track", "--autostart", "path/to/some/dir"],
            id="vvvv_flag",
        ),
        pytest.param(
            ["-d", "-vvv", "track", "--autostart", "path/to/some/dir"],
            id="debug_vvv_flag",
        ),
        pytest.param(
            [
                "-vvv",
                "track",
                "--autostart",
                "path/to/some/dir",
                "path/to/some/other/dir",
            ],
            id="vvv_flag_two_tracked_paths",
        ),
    ),
)
def test_add_to_startup_non_windows(
    argv: list[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    _add_to_startup(argv=argv)
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
