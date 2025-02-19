import json
import os
import time
from threading import Lock, Thread


class HotConfig:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(HotConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path):
        self.config_path = config_path
        self._config = {}
        self._load_config()
        self._start_watcher()

    def _load_config(self):
        with open(self.config_path, "r") as f:
            self._config = json.load(f)

    def _start_watcher(self):
        self._stop_watcher = False

        def watch():
            last_modified = os.path.getmtime(self.config_path)
            while not self._stop_watcher:
                time.sleep(1)
                current_modified = os.path.getmtime(self.config_path)
                if current_modified != last_modified:
                    with self._lock:
                        self._load_config()
                        last_modified = current_modified

        self._watcher_thread = Thread(target=watch)
        self._watcher_thread.start()

    def get(self, key, default=None):
        with self._lock:
            return self._config.get(key, default)

    def stop_watcher(self):
        self._stop_watcher = True
        self._watcher_thread.join()


hot_config = HotConfig("config.json")
