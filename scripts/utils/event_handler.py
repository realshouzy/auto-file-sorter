# -*- coding: UTF-8 -*-
"""Module that contains the class and helper functions needed to move a file to the correct path."""
from __future__ import annotations
from typing import NoReturn, Optional
from pathlib import Path

import sys
import shutil
import logging

import PySimpleGUI as sg
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, DirModifiedEvent
from .helper_funcs import add_date_to_path, rename_file


class EventHandler(FileSystemEventHandler):
    """Class to handle file system events."""

    def __init__(self, watch_path: Path, extension_paths: dict[str, Path]) -> None:
        """Initializes EventHandler instance.

        :param Path watch_path: path wich will be tracked
        :param dict[str, Path] extension_paths: dictionary mapping extension to their paths
        """
        self.watch_path: Path = watch_path.resolve()
        self.extension_paths: dict[str, Path] = extension_paths

        self.logger: logging.Logger = logging.getLogger("EventHandler logger")
        self.logger.debug("Handler initialized")

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> Optional[NoReturn]:  # type: ignore
        try:
            self.logger.debug(event)
            for child in self.watch_path.iterdir():
                # skips directories and non-specified extensions
                if child.is_file() and child.suffix.lower() in self.extension_paths:
                    destination_path: Path = self.extension_paths[child.suffix.lower()]
                    self.logger.debug("Got extension paths")
                    destination_path = add_date_to_path(destination_path)
                    self.logger.debug("Ran date check")
                    destination_path = rename_file(
                        source=child, destination=destination_path
                    )
                    self.logger.debug("Ran rename check")
                    shutil.move(src=child, dst=destination_path)
                    self.logger.info("Moved %s to %s", child, destination_path)
        except PermissionError as perm_exce:
            self.logger.critical(
                "%s -> please check your OS or Anti-Virus settings", perm_exce
            )
            sg.PopupError(
                "Permission denied, check log for more info", title="FileSorter"
            )
            sys.exit(1)
        except Exception as exce:
            self.logger.exception("Unexpected %s", exce.__class__.__name__)
