"""Module testing ``auto_file_sorter.event_handling.py``."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest
from watchdog.events import FileSystemEventHandler

from auto_file_sorter.event_handling import OnModifiedEventHandler

if TYPE_CHECKING:
    from pathlib import Path

# pylint: disable=C0116, W0212, W0621


@pytest.fixture()
def extension_paths(tmp_path: Path) -> dict[str, Path]:
    return {
        ".txt": tmp_path / "txt",
        ".doc": tmp_path / "doc",
    }


@pytest.fixture()
def path_for_undefined_extensions(tmp_path: Path) -> Path:
    return tmp_path.joinpath("undefined")


def test_on_modified_event_handler_base() -> None:
    assert OnModifiedEventHandler.__base__ == FileSystemEventHandler


def test_on_modified_event_handler_str(
    tmp_path: Path,
    extension_paths: dict[str, Path],
    path_for_undefined_extensions: Path,
) -> None:
    test_event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=path_for_undefined_extensions,
    )
    assert str(test_event_handler) == f"OnModifiedEventHandler('{tmp_path}')"


def test_on_modified_event_handler_str_no_path_for_undefined_extensions(
    tmp_path: Path,
    extension_paths: dict[str, Path],
) -> None:
    test_event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=None,
    )
    assert str(test_event_handler) == f"OnModifiedEventHandler('{tmp_path}')"


def test_on_modified_event_handler_repr(
    tmp_path: Path,
    extension_paths: dict[str, Path],
    path_for_undefined_extensions: Path,
) -> None:
    test_event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=path_for_undefined_extensions,
    )
    repr_of_test_event_handler: str = (
        f"OnModifiedEventHandler(tracked_path={tmp_path!r}, "
        f"extension_paths={extension_paths!r}, "
        f"path_for_undefined_extensions={path_for_undefined_extensions!r})"
    )
    assert repr(test_event_handler) == repr_of_test_event_handler


def test_on_modified_event_handler_repr_no_path_for_undefined_extensions(
    tmp_path: Path,
    extension_paths: dict[str, Path],
) -> None:
    test_event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=None,
    )
    repr_of_test_event_handler: str = (
        f"OnModifiedEventHandler(tracked_path={tmp_path!r}, "
        f"extension_paths={extension_paths!r}, "
        f"path_for_undefined_extensions={None!r})"
    )
    assert repr(test_event_handler) == repr_of_test_event_handler


def test_on_modified_event_handler_add_date_to_path(tmp_path: Path) -> None:
    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(tmp_path, {}, None)

    dated_path: Path = event_handler._add_date_to_path(tmp_path)  # type: ignore[unused-ignore]

    assert dated_path.exists()
    assert dated_path == tmp_path / f"{datetime.now():%Y/%b}"


def test_on_modified_event_handler_increment_file_name(tmp_path: Path) -> None:
    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(tmp_path, {}, None)

    file1: Path = tmp_path / "file.txt"
    file2: Path = tmp_path / "file (1).txt"
    file1.touch()
    file2.touch()

    incremented_path: Path = event_handler._increment_file_name(  # type: ignore
        tmp_path,
        file1,
    )

    assert incremented_path.name == "file (2).txt"


def test_on_modified_event_handler_move_file(
    tmp_path: Path,
    extension_paths: dict[str, Path],
) -> None:
    path_for_undefined_extensions: Path = tmp_path / "undefined"
    file_path: Path = tmp_path / "test_file.txt"
    destination_path: Path = extension_paths[".txt"]

    file_path.touch()

    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=path_for_undefined_extensions,
    )

    event_handler._move_file(file_path)  # type: ignore

    assert destination_path.exists()
    assert (destination_path / f"{datetime.now():%Y/%b}" / "test_file.txt").exists()


def test_on_modified_event_handler_on_modified_override() -> None:
    assert OnModifiedEventHandler.on_modified.__override__  # type: ignore[attr-defined] # pylint: disable=E1101


@pytest.mark.skip(reason="Test needs to be written")
def test_on_modified_event_handler_on_modified() -> None:
    ...
