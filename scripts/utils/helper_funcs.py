# -*- coding: UTF-8 -*-
"""Module that contains all helper functions needed to successfully move a file to the correct path."""
from __future__ import annotations
from pathlib import Path

from datetime import date

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
    incremented until the filename is unique (prevents overwriting files). Prevents FileExists exception.

    :param Path source: source of file to be moved
    :param Path destination_path: path to destination directory
    :rtype: Path
    """
    if Path(destination_path/source.name).exists():
        increment = 0
        while True:
            increment += 1
            new_path = destination_path/f'{source.stem} ({increment}){source.suffix}'

            if not new_path.exists():
                return new_path
    else:
        return destination_path/source.name