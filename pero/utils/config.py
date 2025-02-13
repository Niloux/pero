from pathlib import Path

import yaml

from pero.utils.logger import logger


class Config:
    def __init__(self, config_file: str):
        """
        初始化 Config 类，加载配置文件并将其转换为属性。

        :param config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self._config_data = {}  # 存储完整配置
        self._load_config()

    def _load_config(self):
        """加载 YAML 配置并自动转换为属性"""
        try:
            with self.config_file.open("r", encoding="utf-8") as file:
                self._config_data = yaml.safe_load(file) or {}

            # 自动将 YAML 中的键值作为对象属性
            for key, value in self._config_data.items():
                setattr(self, key, value)

            logger.info(f"Loaded config from {self.config_file}")

        except FileNotFoundError:
            logger.error(f"Error: {self.config_file} not found.")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    def get(self, key: str, default=None):
        """
        使用字典风格获取配置值。

        :param key: 配置项的键
        :param default: 如果键不存在，返回的默认值
        :return: 配置项的值
        """
        return self._config_data.get(key, default)

    def __getattr__(self, item):
        """
        允许通过属性访问配置项。

        :param item: 配置项的键
        :return: 配置项的值
        """
        return self._config_data.get(item)

    def __repr__(self):
        return f"Config({self._config_data})"


current_dir = Path(__file__).parent
config_dir = current_dir.parent.parent
config = Config(config_dir / "config.yaml")
