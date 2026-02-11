import yaml
from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv

class Config:
    """
    Configuration manager
    """
    def __init__(self, config_path: str = 'config/config.yaml'):
        self.config_path = Path(config_path)
        self._config = None
        self.load()
        
        # Load environment variables
        load_dotenv()
    
    def load(self):
        """Load configuration from YAML"""
        with open(self.config_path, 'r') as f:
            self._config = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: config.get('ml_models.random_forest.n_estimators')
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def get_api_key(self, service: str) -> str:
        """Get API key from environment"""
        key_map = {
            'alpha_vantage': 'ALPHA_VANTAGE_KEY',
            'fred': 'FRED_KEY'
        }
        return os.getenv(key_map.get(service, ''))
    
    @property
    def all(self) -> Dict:
        """Return all configuration"""
        return self._config

# Global config instance
config = Config()