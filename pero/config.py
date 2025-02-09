import yaml


class Config:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self._config_data = {}  # 存储完整配置
        self.load_config()

    def load_config(self):
        """加载 YAML 配置并自动转换为属性"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                self._config_data = yaml.safe_load(file) or {}

            # 自动将 YAML 中的键值作为对象属性
            for key, value in self._config_data.items():
                setattr(self, key, value)

        except FileNotFoundError:
            print(f"Error: {self.config_file} not found.")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def get(self, key, default=None):
        """支持使用字典风格获取配置值"""
        return self._config_data.get(key, default)

    def __repr__(self):
        return f"Config({self._config_data})"
