#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
from __future__ import annotations
from pathlib import Path

from time import sleep
import PySimpleGUI as sg
import logging
from watchdog.observers import Observer

from event_handler import EventHandler, get_settings


def main() -> None:
    WATCH_PATH = Path(get_settings('general')['tracked_path'])
    LOGGING_FLAG = get_settings('general')['logging']
    event_handler = EventHandler(watch_path=WATCH_PATH, logging_flag=LOGGING_FLAG)

    observer = Observer()
    observer.schedule(event_handler, f'{WATCH_PATH}', recursive=True)
    observer.start()

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        print('\nstopped')
        observer.stop()
    # except Exception as x:
    #     sg.PopupError('Unexpected error')
    #     observer.stop()
    observer.join()


if __name__ == '__main__':
    main()