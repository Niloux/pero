import yaml


class Config:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.ws_uri = None
        self.hp_uri = None
        self.bot_uid = None
        self.token = None

        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                config_data = yaml.safe_load(file)

            self.ws_uri = config_data.get("ws_uri", None)
            self.hp_uri = config_data.get("hp_uri", None)
            self.bot_uid = config_data.get("bot_uid", None)
            self.token = config_data.get("token", None)

        except FileNotFoundError:
            print(f"Error: {self.config_file} not found.")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def __repr__(self):
        return f"Config(ws_uri={self.ws_uri}, hp_uri={self.hp_uri}, bot_uid={self.bot_uid}, token={self.token})"
