import os
import re
from typing import List, Dict
from curl_cffi import requests as curl_requests

class APIClient:
    def __init__(self, config: dict):
        self.config = config
        self.debug = config.get('debug', False)
        
        # Validate IDs
        self._validate_ids()
        
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

    def _validate_ids(self):
        """Validate organization and project IDs"""
        # Remove any whitespace from IDs
        self.config['organization_id'] = self.config['organization_id'].strip()
        self.config['project_id'] = self.config['project_id'].strip()
        
        # Basic UUID format validation
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        
        if not re.match(uuid_pattern, self.config['organization_id'].lower()):
            raise ValueError(f"Invalid organization ID format: {self.config['organization_id']}")
            
        if not re.match(uuid_pattern, self.config['project_id'].lower()):
            raise ValueError(f"Invalid project ID format: {self.config['project_id']}")

    def _log_request(self, method: str, url: str, data: dict = None):
        """Log request details if debug is enabled"""
        if self.debug:
            print(f"\nAPI Request: {method} {url}")
            if data:
                print(f"Request Data: {data}")

    def _handle_error(self, response, operation: str):
        """Handle API error responses"""
        if response.status_code == 400:
            raise ValueError(f"Bad request for {operation}. Please verify your organization ID and project ID are correct.")
        elif response.status_code == 403:
            print("\nAuthentication failed. Session key may have expired.")
            print("Please get a new session key by:")
            print("1. Opening Chrome")
            print("2. Going to claude.ai")
            print("3. Opening DevTools (F12)")
            print("4. Going to Network tab")
            print("5. Finding a request (like 'organizations')")
            print("6. Looking for the 'sessionKey' cookie value")
            raise Exception("Invalid or expired session key")
        elif response.status_code == 404:
            raise ValueError(f"Resource not found. Please verify your organization ID and project ID are correct.")
        else:
            response.raise_for_status()

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
        
        self._log_request('POST', url, data)
        
        response = curl_requests.post(
            url, 
            json=data,
            **self.request_params
        )
        
        self._handle_error(response, "file upload")
        return response.json()

    def delete_file(self, file_id: str) -> None:
        """Delete a file from Claude"""
        url = f"{self.config['base_url']}/api/organizations/{self.config['organization_id']}/projects/{self.config['project_id']}/docs/{file_id}"
        
        data = {
            "docUuid": file_id
        }
        
        self._log_request('DELETE', url, data)
        
        response = curl_requests.delete(
            url,
            json=data,
            **self.request_params
        )
        
        self._handle_error(response, "file deletion")

    def list_remote_files(self) -> List[dict]:
        """List remote files including metadata."""
        url = f"{self.config['base_url']}/api/organizations/{self.config['organization_id']}/projects/{self.config['project_id']}/docs"
        
        self._log_request('GET', url)
        
        response = curl_requests.get(
            url, 
            **self.request_params
        )
        
        self._handle_error(response, "listing files")
        return response.json()