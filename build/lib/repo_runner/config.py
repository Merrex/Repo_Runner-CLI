"""
Configuration management for repo_runner.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .logger import get_logger


class Config:
    """Configuration manager for repo_runner."""
    
    def __init__(self, config_data: Dict[str, Any] = None):
        self.data = config_data or {}
        self.logger = get_logger()
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """Load configuration from file."""
        if config_path:
            config_file = Path(config_path)
        else:
            # Look for config files in order of preference
            config_files = [
                '.runnerconfig.yaml',
                '.runnerconfig.yml',
                '.repo_runner.yaml',
                '.repo_runner.yml',
                'repo_runner.yaml',
                'repo_runner.yml'
            ]
            
            config_file = None
            for filename in config_files:
                if Path(filename).exists():
                    config_file = Path(filename)
                    break
        
        if config_file and config_file.exists():
            return cls._load_from_file(config_file)
        else:
            return cls()
    
    @classmethod
    def _load_from_file(cls, config_file: Path) -> 'Config':
        """Load configuration from a YAML file."""
        logger = get_logger()
        
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
            
            logger.info(f"Loaded configuration from {config_file}")
            return cls(config_data)
        
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_file}: {e}")
            return cls()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self.data[key] = value
    
    def get_nested(self, path: str, default: Any = None) -> Any:
        """Get a nested configuration value using dot notation."""
        keys = path.split('.')
        value = self.data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def merge(self, other_config: Dict[str, Any]):
        """Merge another configuration into this one."""
        self._deep_merge(self.data, other_config)
    
    def _deep_merge(self, target: Dict, source: Dict):
        """Deep merge two dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def save(self, config_path: str):
        """Save configuration to file."""
        config_file = Path(config_path)
        
        try:
            with open(config_file, 'w') as f:
                yaml.safe_dump(self.data, f, default_flow_style=False)
            
            self.logger.info(f"Configuration saved to {config_file}")
        
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {config_file}: {e}")
    
    def create_default_config(self, config_path: str = '.runnerconfig.yaml'):
        """Create a default configuration file."""
        default_config = {
            'project': {
                'name': 'my-project',
                'type': 'auto-detect',
                'version': '1.0.0'
            },
            'environment': {
                'development': {
                    'host': 'localhost',
                    'port': 3000,
                    'debug': True
                },
                'production': {
                    'host': '0.0.0.0',
                    'port': 8000,
                    'debug': False
                }
            },
            'database': {
                'auto_migrate': True,
                'seed_data': True
            },
            'docker': {
                'enabled': True,
                'detached': False,
                'build_args': {}
            },
            'hooks': {
                'pre_install': [],
                'post_install': [],
                'pre_run': [],
                'post_run': [],
                'pre_health': [],
                'post_health': []
            },
            'health_check': {
                'enabled': True,
                'timeout': 60,
                'retry_count': 3
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
        
        config_file = Path(config_path)
        if not config_file.exists():
            with open(config_file, 'w') as f:
                yaml.safe_dump(default_config, f, default_flow_style=False)
            
            self.logger.info(f"Created default configuration: {config_file}")
        else:
            self.logger.info(f"Configuration file already exists: {config_file}")
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self.data[key]
    
    def __setitem__(self, key: str, value: Any):
        """Allow dictionary-style assignment."""
        self.data[key] = value
    
    def __contains__(self, key: str) -> bool:
        """Allow 'in' operator."""
        return key in self.data
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Config({self.data})"