import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

class ConfigManager:
    def __init__(self, config_path: str = ".sync_config.json"):
        self.config_path = config_path
        self.global_config_path = os.path.expanduser("~/.claude-sync.config")
        self.config = self._load_config()

    def _load_global_session(self) -> Optional[str]:
        """Load session key from global config if valid"""
        if os.path.exists(self.global_config_path):
            try:
                with open(self.global_config_path, 'r') as f:
                    global_config = json.load(f)
                
                # Get session info for Claude AI
                session_info = global_config.get("https://claude.ai", {})
                if session_info:
                    # Check expiration
                    expiration = datetime.fromisoformat(session_info.get('expiration', '2000-01-01'))
                    if datetime.now() < expiration:
                        return session_info.get('session_key')
            except Exception as e:
                print(f"Warning: Error reading global config: {e}")
        return None

    def _load_config(self) -> Dict:
        """Load or create config with session key"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        else:
            config = self._create_initial_config()
        
        # Try to get session key from global config
        if 'session_key' not in config:
            global_session = self._load_global_session()
            if global_session:
                config['session_key'] = global_session
                self._save_config(config)
            else:
                config['session_key'] = input("Session Key: ").strip()
                self._save_config(config)
            
        return config

    def _save_config(self, config: Dict):
        """Save config to file"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def _create_initial_config(self) -> Dict:
        """Create initial config file"""
        print("No config file found. Please provide the following information:")
        
        config = {
            'organization_id': input("Organization ID: ").strip(),
            'project_id': input("Project ID: ").strip(),
            'base_url': input("Base URL (default: https://claude.ai): ").strip() or "https://claude.ai",
        }
        
        # Try to get session key from global config
        global_session = self._load_global_session()
        if global_session:
            config['session_key'] = global_session
        else:
            config['session_key'] = input("Session Key: ").strip()
        
        self._save_config(config)
        print(f"Config file created at {self.config_path}")
        return config