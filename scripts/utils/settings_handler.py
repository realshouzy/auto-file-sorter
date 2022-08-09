# -*- coding: UTF-8 -*-
"""
Context manager for settings handling.
"""
from __future__ import annotations
from typing import Any, Generator

from contextlib import contextmanager
import json
import PySimpleGUI as sg


@contextmanager
def open_settings() -> Generator[Any, None, None]:
    """
    Function that creates context manager for easy access to the settings json file and exception handling.

    :rtype: Generator[Any, None, None]
    """
    try:
        file = open('settings.json', 'r')
        yield json.load(file)
    except FileNotFoundError:
        sg.PopupError(f'{__file__}:\nSettings json file not found. Must be located in the same directory as the executable.', title='FileSorter')
        exit()
    except KeyError:
        sg.PopupError(f'{__file__}:\nSettings json file is not correctly configured.', title='FileSorter')
        exit()
    finally:
        if file:
            file.close()