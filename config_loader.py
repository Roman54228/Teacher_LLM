"""
Configuration loader for Interview Prep app
Supports both YAML config and environment variables
"""
import yaml
import os
from typing import Dict, Any

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_data = {}
        self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """Load configuration from YAML file with environment variable override"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f) or {}
                print(f"✓ Конфигурация загружена из {config_path}")
            else:
                print(f"⚠ Файл {config_path} не найден, используются переменные окружения")
                self.config_data = {}
        except Exception as e:
            print(f"✗ Ошибка загрузки конфигурации: {e}")
            self.config_data = {}
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path
        Examples: 'database.url', 'telegram.bot_token'
        """
        # Try environment variable first (converted to uppercase with underscores)
        env_key = key_path.upper().replace('.', '_')
        env_value = os.environ.get(env_key)
        if env_value:
            return env_value
        
        # Try YAML config
        keys = key_path.split('.')
        value = self.config_data
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_database_url(self) -> str:
        """Get database URL, using SQLite for stability"""
        # Force SQLite for local development stability
        sqlite_path = self.get('sqlite.database_path', 'interview_prep.db')
        print(f"✓ Используется SQLite база данных: {sqlite_path}")
        return f"sqlite:///{sqlite_path}"

# Global config instance
config = Config()

def load_config():
    """Load configuration from config.yaml - FastAPI compatibility"""
    return config.config_data