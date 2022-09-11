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
        watch_path: Path = Path(settings["general"]["trackedPath"])
        extension_paths: dict[str, Path] = dict(settings["extensions"])
        logging_level: int = int(settings["general"]["loggingLevel"])
        log_format: str = str(settings["general"]["loggingFormat"])

    logging.basicConfig(
        filename="log.log", level=logging_level, format=log_format, filemode="w"
    )
    main_logger = logging.getLogger("Main logger")
    event_handler = EventHandler(watch_path=watch_path, extension_paths=extension_paths)

    observer = Observer()
    observer.schedule(event_handler, f"{watch_path}", recursive=True)
    observer.start()
    main_logger.info("Started observer")

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        observer.stop()
        main_logger.info("Stopped observer")
    observer.join()


if __name__ == "__main__":
    main()
