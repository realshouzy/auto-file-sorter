#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING, Optional, Sequence

from watchdog.observers import Observer

from .event_handler import FileModifiedEventHandler
from .json_handler import open_json

if TYPE_CHECKING:
    from watchdog.observers.api import BaseObserver


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Runs the program."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--path",
        "--tracked-path",
        type=Path,
        help="path to be tracked",
        required=True,
    )
    parser.add_argument(
        "-e",
        "--extensions",
        "--extension-paths",
        type=Path,
        help="path to extensions.json file",
        required=True,
    )
    # TODO: Make logging optional for the user
    # parser.add_argument(
    #     "-l",
    #     "--log",
    #     "--logging",
    #     action="store_true",
    #     help="enable logging",
    # )
    # parser.add_argument(
    #     "-nl",
    #     "--no-log",
    #     "--no-logging",
    #     action="store_false",
    #     help="disable logging",
    #     dest="logging",
    # )
    parser.add_argument(
        "-lf",
        "--log-format",
        "--logging-format",
        default=r"%(name)s %(levelname)s %(asctime)s - %(message)s",
        type=str,
        help="logging format",
    )
    parser.add_argument(
        "-ll",
        "--log-level",
        "--logging-level",
        default=20,
        type=int,
        help="logging level",
    )
    parser.add_argument(
        "-d",
        "--debug",
        "--debugging",
        action="store_const",
        const=10,
        dest="log_level",
        help="set logging level to debugging (10)",
    )
    # TODO: Add ``auto`` sub command for adding the automation to the startups folder
    args: argparse.Namespace = parser.parse_args(argv)

    logging.basicConfig(
        filename="auto-file-sorter.log",
        level=args.log_level,
        format=args.log_format,
        filemode="w",
    )
    main_logger: logging.Logger = logging.getLogger(main.__name__)
    main_logger.info("Started automation")

    main_logger.info("Getting extension paths from %s", args.extensions)
    with open_json(args.extensions) as json_file:
        extension_paths: dict[str, str] = json_file

    event_handler: FileModifiedEventHandler = FileModifiedEventHandler(
        args.path,
        extension_paths,
    )

    main_logger.debug("Creating observer")
    observer: BaseObserver = Observer()
    main_logger.debug("Scheduling observer: %s", observer)
    observer.schedule(event_handler, args.path, recursive=True)
    main_logger.debug("Starting observer: %s", observer)
    observer.start()
    main_logger.info("Started observer: %s", observer)

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        main_logger.debug("User stopped/interrupted program")
        return 0
    finally:
        if observer.is_alive():
            observer.stop()
            main_logger.info("Stopped observer: %s", observer)
        observer.join()
        main_logger.debug("Joined observer: %s", observer)


if __name__ == "__main__":
    raise SystemExit(main())
