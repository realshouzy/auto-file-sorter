#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module that contains the event handler class to move a file to the correct path."""
from __future__ import annotations

import logging
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING

import PySimpleGUI as sg
from watchdog.events import FileSystemEventHandler

from .helper_funcs import add_date_to_path, increment_file_name

if TYPE_CHECKING:
    from watchdog.events import DirModifiedEvent, FileModifiedEvent

__all__: list[str] = ["FileModifiedEventHandler"]


class FileModifiedEventHandler(FileSystemEventHandler):
    """Class to handle file system events."""

    def __init__(self, tracked_path: str, extension_paths: dict[str, str]) -> None:
        self.tracked_path: Path = Path(tracked_path).resolve()
        self.extension_paths: dict[str, Path] = {
            key: Path(path).resolve() for key, path in extension_paths.items()
        }

        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Handler initialized")

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
        except PermissionError as os_exce:
            self.logger.critical(
                "%s -> please check your OS or Anti-Virus settings",
                os_exce,
            )
            sg.PopupError(
                "Permission denied, check log for more info",
                title="auto-file-sorter",
            )
            raise SystemExit(1) from os_exce
        except OSError as os_exce:
            self.logger.critical(
                "%s -> error while moving file",
                os_exce,
            )
            sg.PopupError(
                "An OS error occurred",
                title="auto-file-sorter",
            )
        except Exception as exce:  # pylint: disable=broad-exception-caught
            self.logger.exception("Unexpected %s", exce.__class__.__name__)

    def move_file(self, file: Path) -> None:
        """Moves the file to its destination path."""
        destination_path: Path = self.extension_paths[file.suffix.lower()]
        self.logger.debug("Got extension path for %s", file)
        destination_path = add_date_to_path(destination_path)
        self.logger.debug("Added date to %s", destination_path)
        destination_path = increment_file_name(destination_path, file)
        self.logger.debug("Processed optional incrementation for %s", file)
        shutil.move(file, destination_path)
        self.logger.info("Moved %s to %s", file, destination_path)
