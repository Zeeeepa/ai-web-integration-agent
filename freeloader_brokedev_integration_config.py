"""
Configuration adapter for BrokeDev integration within the freeloader framework.
"""
import os
import yaml
from typing import Dict, Any, Optional

class BrokeDevConfig:
    """Manages configuration for BrokeDev components within freeloader."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the BrokeDev configuration manager.
        
        Args:
            config_path: Path to the BrokeDev config file. If None, uses default paths.
        """
        self.config_data = {}
        self.config_path = config_path or self._find_default_config()
        self.load_config()
    
    def _find_default_config(self) -> str:
        """Find the default configuration file."""
        # Check common locations
        paths = [
            os.path.join(os.path.expanduser("~"), ".freeloader", "brokedev", "config.yaml"),
            os.path.join(os.path.expanduser("~"), ".brokedev", "config.yaml"),
            "config.yaml"
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        # Return the first path as default, even if it doesn't exist yet
        return paths[0]
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config_data = yaml.safe_load(f)
            else:
                self._create_default_config()
            
            return self.config_data
        except Exception as e:
            print(f"Error loading BrokeDev configuration: {e}")
            self._create_default_config()
            return self.config_data
    
    def _create_default_config(self) -> None:
        """Create a default configuration file."""
        self.config_data = {
            "browser": {
                "user_data_dir": "~/.brokedev/browser_data",
                "screenshot_dir": "./screenshots",
                "headless": False,
                "debug_mode": False
            },
            "antibot": {
                "randomize_user_agent": True,
                "disable_webdriver": True,
                "mask_bot_patterns": True,
                "emulate_human_input": True,
                "webgl_noise": True,
                "canvas_noise": True
            },
            "proxy": {
                "enabled": False,
                "rotation_policy": "round-robin",
                "min_rotate_time": 600,
                "max_fail_count": 3,
                "proxy_file": "~/.brokedev/proxies.txt"
            },
            "tls": {
                "enabled": False,
                "cert_dir": "~/.brokedev/certs",
                "proxy_addr": "127.0.0.1:8443"
            },
            "security": {
                "encrypt_cookies": True,
                "encrypt_credentials": True,
                "key_dir": "~/.brokedev/keys"
            },
            "claude": {
                "url": "https://claude.ai/chat",
                "login_required": True
            },
            "copilot": {
                "url": "https://github.com/features/copilot",
                "login_required": True
            },
            "python_scripts_dir": "./python",
            "log_file": "./brokedev.log",
            "debug_mode": False
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Save the default config
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config_data, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save to file."""
        keys = key.split('.')
        config = self.config_data
        
        # Navigate to the correct nested dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save the config
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config_data, f, default_flow_style=False)