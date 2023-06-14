#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

__all__: list[str] = ["main"]

import argparse
import logging
import sys
from typing import Literal, Optional, Sequence, TextIO

from auto_file_sorter import __status__, __version__
from auto_file_sorter.args_handling import (
    handle_config_args,
    handle_track_args,
    resolved_path_from_str,
)
from auto_file_sorter.constants import (
    CONFIGURATION_LOG_LEVEL,
    LOG_FORMAT,
    LOG_LOCATION,
    MAX_VERBOSITY_LEVEL,
    MOVEMENT_LOG_LEVEL,
    STREAM_HANDLER_FORMATTER,
)

_verbose_output_levels: dict[int, int] = {
    1: logging.ERROR,
    2: logging.INFO,
    3: logging.DEBUG,
}


def main(argv: Optional[Sequence[str]] = None) -> Literal[0, 1]:
    """Runs the program."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="auto-file-sorter",
        description="Automatically sorts files in a directory based on their extension.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__} {__status__}",
        help="Show version of auto-file-sorter",
    )
    parser.add_argument(
        "-D",
        "--debug",
        action="store_true",
        dest="debugging",
        help="Enable debugging by setting logging level to DEBUG",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity (up to 3 levels; third requires debugging)",
    )

    subparsers: argparse._SubParsersAction[  # noqa: SLF001 # type: ignore
        argparse.ArgumentParser
    ] = parser.add_subparsers(
        title="subcommands",
        description="Track a directory or configure the extension paths",
        required=True,
    )

    # "track" subcommand
    track_parser: argparse.ArgumentParser = subparsers.add_parser(
        "track",
        help="Track a directory",
    )
    track_parser.set_defaults(handle=handle_track_args)
    track_parser.add_argument(
        type=resolved_path_from_str,
        dest="tracked_path",
        nargs="?",
        default=".",
        metavar="PATH",
        help="Path to the directory to be tracked (default: current directory)",
    )

    # "config" subcommand
    config_parser: argparse.ArgumentParser = subparsers.add_parser(
        "config",
        help="Configure the extension paths",
    )
    config_parser.set_defaults(
        handle=handle_config_args,
    )
    config_parser.add_argument(
        "-a",
        "--add",
        dest="new_config",
        type=str,
        nargs=2,
        help="Add path for extension",
    )
    config_parser.add_argument(
        "-d",
        "--delete",
        dest="configs_to_be_deleted",
        type=str,
        nargs="+",
        help="Delete extension(s) and its/their path from the configs",
    )

    args: argparse.Namespace = parser.parse_args(argv)

    # custom "MOVEMENT" and "CONFIGURATION" logging level >= logging.CRITICAL (50)
    # so it can be handeled by the stream handler if verbose logging is enabled
    logging.addLevelName(MOVEMENT_LOG_LEVEL, "MOVEMENT")
    logging.addLevelName(CONFIGURATION_LOG_LEVEL, "CONFIGURATION")

    file_handler: logging.FileHandler = logging.FileHandler(
        filename=LOG_LOCATION,
        mode="w",
        encoding="utf-8",
    )

    handlers: list[logging.Handler] = [file_handler]

    if 1 <= args.verbose <= MAX_VERBOSITY_LEVEL:
        stream_handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
        stream_handler.setLevel(_verbose_output_levels[args.verbose])
        stream_handler.setFormatter(STREAM_HANDLER_FORMATTER)
        handlers.append(stream_handler)
    elif args.verbose > MAX_VERBOSITY_LEVEL:
        print(
            "Maximum verbosity level exceeded. Using maximum level of 3.",
            file=sys.stderr,
        )
        stream_handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
        stream_handler.setLevel(MAX_VERBOSITY_LEVEL)
        stream_handler.setFormatter(STREAM_HANDLER_FORMATTER)
        handlers.append(stream_handler)

    log_level: int = logging.INFO if not args.debugging else logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=handlers,
    )

    main_logger: logging.Logger = logging.getLogger(main.__name__)
    main_logger.info("Started logging with level %s", log_level)
    main_logger.debug("args=%s", repr(args))

    exit_code: Literal[0, 1] = args.handle(args)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
