import os
from typing import List, Dict
from curl_cffi import requests as curl_requests

class APIClient:
    def __init__(self, config: dict):
        self.config = config
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://claude.ai/chats',
            'Content-Type': 'application/json',
            'Origin': 'https://claude.ai',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Cookie': f'sessionKey={config["session_key"]}',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers'
        }
        # Common request parameters
        self.request_params = {
            'headers': self.headers,
            'impersonate': "chrome110",
            'verify': False  # Disable SSL verification
        }

    def upload_file(self, filepath: str, local_path: str = None) -> dict:
        """Upload a file to Claude"""
        url = f"{self.config['base_url']}/api/organizations/{self.config['organization_id']}/projects/{self.config['project_id']}/docs"
        
        with open(filepath, 'r') as f:
            content = f.read()
            
        data = {
            "file_name": filepath,  # Use full filepath to preserve structure
            "content": content,
            "project_uuid": self.config['project_id']
        }
        
        response = curl_requests.post(
            url, 
            json=data,
            **self.request_params
        )
        response.raise_for_status()
        return response.json()

    def delete_file(self, file_id: str) -> None:
        """Delete a file from Claude"""
        url = f"{self.config['base_url']}/api/organizations/{self.config['organization_id']}/projects/{self.config['project_id']}/docs/{file_id}"
        
        data = {
            "docUuid": file_id
        }
        
        response = curl_requests.delete(
            url,
            json=data,
            **self.request_params
        )
        response.raise_for_status()

    def list_remote_files(self) -> List[dict]:
        """List remote files including metadata."""
        url = f"{self.config['base_url']}/api/organizations/{self.config['organization_id']}/projects/{self.config['project_id']}/docs"
        
        response = curl_requests.get(
            url, 
            **self.request_params
        )
        
        if response.status_code == 403:
            print("\nAuthentication failed. Session key may have expired.")
            print("Please get a new session key by:")
            print("1. Opening Chrome")
            print("2. Going to claude.ai")
            print("3. Opening DevTools (F12)")
            print("4. Going to Network tab")
            print("5. Finding a request (like 'organizations')")
            print("6. Looking for the 'sessionKey' cookie value")
            raise Exception("Invalid or expired session key")
            
        response.raise_for_status()
        return response.json()