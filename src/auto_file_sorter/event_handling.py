#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module that contains the event handler class to move a file to the correct path."""
from __future__ import annotations

__all__: list[str] = ["OnModifiedEventHandler"]

import logging
import os
import shutil
import signal
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import TYPE_CHECKING, Final

from watchdog.events import FileSystemEventHandler

from auto_file_sorter.constants import MOVE_LOG_LEVEL

if TYPE_CHECKING:
    from pathlib import Path

    from watchdog.events import DirModifiedEvent, FileModifiedEvent

_EVENT_HANDLING_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


class OnModifiedEventHandler(FileSystemEventHandler):
    """Handler for file-modified system events."""

    def __init__(
        self,
        tracked_path: Path,
        extension_paths: dict[str, Path],
    ) -> None:
        self.tracked_path: Path = tracked_path
        self.extension_paths: dict[str, Path] = extension_paths
        _EVENT_HANDLING_LOGGER.info("Initialized %s", self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}('{self.tracked_path}')"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(tracked_path={self.tracked_path!r}, "
            f"extension_paths={self.extension_paths!r})"
        )

    # Overriding method from FileSystemEventHandler
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        try:
            _EVENT_HANDLING_LOGGER.debug(event)
            with ThreadPoolExecutor() as executor:
                for child in self.tracked_path.iterdir():
                    if child.is_file() and child.suffix.lower() in self.extension_paths:
                        _EVENT_HANDLING_LOGGER.debug("Processing %s", child)
                        executor.submit(self._move_file, child)
                    else:
                        _EVENT_HANDLING_LOGGER.debug("Skipping %s", child)
        # Using os.kill instead of SystemExit because of threading
        except PermissionError as perm_err:
            pid: int = os.getpid()
            _EVENT_HANDLING_LOGGER.critical(
                "Permission denied in process %s, please check your OS or antivirus: %s",
                pid,
                perm_err,
            )
            os.kill(pid, signal.SIGTERM)
        except OSError as os_err:
            pid: int = os.getpid()
            _EVENT_HANDLING_LOGGER.critical(
                "Error in process %s while moving file: %s",
                pid,
                os_err,
            )
            os.kill(pid, signal.SIGTERM)
        except Exception as err:
            pid: int = os.getpid()
            _EVENT_HANDLING_LOGGER.exception(
                "Unexpected %s in process %s",
                err.__class__.__name__,
                pid,
            )
            os.kill(pid, signal.SIGTERM)

    def _move_file(self, file_name: Path) -> None:
        """Moves the file to its destination path."""
        destination_path: Path = self.extension_paths[file_name.suffix.lower()]
        _EVENT_HANDLING_LOGGER.debug(
            "Got '%s' extension path for '%s'",
            destination_path,
            file_name,
        )
        dated_destination_path: Path = self._add_date_to_path(destination_path)
        _EVENT_HANDLING_LOGGER.debug("Added date to %s", dated_destination_path)
        final_destination_path: Path = self._increment_file_name(
            dated_destination_path,
            file_name,
        )
        _EVENT_HANDLING_LOGGER.debug(
            "Processed optional incrementation for %s",
            file_name,
        )
        shutil.move(file_name, final_destination_path)
        _EVENT_HANDLING_LOGGER.log(
            MOVE_LOG_LEVEL,
            "Moved %s to %s",
            file_name,
            final_destination_path,
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
        Prevents FileExists exception and overwriting other files.
        """
        new_path: Path = destination / source.name
        if not new_path.exists():
            return new_path

        increment: int = 1
        while new_path.exists():
            increment += 1
            new_path = destination / f"{source.stem} ({increment}){source.suffix}"

        return new_path
