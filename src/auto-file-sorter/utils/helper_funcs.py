#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module that contains all helper functions needed to successfully move a file to the correct path."""
from __future__ import annotations

import os
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

__all__: list[str] = ["add_date_to_path", "increment_file_name", "get_file_path"]


def get_file_path(file_name: str) -> str:
    """Returns the path of the given file name in the current script dirctory."""
    current_script_dir: str = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_script_dir, "..", file_name)


def add_date_to_path(path: Path) -> Path:
    """Helper function that adds current year/month to destination path. If the path
    doesn't already exist, it is created.

    :param Path path: destination root to append subdirectories based on date
    :rtype: Path
    """
    dated_path: Path = path / f"{date.today():%Y/%b}"
    dated_path.mkdir(parents=True, exist_ok=True)
    return dated_path


def increment_file_name(destination: Path, source: Path) -> Path:
    """Helper function that renames file to reflect new path. If a file of the same
    name already exists in the destination folder, the file name is numbered and
    incremented until the filename is unique (prevents overwriting files). Prevents FileExists exception.

    :param Path source: source of file to be moved
    :param Path destination_path: path to destination directory
    :rtype: Path
    """
    new_path: Path = destination / source.name
    if not new_path.exists():
        return new_path

    increment: int = 1
    while new_path.exists():
        new_path = destination / f"{source.stem} ({increment}){source.suffix}"
        increment += 1

    return new_path
