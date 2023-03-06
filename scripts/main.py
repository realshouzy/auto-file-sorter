# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

import logging
from pathlib import Path
from time import sleep

from utils.event_handler import EventHandler
from utils.settings_handler import open_settings
from watchdog.observers import Observer


def main() -> None:
    """Runs the program."""
    with open_settings() as settings:
        watch_path: Path = Path(settings["general"]["trackedPath"])  # type: ignore
        extension_paths: dict[str, Path] = settings["extensions"]  # type: ignore
        logging_level: int = settings["general"]["loggingLevel"]  # type: ignore
        log_format: str = settings["general"]["loggingFormat"]  # type: ignore

    logging.basicConfig(
        filename="log.log",
        level=logging_level,
        format=log_format,
        filemode="w",
    )
    main_logger: logging.Logger = logging.getLogger("Main logger")
    event_handler: EventHandler = EventHandler(
        watch_path=watch_path,
        extension_paths=extension_paths,
    )

    observer: Observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()
    main_logger.info("Started observer")

    try:
        while True:
            sleep(60)
    finally:
        observer.stop()
        observer.join()
        main_logger.info("Stopped observer")


if __name__ == "__main__":
    main()
