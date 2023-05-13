#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module that contains the class and helper functions needed to move a file to the correct path."""
from __future__ import annotations

import logging
import shutil
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import TYPE_CHECKING

import PySimpleGUI as sg
from watchdog.events import FileSystemEventHandler

from .helper_funcs import add_date_to_path, rename_file

if TYPE_CHECKING:
    from watchdog.events import DirModifiedEvent, FileModifiedEvent

__all__: list[str] = ["EventHandler"]


class EventHandler(FileSystemEventHandler):
    """Class to handle file system events."""

    def __init__(self, watch_path: Path, extension_paths: dict[str, str]) -> None:
        """Initializes EventHandler instance.

        :param Path watch_path: path wich will be tracked
        :param dict[str, str] extension_paths: dictionary mapping extension to their paths
        """
        self.watch_path: Path = watch_path.resolve()
        self.extension_paths: dict[str, str] = extension_paths

        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Handler initialized")

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        try:
            self.logger.debug(event)
            with ThreadPool() as pool:  # type: ignore
                for child in self.watch_path.iterdir():
                    if child.is_file() and child.suffix.lower() in self.extension_paths:
                        self.logger.debug("Processing file: %s", child)
                        pool.apply(self.move_file, (child,))
                    else:
                        self.logger.debug("Skipping file: %s", child)
        except PermissionError as perm_exce:
            self.logger.critical(
                "%s -> please check your OS or Anti-Virus settings",
                perm_exce,
            )
            sg.PopupError(
                "Permission denied, check log for more info",
                title="FileSorter",
            )
            raise SystemExit(1) from perm_exce
        except Exception as exce:  # pylint: disable=broad-exception-caught
            self.logger.exception("Unexpected %s", exce.__class__.__name__)

    def move_file(self, file: Path) -> None:
        "Moves the file to its destination path."
        destination_path: Path = Path(self.extension_paths[file.suffix.lower()])
        self.logger.debug("Got extension path for %s", file)
        destination_path = add_date_to_path(destination_path)
        self.logger.debug("Ran date check for %s", destination_path)
        destination_path = rename_file(
            source=file,
            destination=destination_path,
        )
        self.logger.debug("Ran rename check for %s", file)
        shutil.move(src=file, dst=destination_path)
        self.logger.info("Moved %s to %s", file, destination_path)
