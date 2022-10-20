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
    dated_path: Path = path / Path(f"{date.today():%Y/%b}")
    dated_path.mkdir(parents=True, exist_ok=True)
    return dated_path


def rename_file(destination: Path, source: Path) -> Path:
    """
    Helper function that renames file to reflect new path. If a file of the same
    name already exists in the destination folder, the file name is numbered and
    incremented until the filename is unique (prevents overwriting files). Prevents FileExists exception.

    :param Path source: source of file to be moved
    :param Path destination_path: path to destination directory
    :rtype: Path
    """
    if not Path(destination / source.name).exists():
        return destination / source.name

    increment: int = 0
    while True:
        increment += 1
        new_path: Path = destination / f"{source.stem} ({increment}){source.suffix}"

        if not new_path.exists():
            return new_path
