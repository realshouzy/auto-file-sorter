#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module that contains the event handler class to move a file to the correct path."""
from __future__ import annotations

import logging
import os
import shutil
import signal
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import TYPE_CHECKING, Self

from watchdog.events import FileSystemEventHandler

if TYPE_CHECKING:
    from pathlib import Path

    from watchdog.events import DirModifiedEvent, FileModifiedEvent

__all__: list[str] = ["FileModifiedEventHandler"]


class FileModifiedEventHandler(FileSystemEventHandler):
    """Handler for file-modified system events."""

    def __init__(
        self,
        tracked_path: Path,
        extension_paths: dict[str, Path],
    ) -> None:
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        self.tracked_path: Path = tracked_path
        self.extension_paths: dict[str, Path] = extension_paths

        self.logger.info("Initialized %s", self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}('{self.tracked_path}')"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(tracked_path={self.tracked_path!r}, extension_paths={self.extension_paths!r})"

    def __reduce__(self) -> tuple[type[Self], tuple[Path, dict[str, Path]]]:
        return self.__class__, (self.tracked_path, self.extension_paths)

    def on_modified(  # overriding method from FileSystemEventHandler
        self,
        event: DirModifiedEvent | FileModifiedEvent,
    ) -> None:
        try:
            self.logger.debug(event)
            with ThreadPoolExecutor() as executor:
                for child in self.tracked_path.iterdir():
                    if child.is_file() and child.suffix.lower() in self.extension_paths:
                        self.logger.debug("Processing %s", child)
                        executor.submit(self._move_file, child)
                    else:
                        self.logger.debug("Skipping %s", child)
        # os.kill instead of SystemExit because of threading
        except PermissionError as perm_err:
            pid: int = os.getpid()
            self.logger.critical(
                "Permission denied in process %s, please check your OS or antivirus: %s",
                pid,
                perm_err,
            )
            os.kill(pid, signal.SIGINT)
        except OSError as os_err:
            pid: int = os.getpid()  # type: ignore[no-redef]
            self.logger.critical(
                "Error in process %s while moving file: %s",
                pid,
                os_err,
            )
            os.kill(pid, signal.SIGINT)
        except Exception as err:  # pylint: disable=broad-exception-caught
            pid: int = os.getpid()  # type: ignore[no-redef]
            self.logger.exception(
                "Unexpected %s in process %s",
                err.__class__.__name__,
                pid,
            )
            os.kill(pid, signal.SIGINT)

    def _move_file(self, file_name: Path) -> None:
        """Moves the file to its destination path."""
        destination_path: Path = self.extension_paths[file_name.suffix.lower()]
        self.logger.debug(
            "Got '%s' extension path for '%s'",
            destination_path,
            file_name,
        )
        dated_destination_path: Path = self.add_date_to_path(destination_path)
        self.logger.debug("Added date to %s", dated_destination_path)
        final_destination_path: Path = self.increment_file_name(
            dated_destination_path,
            file_name,
        )
        self.logger.debug("Processed optional incrementation for %s", file_name)
        shutil.move(file_name, final_destination_path)
        self.logger.log(60, "Moved %s to %s", file_name, final_destination_path)

    @staticmethod
    def add_date_to_path(path: Path) -> Path:
        """Adds current year/month to destination path. If the path
        doesn't already exist, it is created.
        """
        dated_path: Path = path / f"{date.today():%Y/%b}"
        dated_path.mkdir(parents=True, exist_ok=True)
        return dated_path

    @staticmethod
    def increment_file_name(destination: Path, source: Path) -> Path:
        """If a file of the same name already exists in the destination folder,
        the file name is numbered and incremented until the filename is unique.
        Prevents FileExists exception and overwriting other files.
        """
        new_path: Path = destination / source.name
        if not new_path.exists():
            return new_path

        increment: int = 1
        while new_path.exists():
            new_path = destination / f"{source.stem} ({increment}){source.suffix}"
            increment += 1

        return new_path
