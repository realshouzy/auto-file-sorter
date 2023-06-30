# auto-file-sorter

[![Code Size](https://img.shields.io/github/languages/code-size/realshouzy/file-sorter)](https://github.com/realshouzy/file-sorter)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
![GitHub top language](https://img.shields.io/github/languages/top/realshouzy/auto-file-sorter)
![Contributors](https://img.shields.io/github/contributors/realshouzy/auto-file-sorter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/realshouzy/auto-file-sorter/blob/main/LICENSE)

**``auto-file-sorter`` is a Python automation tool that tracks a directory and sorts files into their respective folders based on their file extensions.**

## Installation

Make sure you have Python 3.10 or later installed. You can install the package using ``pip``:

```bash
pip install git+https://github.com/realshouzy/auto-file-sorter.git
```

Alternatively, you can clone the repository and install the required dependencies by executing the following commands in the root of the project:

```bash
git clone https://github.com/realshouzy/auto-file-sorter.git
pip install -r requierments.txt
```

The project uses the following packages and libraries:

```python
# standard library
import argparse
import concurrent.futures
import datetime
import json
import logging
import os
import pathlib
import platform
import re
import shutil
import signal
import sys
import time
import typing

# third party
import watchdog.events
import watchdog.observers

# only for type annotations; not used at runtime
import watchdog.observers.api
```

## Documentation

Consult ``auto-file-sorter --help`` / ``auto-file-sorter -h`` for the full set of options. This also applies to all subcommands:

- ``auto-file-sorter track``
- ``auto-file-sorter read``
- ``auto-file-sorter write``
- ``auto-file-sorter locations``

### Arguments and flags of ``auto-file-sorter``

- ``--version`` / ``-V``: utputs the installed version and status, either ``production`` or ``development``.
- ``--debug`` / ``-d``: Sets the logging level to 10 (debugging), enabling more informative debugging logs.
- ``--verbose`` / ``-v``: Enables verbose outputs. It can be used up to three levels, with each level printing more logs to the stream. The first level prints all logs up to the logging level WARNING, the second level prints all logs up to INFO, and the third level prints all logs up to DEBUG (this requires the debugging flag).
- ``--log-location``: Specifies the path to a log file. By default, the log file will be located with the source code.

### Arguments and flags of ``auto-file-sorter track``

- Positional arguments: Paths to the directories to be tracked. At least one directory path must be provided. The tool will track all the given directories simultaneously using threading.
- ``--autostart``(only supported on Windows): Runs the command on startup. Refer to [Windows setup](#windows-setup) for more information.

### Arguments of ``auto-file-sorter read``

- Positional arguments: Extensions for which their respective paths should be read from the configs.json file. If no extensions are given, it will print out the entire ``configs.json`` file.

### Arguments of ``auto-file-sorter write``

- ``--add`` / ``-a``: Adds an extension and its corresponding path to the ``configs.json`` file. It takes two arguments: the extension and the path to which files with this extension will be saved. If the extension already exists, the path will be overridden.
- ``--remove`` / ``-r``: Removes one or more extensions and their respective paths from the configuration.
- ``--json`` / ``-j``: Loads one or more ``json`` files that bind extensions to paths and merges them into the ``configs.json`` file.

### Flags of ``auto-file-sorter locations``

- ``--get-log-location`` / ``-l``: Prints the location of the log file.
- ``--get-config-location`` / ``-c``: Prints the location of the config file.

## Run on startup

### Windows setup

To run the tool on startup, add the ``--autostart`` flag after the ``track`` subcommand. This will add the command to the Startup folder as a ``.vbs`` file, ensuring it runs in the background. It removes all occurrences of ``--verbose``, any number of ``-v``, and ``--autostart`` to avoid the overhead of creating a StreamHandler and prevent overwriting the ``.vbs`` file on every startup. For example, ``auto-file-sorter -d -vvv track C:\path\to\be\tracked`` will be transformed into ``C:\path\to\auto-file-sorter.exe -d track C:\path\to\be\tracked``, which will be executed by the ``.vbs`` file.

### macOS setup

Add the desired command to the ``Automator`` app. You can find a tutorial [here](https://youtu.be/LfxZMofHs_U?t=658).

### Linux setup

Due to the wide variety of Linux distributions and their differences, it is up to the user to configure ``auto-file-sorter`` to run on startup.

## Usage

Simply place files into the tracked folder, and the tool will automatically sort them for you.

## Contributing

Contributions are welcome! Please create an issue for any suggestions or bug reports.

## TODO

Check the [TODO](/TODO.md) file for pending tasks and future improvements.
