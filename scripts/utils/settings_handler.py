# -*- coding: UTF-8 -*-
"""Context manager for settings handling."""
from __future__ import annotations
from typing import Iterator, TypeAlias
from pathlib import Path

from contextlib import contextmanager
import sys
import json
import PySimpleGUI as sg

Settings: TypeAlias = dict[str, dict[str, Path | int | str]]

@contextmanager
def open_settings() -> Iterator[Settings]:
    """
    Function that creates context manager for easy access to the settings json file with exception handling.

    :rtype: Iterator[dict[str, dict[str, Path | int | str]]]
    """
    try:
        file = open('settings.json', 'r')
        yield json.load(file)
        file.close()
    except FileNotFoundError:
        sg.PopupError(f'{__file__}:\nSettings json file not found. Must be located in the same directory as the executable.', title='FileSorter')
        sys.exit(1)
    except KeyError:
        sg.PopupError(f'{__file__}:\nSettings json file is not correctly configured.', title='FileSorter')
        file.close()
        sys.exit(1)
    except Exception as x:
        sg.PopupError(f'Unexpected {type(x).__name__} -> check log for more info.')