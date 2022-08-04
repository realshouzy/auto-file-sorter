#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
from __future__ import annotations
from pathlib import Path

from time import sleep
from watchdog.observers import Observer

from event_handler import EventHandler, get_settings


def main() -> None:
    WATCH_PATH = Path(get_settings('general')['trackedPath'])
    LOGGING_LEVEL = get_settings('general')['loggingLevel']
    LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
    event_handler = EventHandler(watch_path=WATCH_PATH, 
                                               logging_level=LOGGING_LEVEL, 
                                               log_format=LOG_FORMAT)

    observer = Observer()
    observer.schedule(event_handler, f'{WATCH_PATH}', recursive=True)
    observer.start()

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()