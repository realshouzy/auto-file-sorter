# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from time import sleep
from typing import Optional, Sequence

from watchdog.observers import Observer

from .utils.event_handler import EventHandler
from .utils.helper_funcs import get_file_path
from .utils.settings_handler import open_settings


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Runs the program."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--settings",
        default=get_file_path("settings.json"),
        help="path to settings.json file",
    )
    parser.add_argument(
        "-l",
        "--log",
        default=get_file_path("log.log"),
        help="path to log.log file",
    )
    args = parser.parse_args(argv)

    with open_settings(args.settings) as settings:
        watch_path: Path = Path(settings["general"]["trackedPath"])  # type: ignore
        extension_paths: dict[str, str] = dict(settings["extensions"])  # type: ignore
        logging_level: int = int(settings["general"]["loggingLevel"])
        log_format: str = str(settings["general"]["loggingFormat"])

    logging.basicConfig(
        filename=args.log,
        level=logging_level,
        format=log_format,
        filemode="w",
    )
    main_logger: logging.Logger = logging.getLogger(__name__)
    event_handler: EventHandler = EventHandler(
        watch_path=watch_path,
        extension_paths=extension_paths,
    )

    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()
    main_logger.info("Started observer: %s", observer)

    try:
        while True:
            sleep(60)
    finally:
        observer.stop()
        observer.join()
        main_logger.info("Stopped observer: %s", observer)


if __name__ == "__main__":
    raise SystemExit(main())
