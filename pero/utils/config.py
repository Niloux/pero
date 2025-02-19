import json
from pathlib import Path
from threading import Lock

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from pero.utils.logger import logger


class ConfigManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, config_path, config_type="yaml"):
        """创建单例实例并初始化配置加载"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ConfigManager, cls).__new__(cls)
                    cls._instance._init(config_path, config_type)
        return cls._instance

    def _init(self, config_path, config_type):
        """初始化配置管理器"""
        self.config_path = Path(config_path)
        self.config_type = config_type
        self._config = {}
        self._load_config()
        self._start_watcher()

    def _load_config(self):
        """加载配置文件（YAML或JSON）"""
        try:
            if self.config_type == "yaml":
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}
            elif self.config_type == "json":
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            else:
                raise ValueError(f"Unsupported config type: {self.config_type}")

            # 将配置项转换为类属性
            for key, value in self._config.items():
                setattr(self, key, value)

            logger.info(f"Loaded config from {self.config_path}")

        except FileNotFoundError:
            logger.error(f"Error: {self.config_path} not found.")
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing config: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while loading config: {e}")

    def _start_watcher(self):
        """启动文件变动监视器"""
        self._stop_watcher = False

        class ConfigChangeHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.src_path == str(self.config_path):
                    logger.info(f"Config file {self.config_path} modified, reloading...")
                    self._load_config()

        # 使用 watchdog 来监听文件变化
        self._observer = Observer()
        self._observer.schedule(ConfigChangeHandler(), str(self.config_path.parent), recursive=False)
        self._observer.start()

    def get(self, key, default=None):
        """获取配置项，支持字典方式访问"""
        with self._lock:
            return self._config.get(key, default)

    def stop_watcher(self):
        """停止文件监视"""
        self._stop_watcher = True
        self._observer.stop()
        self._observer.join()

    def __repr__(self):
        return f"ConfigManager(config={self._config})"


config_file = "config.yaml"
config_manager = ConfigManager(config_file, config_type="yaml")
