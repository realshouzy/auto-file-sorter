# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations
from pathlib import Path

import logging
from time import sleep
from watchdog.observers import Observer

from utils.event_handler import EventHandler
from utils.settings_handler import open_settings


def main() -> None:
    """Runs the program."""
    with open_settings() as settings:
        WATCH_PATH = Path(settings['general']['trackedPath'])
        EXTENSION_PATHS = dict(settings['extensions'])
        LOGGING_LEVEL = int(settings['general']['loggingLevel'])
        LOG_FORMAT = str(settings['general']['loggingFormat'])

    logging.basicConfig(filename='log.log',
                        level=LOGGING_LEVEL,
                        format=LOG_FORMAT,
                        filemode='w')
    main_logger = logging.getLogger('Main logger')
    event_handler = EventHandler(watch_path=WATCH_PATH, extension_paths=EXTENSION_PATHS)

    observer = Observer()
    observer.schedule(event_handler, f'{WATCH_PATH}', recursive=True)
    observer.start()
    main_logger.info('Started observer')

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        observer.stop()
        main_logger.info('Stopped observer')
    observer.join()


if __name__ == '__main__':
    main()