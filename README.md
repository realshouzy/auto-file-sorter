# auto-file-sorter

[![Code Size](https://img.shields.io/github/languages/code-size/realshouzy/file-sorter)](https://github.com/realshouzy/file-sorter)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/realshouzy/auto-file-sorter/blob/main/LICENSE)

This is a python automation that watches a folder and sorts the files into their respective folders.

## Installation

Make sure you have python (^3.11).
You can install it via ``pip``:

```bash
pip install git+https://github.com/realshouzy/auto-file-sorter.git
```

Or clone the repo and then install all the required libraries by typing the following command in the root of the project:

```bash
git clone https://github.com/realshouzy/auto-file-sorter.git
pip install -r requierments.txt
```

The used packages are:

```python
# standard library
import argparse
import concurrent.futures
import contextlib
import datetime
import json
import logging
import os
import pathlib
import shutil
import typing

# third party
import watchdog
```

### macOS Setup

Add the following command to the ``Automator`` app. You can find a tutorial [here](https://youtu.be/LfxZMofHs_U?t=658).

If installed via ``pip``:

```bash
python3 -m auto-file-sorter
```

Else:

```bash
python3 -m path.to.the.src.auto-file-sorter
```

In case both do not work:

```bash
python3 /path/to/the/src/__main__.py
```

and add any needed extensions and configurations to the [settings.json](/src/auto-file-sorter/settings.json) file. Finally restart your computer.

### Windows Setup

Create a ``.bat`` file in ``C:\Users\{user here}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`` with the following content:

If installed via ``pip``:

```bash
start /b python -m auto-file-sorter
```

Else:

```bash
start /b python -m path.to.the.src.auto-file-sorter
```

In case both do not work:

```bash
start /b python C:\path\to\src\__main__.py
```

and add any needed extensions and configurations to the [settings.json](/src/auto-file-sorter/settings.json) file. Finally restart your computer.

Perhabs I'll add an executable in the future.

## Usage

Throw stuff into the tracked folder and it will be automatically sorted for you.

You can add to optional flags to the startup:

``--settings``/``-s`` to add the path to the specific [settings.json](/src/auto-file-sorter/settings.json) file

```bash
python -m auto-file-sorter --settings "C:\path\to\the\settings.json"
python -m auto-file-sorter -s "C:\path\to\the\settings.json"
```

If not given, the programm will first search its directory and subdirectory for said file and if not found will throw an error.

And ``--log``/``-l`` to add the path to an already existing ``log.log`` file.

```bash
python -m auto-file-sorter --log "C:\path\to\log.log"
python -m auto-file-sorter -l "C:\path\to\log.log"
```

If not given, the programm will first search its directory and subdirectory for said file and if not found create a new file in its directory.
