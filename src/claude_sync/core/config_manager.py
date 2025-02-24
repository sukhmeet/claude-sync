import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class ConfigManager:
    def __init__(self, config_path: str = ".sync_config.json"):
        self.config_path = config_path
        self.global_config_path = os.path.expanduser("~/.claude-sync.config")
        self.config = self._load_config()

    def _load_global_session(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Load session key and default org ID from global config if valid
        Returns (session_key, default_org_id)
        """
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
                        return (
                            session_info.get('session_key'),
                            session_info.get('default_organization_id')
                        )
            except Exception as e:
                print(f"Warning: Error reading global config: {e}")
        return None, None

    def _ensure_global_config(self) -> Tuple[str, str]:
        """
        Ensure global config exists with session key and default org ID.
        Returns (session_key, default_org_id)
        """
        session_key, default_org_id = self._load_global_session()
        
        # If no global config exists or it's expired, create it
        if not session_key or not default_org_id:
            print("\nSetting up global Claude configuration...")
            
            # Get session key if needed
            if not session_key:
                session_key = input("Please enter your Claude session key: ").strip()
            
            # Always get default org ID if it doesn't exist
            if not default_org_id:
                print("\nPlease enter your default organization ID.")
                print("This will be saved globally and suggested as default for all projects.")
                default_org_id = input("Default organization ID: ").strip()
            
            # Save to global config
            self._save_global_config(session_key, default_org_id)
            print("\nGlobal configuration saved successfully.")
        
        return session_key, default_org_id

    def _save_global_config(self, session_key: str, org_id: str):
        """Save session key and default org ID to global config"""
        try:
            # Load existing config or create new
            if os.path.exists(self.global_config_path):
                with open(self.global_config_path, 'r') as f:
                    global_config = json.load(f)
            else:
                global_config = {}

            # Update Claude AI section
            claude_config = {
                'session_key': session_key,
                'default_organization_id': org_id,
                'expiration': (datetime.now().replace(microsecond=0) + 
                             timedelta(days=7)).isoformat(),
                'updated_at': datetime.now().replace(microsecond=0).isoformat()
            }

            global_config["https://claude.ai"] = claude_config

            # Save updated config
            with open(self.global_config_path, 'w') as f:
                json.dump(global_config, f, indent=2)

        except Exception as e:
            print(f"Warning: Error saving global config: {e}")

    def _load_config(self) -> Dict:
        """Load or create project-specific config"""
        # First ensure we have valid global config
        session_key, default_org_id = self._ensure_global_config()
        
        # Now handle project-specific config
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        else:
            config = self._create_initial_config(session_key, default_org_id)
        
        # Update session key if needed
        if 'session_key' not in config or config['session_key'] != session_key:
            config['session_key'] = session_key
            self._save_config(config)
            
        return config

    def _create_initial_config(self, session_key: str, default_org_id: str) -> Dict:
        """Create initial project config file"""
        print("\nNo project config file found. Creating new configuration...")
        
        config = {
            'session_key': session_key,
            'base_url': input("Base URL (default: https://claude.ai): ").strip() or "https://claude.ai",
        }
        
        # Handle organization ID
        print(f"\nDefault organization ID: {default_org_id}")
        use_default = input("Use this organization ID for this project? [Y/n]: ").lower().strip()
        if use_default != 'n':
            config['organization_id'] = default_org_id
        else:
            print("Please enter the organization ID for this project:")
            config['organization_id'] = input("Organization ID: ").strip()
        
        # Add project ID
        config['project_id'] = input("Project ID: ").strip()
        
        self._save_config(config)
        print(f"\nProject config file created at {self.config_path}")
        return config

    def _save_config(self, config: Dict):
        """Save project config to file"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)