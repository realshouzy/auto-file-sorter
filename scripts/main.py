#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
from __future__ import annotations
from pathlib import Path

from time import sleep
import json
from watchdog.observers import Observer

from event_handler import EventHandler

def main() -> None:
    watch_path = Path('C:/Users/yanni/Downloads/downloaded')
    destination_root = Path('C:/Users/yanni/Downloads')
    event_handler = EventHandler(watch_path=watch_path, destination_root=destination_root)

    observer = Observer()
    observer.schedule(event_handler, f'{watch_path}', recursive=True)
    observer.start()

    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()