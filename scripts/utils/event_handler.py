# -*- coding: UTF-8 -*-
"""Module that contains the class and helper functions needed to move a file to the correct path."""
from __future__ import annotations
from typing import NoReturn, Optional
from pathlib import Path

import sys
import shutil
import logging
import PySimpleGUI as sg

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from .helper_funcs import add_date_to_path, rename_file


class EventHandler(FileSystemEventHandler):
    """Class to handle file system events."""
    def __init__(self, watch_path: Path, extension_paths: dict[str, Path]) -> None:
        """
        Initializes EventHandler instance.

        :param Path watch_path: path wich will be tracked
        :param int logging_level: logging level (0: NOTSET, 10: DEBUG, 20: INFO, 30: WARNING, 40: ERROR, 50: CRITICAL)
        :param str log_format: format string for the logger
        """
        self.watch_path: Path = watch_path.resolve()
        self.extension_paths: dict[str, Path] = extension_paths

        self.logger: logging.Logger = logging.getLogger('EventHandler logger')
        self.logger.debug('Handler initialized')


    def on_modified(self, event: FileSystemEvent) -> Optional[NoReturn]:
        try:
            self.logger.debug(event)
            for child in self.watch_path.iterdir():
                # skips directories and non-specified extensions
                if child.is_file() and child.suffix.lower() in self.extension_paths:
                    destination_path = self.extension_paths[child.suffix.lower()]
                    self.logger.debug('Got extension paths')
                    destination_path = add_date_to_path(path=destination_path)
                    self.logger.debug('Ran date check')
                    destination_path = rename_file(source=child, destination_path=destination_path)
                    self.logger.debug('Ran rename check')
                    shutil.move(src=child, dst=destination_path)
                    self.logger.info(f'Moved {child} to {destination_path}')
        except PermissionError as pe:
            self.logger.critical(f'{pe} -> please check your OS or Anti-Virus settings')
            sg.PopupError('Permission denied, check log for more info', title='FileSorter')
            sys.exit(1)
        except Exception as ex:
            self.logger.exception(f'Unexpected {type(ex).__name__}: {ex}')