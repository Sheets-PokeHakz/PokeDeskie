import os
import json
from typing import Dict, Any, List


class Config:
    def __init__(self, config_file: str = "Config.json"):
        self.config_file = config_file
        self._config_data = {}
        self.load_config()

    def load_config(self) -> None:
        try:
            with open(self.config_file, "r") as file:
                self._config_data = json.load(file)
        except FileNotFoundError:
            print(
                f"Config file {self.config_file} not found. Using default configuration."
            )
            self._config_data = self._get_default_config()
        except json.JSONDecodeError:
            print(f"Invalid JSON in {self.config_file}. Using default configuration.")
            self._config_data = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "trade_log": [],
            "rand_channels": [],
            "trade_channels": [],
            "WEBHOOK_URL": "",
        }

    def save_config(self) -> None:
        with open(self.config_file, "w") as file:
            json.dump(self._config_data, file, indent=4)

    @property
    def trade_log(self) -> List[int]:
        return self._config_data.get("trade_log", [])

    @property
    def rand_channels(self) -> List[int]:
        return self._config_data.get("rand_channels", [])

    @property
    def trade_channels(self) -> List[int]:
        return self._config_data.get("trade_channels", [])

    @property
    def admin_uids(self) -> List[int]:
        return self._config_data.get("admin_uids", [])

    @property
    def webhook_url(self) -> str:
        return self._config_data.get("WEBHOOK_URL", "")

    @property
    def bot_token(self) -> str:
        return os.getenv("BOT_TOKEN", "")

    @property
    def admin_user_id(self) -> int:
        return 988118054456152084


config = Config()
