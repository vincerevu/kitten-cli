import os
import tomlkit
from kitten_cli.config.settings import AppConfig

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.kitten/config.toml")
LOCAL_CONFIG_PATH = "./config.toml"

class ConfigManager:
    """Manages loading and saving the application configuration from TOML files."""

    @staticmethod
    def get_config_path() -> str:
        # Prefer local config over global config
        if os.path.exists(LOCAL_CONFIG_PATH):
            return LOCAL_CONFIG_PATH
        return DEFAULT_CONFIG_PATH

    @staticmethod
    def load_config() -> AppConfig:
        config_path = ConfigManager.get_config_path()
        if not os.path.exists(config_path):
            return AppConfig() # Return defaults if no config exists
            
        with open(config_path, "r", encoding="utf-8") as f:
            try:
                data = tomlkit.load(f)
                return AppConfig(**data)
            except Exception as e:
                print(f"Failed to load config from {config_path}: {e}")
                return AppConfig()

    @staticmethod
    def save_config(config: AppConfig, path: str = None) -> None:
        save_path = path or ConfigManager.get_config_path()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        
        # Read existing toml to preserve comments, or create new
        if os.path.exists(save_path):
            with open(save_path, "r", encoding="utf-8") as f:
                doc = tomlkit.load(f)
        else:
            doc = tomlkit.document()
            
        # Update doc with new config values
        config_dict = config.model_dump(exclude_none=True)
        
        for section, values in config_dict.items():
            if section not in doc:
                doc[section] = tomlkit.table()
            
            if isinstance(values, dict):
                for key, value in values.items():
                    doc[section][key] = value
            else:
                doc[section] = values
                
        with open(save_path, "w", encoding="utf-8") as f:
            tomlkit.dump(doc, f)
