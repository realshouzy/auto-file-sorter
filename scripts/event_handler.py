# -*- coding: UTF-8 -*-
"""
Module that contains the class and helper functions needed to move a file to the correct path.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any

import shutil
import json
import logging
from datetime import date

from watchdog.events import FileSystemEventHandler


def add_date_to_path(path: Path) -> Path:
    """
    Helper function that adds current year/month to destination path. If the path
    doesn't already exist, it is created.

    :param Path path: destination root to append subdirectories based on date
    :rtype: Path
    """
    dated_path = path/Path(f'{date.today().strftime("%Y")}')/Path(f'{date.today().strftime("%b")}')
    dated_path.mkdir(parents=True, exist_ok=True)
    return dated_path


def rename_file(destination_path: Path, source: Path) -> Path:
    """
    Helper function that renames file to reflect new path. If a file of the same
    name already exists in the destination folder, the file name is numbered and
    incremented until the filename is unique (prevents overwriting files).

    :param Path source: source of file to be moved
    :param Path destination_path: path to destination directory
    :rtype: Path
    """
    if Path(destination_path/source.name).exists():
        increment = 0
        while True:
            increment += 1
            new_name = destination_path/f'{source.stem} ({increment}){source.suffix}'

            if not new_name.exists():
                return new_name
    else:
        return destination_path/source.name


def get_settings(option: str) -> dict[str, Path | int | str]:
    """
    Helper functions that returns an options dict from the settings json file.

    :param str option: option in the settings json file
    :rtype: dict[str, Path | str]
    """
    with open('settings.json', 'r') as f:
        settings = json.load(f)
    return settings[option]


class EventHandler(FileSystemEventHandler):
    def __init__(self, watch_path: Path, logging_level: int, log_format: str) -> None:
        """
        Initializes EventHandler instance.

        :param Path watch_path: path wich will be tracked
        :param int logging_level: logging level (0: NOTSET, 10: DEBUG, 20: INFO, 30: WARNING, 40: ERROR, 50: CRITICAL)
        :param str log_format: format string for the logger
        """
        self.watch_path: Path = watch_path.resolve()
        self.extension_paths: dict[str, Path] = get_settings('extensions')

        logging.basicConfig(filename='log.log', 
                            level=logging_level, 
                            format=log_format, 
                            filemode='w')
        self.logger: logging.Logger = logging.getLogger()
        self.logger.debug('Handler initialized')

    def on_modified(self, event: Any) -> None:
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
        except Exception as x:
            self.logger.exception(f'Unexpected {type(x).__name__}: {x}')