"""Module testing ``auto_file_sorter.event_handling.py``."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler

# pylint: disable=C0116, W0212, W0611, W0621
from auto_file_sorter.event_handling import OnModifiedEventHandler
from tests.fixtures import extension_paths, path_for_undefined_extensions

if TYPE_CHECKING:
    from pathlib import Path


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

    dated_path: Path = event_handler._add_date_to_path(tmp_path)

    assert dated_path.exists()
    assert dated_path == tmp_path / f"{datetime.now():%Y/%b}"


def test_on_modified_event_handler_increment_file_name(tmp_path: Path) -> None:
    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(tmp_path, {}, None)

    file1: Path = tmp_path / "file.txt"
    file2: Path = tmp_path / "file (1).txt"
    file1.touch()
    file2.touch()

    incremented_path: Path = event_handler._increment_file_name(
        tmp_path,
        file1,
    )

    assert incremented_path.name == "file (2).txt"


def test_on_modified_event_handler_move_file(
    tmp_path: Path,
    extension_paths: dict[str, Path],
) -> None:
    file_path: Path = tmp_path / "test_file.txt"
    file_path.touch()

    destination_path: Path = extension_paths[".txt"]

    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=None,
    )

    event_handler._move_file(file_path)

    assert destination_path.exists()
    assert (destination_path / f"{datetime.now():%Y/%b}" / "test_file.txt").exists()


def test_on_modified_event_handler_move_file_undefined_extension(
    tmp_path: Path,
    extension_paths: dict[str, Path],
    path_for_undefined_extensions: Path,
) -> None:
    file_path: Path = tmp_path / "test_file.idk"
    file_path.touch()

    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=path_for_undefined_extensions,
    )

    event_handler._move_file(file_path)

    assert path_for_undefined_extensions.exists()
    assert (
        path_for_undefined_extensions / f"{datetime.now():%Y/%b}" / "test_file.idk"
    ).exists()


def test_on_modified_event_handler_move_file_permission_error_no_exit(
    tmp_path: Path,
    extension_paths: dict[str, Path],
) -> None:
    file_path: Path = tmp_path / "test_file.txt"
    file_path.touch()

    destination_path: Path = extension_paths[".txt"]
    destination_path.touch()
    destination_path.chmod(0000)

    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=None,
    )

    event_handler._move_file(file_path)

    assert destination_path.exists()
    assert not (destination_path / f"{datetime.now():%Y/%b}" / "test_file.txt").exists()


def test_on_modified_event_handler_move_file_file_not_found_error_no_exit(
    tmp_path: Path,
    extension_paths: dict[str, Path],
) -> None:
    file_path: Path = tmp_path / "test_file.txt"
    destination_path: Path = extension_paths[".txt"]

    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=None,
    )

    event_handler._move_file(file_path)

    assert destination_path.exists()
    assert not (destination_path / f"{datetime.now():%Y/%b}" / "test_file.txt").exists()


def test_on_modified_event_handler_move_file_increment(
    tmp_path: Path,
    extension_paths: dict[str, Path],
) -> None:
    file_path2: Path = tmp_path / "test_file.txt"
    file_path2.touch()

    destination_path: Path = extension_paths[".txt"]

    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=None,
    )

    event_handler._move_file(file_path2)

    assert destination_path.exists()
    assert (destination_path / f"{datetime.now():%Y/%b}" / "test_file.txt").exists()

    file_path2: Path = tmp_path / "test_file.txt"
    file_path2.touch()

    event_handler._move_file(file_path2)

    assert (destination_path / f"{datetime.now():%Y/%b}" / "test_file (2).txt").exists()


def test_on_modified_event_handler_on_modified_override() -> None:
    assert OnModifiedEventHandler.on_modified.__override__  # type: ignore[attr-defined]  # pylint: disable=E1101


def test_on_modified_event_handler_on_modified(
    tmp_path: Path,
    extension_paths: dict[str, Path],
) -> None:
    file_path: Path = tmp_path / "test_file.txt"
    file_path.touch()

    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=None,
    )

    event: FileModifiedEvent = FileModifiedEvent(file_path)  # type: ignore

    event_handler.on_modified(event)

    destination_path: Path = extension_paths[".txt"]

    # Assert that the file was moved to its correct destination
    assert destination_path.exists()
    assert (destination_path / f"{datetime.now():%Y/%b}" / "test_file.txt").exists()


def test_on_modified_event_handler_on_modified_skip_directory(
    tmp_path: Path,
    extension_paths: dict[str, Path],
) -> None:
    subdirectory: Path = tmp_path / "subdir"
    subdirectory.mkdir()

    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=None,
    )

    event: DirModifiedEvent = DirModifiedEvent(subdirectory)  # type: ignore

    event_handler.on_modified(event)

    destination_path: Path = extension_paths[".txt"]

    assert not destination_path.exists()
    assert not (destination_path / f"{datetime.now():%Y/%b}").exists()


def test_on_modified_event_handler_on_modified_undefined_extension(
    tmp_path: Path,
    extension_paths: dict[str, Path],
    path_for_undefined_extensions: Path,
) -> None:
    file_path: Path = tmp_path / "test_file.idk"
    file_path.touch()

    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=path_for_undefined_extensions,
    )

    event: FileModifiedEvent = FileModifiedEvent(file_path)  # type: ignore

    event_handler.on_modified(event)

    assert path_for_undefined_extensions.exists()
    assert (
        path_for_undefined_extensions / f"{datetime.now():%Y/%b}" / "test_file.idk"
    ).exists()


def test_on_modified_event_handler_on_modified_permission_error(
    tmp_path: Path,
    extension_paths: dict[str, Path],
) -> None:
    file_path: Path = tmp_path / "test_file.txt"
    file_path.touch()

    destination_path: Path = extension_paths[".txt"]
    destination_path.touch()
    destination_path.chmod(0)

    event_handler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=None,
    )

    event: FileModifiedEvent = FileModifiedEvent(file_path)  # type: ignore

    event_handler.on_modified(event)

    assert destination_path.exists()
    assert not (destination_path / f"{datetime.now():%Y/%b}" / "test_file.txt").exists()


def test_on_modified_event_handler_on_modified_file_not_found_error(
    tmp_path: Path,
    extension_paths: dict[str, Path],
) -> None:
    file_path: Path = tmp_path / "test_file.txt"
    destination_path: Path = extension_paths[".txt"]

    event_handler: OnModifiedEventHandler = OnModifiedEventHandler(
        tmp_path,
        extension_paths,
        path_for_undefined_extensions=None,
    )

    event: FileModifiedEvent = FileModifiedEvent(file_path)  # type: ignore

    event_handler.on_modified(event)

    assert not destination_path.exists()
    assert not (destination_path / f"{datetime.now():%Y/%b}" / "test_file.txt").exists()
