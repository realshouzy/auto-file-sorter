#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module that contains the event handler class to move a file to the correct path."""
from __future__ import annotations

import logging
import shutil
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

    def __init__(self, tracked_path: Path, extension_paths: dict[str, Path]) -> None:
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        self.tracked_path: Path = tracked_path
        self.extension_paths: dict[str, Path] = extension_paths

        self.logger.info("Initialized handler: %s", self)

    def __str__(self) -> str:
        return ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(tracked_path={self.tracked_path!r}, extension_paths={self.extension_paths!r})"

    def __reduce__(self) -> tuple[type[Self], tuple[Path, dict[str, Path]]]:
        return self.__class__, (self.tracked_path, self.extension_paths)

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        try:
            self.logger.debug(event)
            with ThreadPoolExecutor() as executor:
                for child in self.tracked_path.iterdir():
                    if child.is_file() and child.suffix.lower() in self.extension_paths:
                        self.logger.debug("Processing %s", child)
                        executor.submit(self._move_file, child)
                    else:
                        self.logger.debug("Skipping %s", child)
        except PermissionError as perm_err:
            self.logger.critical(
                "%s -> please check your OS or Anti-Virus settings",
                perm_err,
            )
            raise SystemExit(1) from perm_err
        except OSError as os_err:
            self.logger.critical(
                "%s -> error while moving file",
                os_err,
            )
        except Exception as err:  # pylint: disable=broad-exception-caught
            self.logger.exception("Unexpected %s", err.__class__.__name__)

    def _move_file(self, file: Path) -> None:
        """Moves the file to its destination path."""
        destination_path: Path = self.extension_paths[file.suffix.lower()]
        self.logger.debug("Got extension path for %s", file)
        destination_path = self.add_date_to_path(destination_path)
        self.logger.debug("Added date to %s", destination_path)
        destination_path = self.increment_file_name(destination_path, file)
        self.logger.debug("Processed optional incrementation for %s", file)
        shutil.move(file, destination_path)
        self.logger.info("Moved %s to %s", file, destination_path)

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
