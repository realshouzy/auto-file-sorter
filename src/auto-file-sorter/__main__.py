#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

import argparse
import logging
from time import sleep
from typing import TYPE_CHECKING, Optional, Sequence

from watchdog.observers import Observer

from .utils.event_handler import FileModifiedEventHandler
from .utils.helper_funcs import get_file_path
from .utils.settings_handler import open_settings

if TYPE_CHECKING:
    from watchdog.observers.api import BaseObserver


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
    args: argparse.Namespace = parser.parse_args(argv)

    with open_settings(args.settings) as settings:
        tracked_path: str = str(settings["general"]["trackedPath"])
        extension_paths: dict[str, str] = dict(settings["extensions"])  # type: ignore
        logging_level: int = int(settings["general"]["loggingLevel"])
        log_format: str = str(settings["general"]["loggingFormat"])

    logging.basicConfig(
        filename=args.log,
        level=logging_level,
        format=log_format,
        filemode="w",
    )
    main_logger: logging.Logger = logging.getLogger(main.__name__)
    event_handler: FileModifiedEventHandler = FileModifiedEventHandler(
        tracked_path,
        extension_paths,
    )

    observer: BaseObserver = Observer()
    observer.schedule(event_handler, tracked_path, recursive=True)
    observer.start()
    main_logger.info("Started observer: %s", observer)

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        return 0
    finally:
        if observer.is_alive():
            observer.stop()
            main_logger.info("Stopped observer: %s", observer)
        observer.join()
        main_logger.debug("Joined observer: %s", observer)


if __name__ == "__main__":
    raise SystemExit(main())
