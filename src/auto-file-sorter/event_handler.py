#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module that contains the event handler class to move a file to the correct path."""
from __future__ import annotations

import logging
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from watchdog.events import FileSystemEventHandler

if TYPE_CHECKING:
    from watchdog.events import DirModifiedEvent, FileModifiedEvent

__all__: list[str] = ["FileModifiedEventHandler"]


class FileModifiedEventHandler(FileSystemEventHandler):
    """Handler file system events."""

    def __init__(self, tracked_path: Path, extension_paths: dict[str, str]) -> None:
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        self.tracked_path: Path = tracked_path.resolve()
        self.extension_paths: dict[str, Path] = {
            key: Path(path).resolve() for key, path in extension_paths.items()
        }
        self.logger.debug("Resolved all given paths")

        self.logger.info("Initialized handler: %s", self)

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        try:
            self.logger.debug(event)
            with ThreadPoolExecutor() as executor:
                for child in self.tracked_path.iterdir():
                    if child.is_file() and child.suffix.lower() in self.extension_paths:
                        self.logger.debug("Processing %s", child)
                        executor.submit(self.move_file, child)
                    else:
                        self.logger.debug("Skipping %s", child)
        except PermissionError as perm_exce:
            self.logger.critical(
                "%s -> please check your OS or Anti-Virus settings",
                perm_exce,
            )
            raise SystemExit(1) from perm_exce
        except OSError as os_exce:
            self.logger.critical(
                "%s -> error while moving file",
                os_exce,
            )
        except Exception as exce:  # pylint: disable=broad-exception-caught
            self.logger.exception("Unexpected %s", exce.__class__.__name__)

    def move_file(self, file: Path) -> None:
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
