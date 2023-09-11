"""Tests for ``auto_file_sorter.args_handling``."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

# pylint: disable=C0116, W0611
from auto_file_sorter.args_handling import (
    _add_to_startup,
    _create_observers,
    _get_extension_paths_from_configs,
    handle_locations_args,
    handle_read_args,
    handle_track_args,
    handle_write_args,
    resolved_path_from_str,
)

#  valid_json_data is indirectly used by test_configs, do not remove!
from tests.fixtures import (
    info_caplog,
    path_for_undefined_extensions,
    test_configs,
    valid_json_data,
)

if TYPE_CHECKING:
    from watchdog.observers.api import BaseObserver


@pytest.mark.skipif(
    platform.system() != "Windows",
    reason="Test behavior on Windows-systems",
)
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
def test_resolved_path_from_str_windows(
    path_as_str: str,
    expected_path: Path,
) -> None:  # pragma: win32 cover
    assert resolved_path_from_str(path_as_str) == expected_path


@pytest.mark.skipif(
    platform.system() != "Linux" and platform.system() != "Darwin",
    reason="Test behavior on Posix systems",
)
@pytest.mark.parametrize(
    ("path_as_str", "expected_path"),
    (
        pytest.param(
            "/path/to/some/file.txt",
            Path("/path/to/some/file.txt"),
            id="regular_str",
        ),
        pytest.param(
            "  /path/to/some/file.txt  ",
            Path("/path/to/some/file.txt"),
            id="trailing_whitespaces_str",
        ),
    ),
)
def test_resolved_path_from_str_posix(
    path_as_str: str,
    expected_path: Path,
) -> None:  # pragma: posix cover
    assert resolved_path_from_str(path_as_str) == expected_path


@pytest.mark.skipif(
    platform.system() != "Windows",
    reason="Test behavior on Windows-systems",
)
@pytest.mark.parametrize(
    ("argv", "cmd"),
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
    cmd: str,
    tmp_path: Path,
    info_caplog: pytest.LogCaptureFixture,
) -> None:  # pragma: win32 cover
    path_to_vbs: Path = tmp_path / "auto-file-sorter.vbs"
    vbs_file_contents: str = (
        'Set objShell = WScript.CreateObject("WScript.Shell")\n'
        f'objShell.Run "{cmd}", 0, True\n'
    )

    _add_to_startup(argv=argv, startup_folder=tmp_path)

    assert path_to_vbs.exists()
    assert path_to_vbs.read_text(encoding="utf-8") == vbs_file_contents

    assert info_caplog.record_tuples == [
        (
            "auto_file_sorter.args_handling",
            20,
            f"Added '{path_to_vbs}' with '{cmd}' to startup",
        ),
    ]


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Test behavior on Non-Windows systems",
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
) -> None:  # pragma: win32 no cover
    _add_to_startup(argv=argv)
    assert caplog.record_tuples == [
        (
            "auto_file_sorter.args_handling",
            30,
            "Adding 'auto-file-sorter' to startup is only supported on Windows.",
        ),
    ]


def test_handle_write_args_new_config(
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=[".jpg", "/path/to/jpg"],
        json_file=None,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 0

    updated_configs: dict[str, str] = json.loads(
        test_configs_file.read_text(encoding="utf-8"),
    )

    assert updated_configs[".jpg"] == "/path/to/jpg"

    assert (
        "auto_file_sorter.args_handling",
        70,
        f"Updated '.jpg': '/path/to/jpg' from '{test_configs_file}'",
    ) in caplog.record_tuples


@pytest.mark.parametrize(
    "new_config",
    (
        pytest.param(["", "/path/to/jpg"], id="no_extension"),
        pytest.param([".jpg", ""], id="no_path"),
    ),
)
def test_handle_write_args_new_config_no_extension_or_path(
    new_config: list[str],
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=new_config,
        json_file=None,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 1

    assert (
        "auto_file_sorter.args_handling",
        50,
        f"Either an empty extension '{new_config[0].lower().replace(' ', '')}' "
        f"or an empty path '{new_config[1].strip()}' was specified to add, which is invalid",
    ) in caplog.record_tuples


@pytest.mark.parametrize(
    "extension",
    (
        pytest.param(" TXT"),
        pytest.param("zip "),
        pytest.param("_7z_"),
        pytest.param("-123"),
        pytest.param(".PnG!"),
        pytest.param(".Jp2@"),
        pytest.param("/doc"),
    ),
)
def test_handle_write_args_new_config_invalid_extension(
    extension: str,
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=[extension, "/path/to/some/dir"],
        json_file=None,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 1

    assert (
        "auto_file_sorter.args_handling",
        50,
        f"Given extension '{extension.lower().replace(' ', '')}' is invalid",
    ) in caplog.record_tuples


def test_handle_write_args_load_json_file(
    tmp_path: Path,
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    json_file_path = tmp_path / "test_load_configs.json"
    json_data: dict[str, str] = {
        ".docx": "/path/to/docx",
        ".png": "/path/to/png",
    }

    json_file_path.write_text(json.dumps(json_data), encoding="utf-8")

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=None,
        json_file=json_file_path,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 0

    updated_configs: dict[str, str] = json.loads(
        test_configs_file.read_text(encoding="utf-8"),
    )

    assert updated_configs[".docx"] == "/path/to/docx"
    assert updated_configs[".png"] == "/path/to/png"

    assert (
        "auto_file_sorter.args_handling",
        70,
        f"Loaded '{json_file_path}' into configs",
    ) in caplog.record_tuples


def test_handle_write_args_load_json_file_no_json(
    tmp_path: Path,
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    json_file_path = tmp_path / "test_load_configs.txt"

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=None,
        json_file=json_file_path,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 1

    assert (
        "auto_file_sorter.args_handling",
        50,
        "Configs can only be read from json files",
    ) in caplog.record_tuples


def test_handle_write_args_load_json_file_file_not_found_error(
    tmp_path: Path,
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    json_file_path = tmp_path / "test_load_configs.json"

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=None,
        json_file=json_file_path,
        configs_to_be_removed=None,
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 1

    assert (
        "auto_file_sorter.args_handling",
        50,
        f"Unable to find '{json_file_path}'",
    ) in caplog.record_tuples


def test_handle_write_args_load_json_file_decode_error(
    tmp_path: Path,
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

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

    assert (
        "auto_file_sorter.args_handling",
        50,
        f"Given JSON file is not correctly formatted: '{json_file_path}'",
    ) in caplog.record_tuples


def test_handle_write_args_remove_configs(
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=None,
        json_file=None,
        configs_to_be_removed=[".txt", ".pdf"],
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 0

    updated_configs: dict[str, str] = json.loads(
        test_configs_file.read_text(encoding="utf-8"),
    )

    assert ".txt" not in updated_configs
    assert ".pdf" not in updated_configs

    assert (
        "auto_file_sorter.args_handling",
        70,
        "Removed '.txt'",
    ) in caplog.record_tuples
    assert (
        "auto_file_sorter.args_handling",
        70,
        "Removed '.pdf'",
    ) in caplog.record_tuples


def test_handle_write_args_remove_configs_invalid_extenion(
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=None,
        json_file=None,
        configs_to_be_removed=[".txt", "_ABC_"],
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 0

    updated_configs: dict[str, str] = json.loads(
        test_configs_file.read_text(encoding="utf-8"),
    )

    assert ".pdf" in updated_configs
    assert ".txt" not in updated_configs

    assert (
        "auto_file_sorter.args_handling",
        70,
        "Removed '.txt'",
    ) in caplog.record_tuples
    assert (
        "auto_file_sorter.args_handling",
        30,
        "Skipping invalid extension: '_abc_'",
    ) in caplog.record_tuples


def test_handle_write_args_remove_configs_with_extension_not_in_configs(
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        new_config=None,
        json_file=None,
        configs_to_be_removed=[".txt", ".png"],
    )
    exit_code: int = handle_write_args(args)
    assert exit_code == 0

    updated_configs: dict[str, str] = json.loads(
        test_configs_file.read_text(encoding="utf-8"),
    )

    assert ".pdf" in updated_configs
    assert ".txt" not in updated_configs

    assert (
        "auto_file_sorter.args_handling",
        70,
        "Removed '.txt'",
    ) in caplog.record_tuples
    assert (
        "auto_file_sorter.args_handling",
        30,
        "Ignoring '.png', because it is not in the configs",
    ) in caplog.record_tuples


@pytest.mark.skipif(
    platform.system() != "Windows",
    reason="Test behavior on Windows-systems",
)
def test_handle_read_args_all_configs_windows(
    test_configs: tuple[Path, dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:  # pragma: win32 cover
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        get_configs=None,
    )
    exit_code: int = handle_read_args(args)
    assert exit_code == 0

    assert (
        capsys.readouterr().out == ".txt: C:\\path\\to\\txt\n.pdf: C:\\path\\to\\pdf\n"
    )

    assert (
        "auto_file_sorter.args_handling",
        70,
        "Printed all the configs",
    ) in caplog.record_tuples


@pytest.mark.skipif(
    platform.system() != "Linux" and platform.system() != "Darwin",
    reason="Test behavior on Posix systems",
)
def test_handle_read_args_all_configs_posix(
    test_configs: tuple[Path, dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:  # pragma: posix cover
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        get_configs=None,
    )

    with pytest.raises(SystemExit):
        handle_read_args(args)

    assert capsys.readouterr().out == ".txt: /path/to/txt\n.pdf: /path/to/pdf\n"

    assert (
        "auto_file_sorter.args_handling",
        70,
        "Printed all the configs",
    ) in caplog.record_tuples


@pytest.mark.skipif(
    platform.system() != "Windows",
    reason="Test behavior on Windows-systems",
)
def test_handle_read_args_selected_configs_windows(
    test_configs: tuple[Path, dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:  # pragma: win32 cover
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        get_configs=[".pdf"],
    )
    exit_code: int = handle_read_args(args)
    assert exit_code == 0

    assert capsys.readouterr().out == ".pdf: C:\\path\\to\\pdf\n"

    assert (
        "auto_file_sorter.args_handling",
        70,
        "Printed the selected configs",
    ) in caplog.record_tuples


@pytest.mark.skipif(
    platform.system() != "Linux" and platform.system() != "Darwin",
    reason="Test behavior on Posix systems",
)
def test_handle_read_args_selected_configs_posix(
    test_configs: tuple[Path, dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:  # pragma: posix cover
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        get_configs=[".pdf"],
    )
    exit_code: int = handle_read_args(args)
    assert exit_code == 0

    assert capsys.readouterr().out == ".pdf: /path/to/pdf\n"

    assert (
        "auto_file_sorter.args_handling",
        70,
        "Printed the selected configs",
    ) in caplog.record_tuples


def test_handle_read_args_selected_configs_invalid_extensions(
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        get_configs=["abc"],
    )

    with pytest.raises(SystemExit):
        handle_read_args(args)

    assert (
        "auto_file_sorter.args_handling",
        30,
        "Ignoring invalid extension 'abc'",
    ) in caplog.record_tuples
    assert (
        "auto_file_sorter.args_handling",
        50,
        "No valid extensions selected",
    ) in caplog.record_tuples


def test_handle_read_args_selected_extension_not_in_configs(
    test_configs: tuple[Path, dict[str, str]],
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        get_configs=[".odt"],
    )

    with pytest.raises(SystemExit):
        handle_read_args(args)

    assert (
        "auto_file_sorter.args_handling",
        30,
        "Ignoring '.odt', because it is not in the configs",
    ) in caplog.record_tuples
    assert (
        "auto_file_sorter.args_handling",
        50,
        "No valid extensions selected",
    ) in caplog.record_tuples


def test_get_extension_paths_from_configs(
    test_configs: tuple[Path, dict[str, str]],
    info_caplog: pytest.LogCaptureFixture,
) -> None:
    _, test_configs_data = test_configs
    expected_extension_paths: dict[str, Path] = {
        extension: resolved_path_from_str(path_as_str)
        for extension, path_as_str in test_configs_data.items()
    }
    assert (
        _get_extension_paths_from_configs(test_configs_data) == expected_extension_paths
    )
    assert info_caplog.record_tuples == [
        (
            "auto_file_sorter.args_handling",
            20,
            "Got extension paths",
        ),
    ]


def test_create_observers(
    test_configs: tuple[Path, dict[str, str]],
    path_for_undefined_extensions: Path,
    tmp_path: Path,
) -> None:
    _, test_configs_data = test_configs
    extension_paths: dict[str, Path] = {
        extension: resolved_path_from_str(path_as_str)
        for extension, path_as_str in test_configs_data.items()
    }

    observers: list[BaseObserver] = _create_observers(
        [tmp_path],
        extension_paths,
        path_for_undefined_extensions,
    )

    assert len(observers) == 1
    assert observers[0].name == str(tmp_path)
    assert observers[0].daemon
    assert not observers[0].is_alive()


def test_create_observers_paths_dont_exists_exit(
    test_configs: tuple[Path, dict[str, str]],
    path_for_undefined_extensions: Path,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    _, test_configs_data = test_configs
    extension_paths: dict[str, Path] = {
        extension: resolved_path_from_str(path_as_str)
        for extension, path_as_str in test_configs_data.items()
    }

    observers: list[BaseObserver] = _create_observers(
        [tmp_path / "test"],
        extension_paths,
        path_for_undefined_extensions,
    )

    assert not observers
    assert (
        "auto_file_sorter.args_handling",
        30,
        f"Skipping '{tmp_path / 'test'}', because it does not exist",
    ) in caplog.record_tuples


def test_create_observers_path_is_file_exit(
    test_configs: tuple[Path, dict[str, str]],
    path_for_undefined_extensions: Path,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    invalid_tracked_path: Path = tmp_path / "test.txt"
    invalid_tracked_path.touch()
    _, test_configs_data = test_configs
    extension_paths: dict[str, Path] = {
        extension: resolved_path_from_str(path_as_str)
        for extension, path_as_str in test_configs_data.items()
    }

    observers: list[BaseObserver] = _create_observers(
        [invalid_tracked_path],
        extension_paths,
        path_for_undefined_extensions,
    )

    assert not observers
    assert (
        "auto_file_sorter.args_handling",
        30,
        f"Skipping '{invalid_tracked_path}', expected a directory, not a file",
    ) in caplog.record_tuples


def test_handle_track_args_all_paths_not_found(
    test_configs: tuple[Path, dict[str, str]],
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        tracked_paths=[tmp_path / "test"],
        path_for_undefined_extensions=None,
        enable_autostart=False,
    )
    exit_code: int = handle_track_args(args)
    assert exit_code == 1

    assert (
        "auto_file_sorter.args_handling",
        50,
        f"All given paths are invalid: {tmp_path / 'test'}",
    ) in caplog.record_tuples


def test_handle_track_args_no_configs(
    test_configs: tuple[Path, dict[str, str]],
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    test_configs_file, _ = test_configs
    test_configs_file.write_text(json.dumps({}))

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        tracked_paths=[tmp_path],
        path_for_undefined_extensions=None,
        enable_autostart=False,
    )
    exit_code: int = handle_track_args(args)
    assert exit_code == 1

    assert (
        "auto_file_sorter.args_handling",
        50,
        f"No paths for extensions defined in '{test_configs_file}'",
    ) in caplog.record_tuples


def test_handle_locations_args_get_log_location(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    test_log_file: Path = tmp_path / "auto-file-sorter.log"

    args: argparse.Namespace = argparse.Namespace(
        log_location=test_log_file,
        get_log_location=True,
        get_configs_location=False,
    )

    exit_code: int = handle_locations_args(args)

    assert capsys.readouterr().out == f"{test_log_file}\n"

    assert exit_code == 0


def test_handle_locations_args_get_configs_location(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    test_configs_file: Path = tmp_path / "configs.json"

    args: argparse.Namespace = argparse.Namespace(
        configs_location=test_configs_file,
        get_log_location=False,
        get_configs_location=True,
    )

    exit_code: int = handle_locations_args(args)

    assert capsys.readouterr().out == f"{test_configs_file}\n"

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
        get_configs_location=True,
    )

    exit_code: int = handle_locations_args(args)

    assert capsys.readouterr().out == f"{test_log_file}\n{test_configs_file}\n"

    assert exit_code == 0
    exit_code: int = handle_locations_args(args)

    assert capsys.readouterr().out == f"{test_log_file}\n{test_configs_file}\n"

    assert exit_code == 0
