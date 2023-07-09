#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module that contains the event handler class to move a file to the correct path."""
from __future__ import annotations

__all__: list[str] = ["OnModifiedEventHandler"]

import logging
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import TYPE_CHECKING, Optional

from watchdog.events import FileSystemEventHandler

from auto_file_sorter.constants import MOVE_LOG_LEVEL

if TYPE_CHECKING:
    from pathlib import Path

    from watchdog.events import DirModifiedEvent, FileModifiedEvent

event_handling_logger: logging.Logger = logging.getLogger(__name__)


class OnModifiedEventHandler(FileSystemEventHandler):
    """Handler for file-modified system events."""

    def __init__(
        self,
        tracked_path: Path,
        extension_paths: dict[str, Path],
        path_for_undefined_extensions: Optional[Path],
    ) -> None:
        self.tracked_path: Path = tracked_path
        self.extension_paths: dict[str, Path] = extension_paths
        self.path_for_undefined_extensions: Optional[
            Path
        ] = path_for_undefined_extensions
        event_handling_logger.info("Initialized %s", self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}('{self.tracked_path}')"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(tracked_path={self.tracked_path!r}, "
            f"extension_paths={self.extension_paths!r}, "
            f"path_for_undefined_extensions={self.path_for_undefined_extensions!r})"
        )

    # Overriding method from FileSystemEventHandler
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        event_handling_logger.debug("event=%s", repr(event))
        with ThreadPoolExecutor() as executor:
            for child in self.tracked_path.iterdir():
                if child.is_file():
                    event_handling_logger.debug("Processing '%s'", child)
                    executor.submit(self._move_file, child)
                else:
                    event_handling_logger.debug("Skipping directory: '%s'", child)

    def _move_file(self, file_path: Path) -> None:
        """Moves the file to its destination path."""
        destination_path: Optional[Path] = self.extension_paths.get(
            file_path.suffix.lower(),
            self.path_for_undefined_extensions,
        )

        if destination_path is None:
            event_handling_logger.warning(
                "Skipping '%s', because no path was defined in the configs "
                "and no path for undefined extensions was specified",
                file_path,
            )
            return

        event_handling_logger.debug(
            "Got '%s' extension path for '%s'",
            destination_path,
            file_path,
        )
        try:
            dated_destination_path: Path = self._add_date_to_path(destination_path)
            event_handling_logger.debug("Added date to %s", dated_destination_path)
            final_destination_path: Path = self._increment_file_name(
                dated_destination_path,
                file_path,
            )
            event_handling_logger.debug(
                "Processed optional incrementation for '%s'",
                file_path,
            )
            shutil.move(file_path, final_destination_path)
            event_handling_logger.log(
                MOVE_LOG_LEVEL,
                "Moved %s to %s",
                file_path,
                final_destination_path,
            )
        except PermissionError as perm_err:
            pid: int = os.getpid()
            event_handling_logger.critical(
                "Permission denied in process %s, please check your OS or antivirus: %s",
                pid,
                perm_err,
            )
        except FileNotFoundError as file_not_found_err:
            pid: int = os.getpid()
            event_handling_logger.error(
                "File not found in process %s while moving %s: %s",
                pid,
                file_path,
                file_not_found_err,
            )
        except (OSError, shutil.Error) as os_err:
            pid: int = os.getpid()
            event_handling_logger.critical(
                "Error in process %s while moving file: %s",
                pid,
                os_err,
            )
        except Exception as err:
            pid: int = os.getpid()
            event_handling_logger.exception(
                "Unexpected %s in process %s",
                err.__class__.__name__,
                pid,
            )

    @staticmethod
    def _add_date_to_path(path: Path) -> Path:
        """Adds current year/month to destination path. If the path
        doesn't already exist, it is created.
        """
        dated_path: Path = path / f"{date.today():%Y/%b}"
        dated_path.mkdir(parents=True, exist_ok=True)
        return dated_path

    @staticmethod
    def _increment_file_name(destination: Path, source: Path) -> Path:
        """If a file of the same name already exists in the destination folder,
        the file name is numbered and incremented until the filename is unique.
        This prevents overwriting other files.
        """
        new_path: Path = destination / source.name
        if not new_path.exists():
            return new_path

        increment: int = 1
        while new_path.exists():
            increment += 1
            new_path = destination / f"{source.stem} ({increment}){source.suffix}"

        return new_path
