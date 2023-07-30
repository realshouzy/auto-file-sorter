"""Module testing ``auto_file_sorter.args_handling.py``."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import pytest

from auto_file_sorter.args_handling import (
    _add_to_startup,
    handle_locations_args,
    handle_read_args,
    handle_track_args,
    handle_write_args,
    resolved_path_from_str,
)

# pylint: disable=C0116, W0621


@pytest.fixture()
def test_config(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    test_configs_file: Path = tmp_path / "test_configs.json"

    test_configs: dict[str, str] = {
        ".txt": "/path/to/txt",
        ".pdf": "/path/to/pdf",
    }

    with test_configs_file.open(mode="w") as json_file:
        json.dump(test_configs, json_file, indent=4)

    return test_configs_file, test_configs


@pytest.mark.parametrize(
    ("path_as_str", "expected_path"),
    (
        pytest.param(
            "/path/to/some/file.txt",
            Path("C:/path/to/some/file.txt"),
            id="regular_str",
        ),
        pytest.param(
            "  /path/to/some/file.txt  ",
            Path("C:/path/to/some/file.txt"),
            id="trailing_whitespaces_str",
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


def test_handle_write_args_new_config(test_config: tuple[Path, dict[str, str]]) -> None:
    test_configs_file, _ = test_config

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=[".jpg", "/path/to/jpg"],
        json_file=None,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 0

    with test_configs_file.open() as json_file:
        updated_configs: dict[str, str] = json.load(json_file)

    assert updated_configs[".jpg"] == "/path/to/jpg"


@pytest.mark.parametrize(
    "new_config",
    (
        pytest.param(["", "/path/to/jpg"], id="no_extension"),
        pytest.param([".jpg", ""], id="no_path"),
    ),
)
def test_handle_write_args_new_config_no_extension_or_path(
    new_config: list[str],
    test_config: tuple[Path, dict[str, str]],
) -> None:
    test_configs_file, _ = test_config

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=new_config,
        json_file=None,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 1


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
def test_handle_write_args_new_config_invalid_extension(
    extension: str,
    test_config: tuple[Path, dict[str, str]],
) -> None:
    test_configs_file, _ = test_config

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=[extension, "/path/to/some/dir"],
        json_file=None,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 1


def test_handle_write_args_load_json_file(
    tmp_path: Path,
    test_config: tuple[Path, dict[str, str]],
) -> None:
    test_configs_file, _ = test_config

    json_file_path = tmp_path / "test_load_configs.json"
    json_data: dict[str, str] = {
        ".docx": "/path/to/docx",
        ".png": "/path/to/png",
    }
    with json_file_path.open("w") as json_file:
        json.dump(json_data, json_file)

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=None,
        json_file=json_file_path,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 0

    with test_configs_file.open() as json_file:
        updated_configs: dict[str, str] = json.load(json_file)

    assert updated_configs[".docx"] == "/path/to/docx"
    assert updated_configs[".png"] == "/path/to/png"


def test_handle_write_args_load_json_file_no_json(
    tmp_path: Path,
    test_config: tuple[Path, dict[str, str]],
) -> None:
    test_configs_file, _ = test_config

    json_file_path = tmp_path / "test_load_configs.txt"

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=None,
        json_file=json_file_path,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 1


def test_handle_write_args_load_json_file_file_not_found_error(
    tmp_path: Path,
    test_config: tuple[Path, dict[str, str]],
) -> None:
    test_configs_file, _ = test_config

    json_file_path = tmp_path / "test_load_configs.json"

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=None,
        json_file=json_file_path,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 1


def test_handle_write_args_load_json_file_json_decode_error(
    tmp_path: Path,
    test_config: tuple[Path, dict[str, str]],
) -> None:
    test_configs_file, _ = test_config

    json_file_path = tmp_path / "test_load_configs.json"
    json_file_path.write_text("invalid json data")

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=None,
        json_file=json_file_path,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 1


def test_handle_write_args_remove_configs(
    test_config: tuple[Path, dict[str, str]],
) -> None:
    test_configs_file, _ = test_config

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=None,
        json_file=None,
        configs_to_be_removed=[".txt", ".pdf", ".png"],
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 0

    with test_configs_file.open() as json_file:
        updated_configs: dict[str, str] = json.load(json_file)

    assert ".txt" not in updated_configs
    assert ".pdf" not in updated_configs
    assert ".png" not in updated_configs


@pytest.mark.parametrize(
    ("get_configs", "expected_out"),
    (
        pytest.param(
            None,
            ".txt: C:\\path\\to\\txt\n.pdf: C:\\path\\to\\pdf\n",
            id="all_configs",
        ),
        pytest.param(
            [".pdf"],
            ".pdf: C:\\path\\to\\pdf\n",
            id="selected_configs",
        ),
        pytest.param(
            [".png"],
            "",
            id="selected_configs_not_in_config",
        ),
    ),
)
def test_handle_read_args(
    get_configs: list[str] | None,
    expected_out: str,
    test_config: tuple[Path, dict[str, str]],
    capsys: pytest.CaptureFixture[str],
) -> None:
    test_configs_file, _ = test_config

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        get_configs=get_configs,
    )
    exit_code: int = handle_read_args(args)
    assert exit_code == 0

    out, _ = capsys.readouterr()
    assert out == expected_out


# TODO: Make this actually testable
@pytest.mark.skip(reason="Test not finished yet")
def test_handle_track_args_no_auto_start(
    test_config: tuple[Path, dict[str, str]],
    tmp_path: Path,
) -> None:
    test_configs_file, _ = test_config

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        tracked_paths=[tmp_path],
        path_for_undefined_extensions=None,
        enable_autostart=False,
    )
    exit_code: int = handle_track_args(args)
    assert exit_code == 0


def test_handle_locations_args_get_log_location(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    test_log_file: Path = tmp_path / "auto-file-sorter.log"

    args: argparse.Namespace = argparse.Namespace(
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

    args: argparse.Namespace = argparse.Namespace(
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

    args: argparse.Namespace = argparse.Namespace(
        log_location=test_log_file,
        configs_location=test_configs_file,
        get_log_location=True,
        get_config_location=True,
    )

    exit_code: int = handle_locations_args(args)

    out, _ = capsys.readouterr()

    assert out == f"{test_log_file}\n{test_configs_file}\n"

    assert exit_code == 0
