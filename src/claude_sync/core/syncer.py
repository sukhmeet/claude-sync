import os
from typing import Dict, Set, Tuple
from datetime import datetime
from claude_sync.api.client import APIClient
from claude_sync.core.config_manager import ConfigManager
from claude_sync.utils.ignore_parser import GitignoreParser

class FileSyncer:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.config_manager = ConfigManager()
        self.ignore_parser = GitignoreParser()
        self.config = self.config_manager._load_config()
        self.api_client = APIClient(self.config)

    def get_local_files(self) -> Dict[str, float]:
        """Get local files with their modification timestamps"""
        files = {}
        
        if self.debug:
            print("\nDebug: Scanning local files...")
            
        for root, _, filenames in os.walk('.'):
            for filename in filenames:
                filepath = os.path.relpath(os.path.join(root, filename))
                if not self.ignore_parser.should_ignore(filepath):
                    mtime = os.path.getmtime(filepath)
                    files[filepath] = mtime
                    if self.debug:
                        print(f"  {filepath}: {datetime.fromtimestamp(mtime)}")
                        
        return files

    def get_sync_status(self) -> Tuple[Dict[str, dict], Dict[str, dict]]:
        """Get sync status comparing local and remote state"""
        local_files = self.get_local_files()
        remote_files = self.api_client.list_remote_files()

        if self.debug:
            print("\nDebug: Remote files response:")
            print(remote_files)
            
        # Index remote files by their name/path
        remote_state = {}
        for file in remote_files:
            # Try to get local path from metadata, fallback to filename
            local_path = file.get('metadata', {}).get('local_path', file['file_name'])
            remote_state[local_path] = {
                'id': file['uuid'],  # API returns 'uuid' instead of 'id'
                'updated_at': file.get('updated_at', file.get('created_at')),
                'content_hash': file.get('content_hash')
            }

        # Track files to sync and remote files to delete
        sync_status = {}
        delete_status = {}

        # Check local files that need syncing
        for filepath, local_mtime in local_files.items():
            remote_info = remote_state.get(filepath)
            
            if not remote_info:
                # File doesn't exist remotely
                sync_status[filepath] = {
                    'needs_sync': True,
                    'last_sync': 'Never',
                    'action': 'upload'
                }
            else:
                # Convert remote time to UTC
                remote_time = datetime.fromisoformat(remote_info['updated_at'].replace('Z', '+00:00'))
                # Convert local time to UTC aware datetime
                local_time = datetime.fromtimestamp(local_mtime).astimezone()
                
                # Compare using timestamps to avoid timezone issues
                if local_time.timestamp() > remote_time.timestamp():
                    sync_status[filepath] = {
                        'needs_sync': True,
                        'last_sync': remote_info['updated_at'],
                        'action': 'replace',
                        'remote_id': remote_info['id']  # This is the UUID from our earlier mapping
                    }
                else:
                    sync_status[filepath] = {
                        'needs_sync': False,
                        'last_sync': remote_info['updated_at'],
                        'action': None
                    }

        # Check remote files that need deletion
        for remote_file in remote_files:
            local_path = remote_file.get('metadata', {}).get('local_path', remote_file['file_name'])
            if local_path not in local_files:
                delete_status[local_path] = {
                    'id': remote_file['uuid'],  # API returns 'uuid' instead of 'id'
                    'last_updated': remote_file.get('updated_at', remote_file.get('created_at'))
                }

        return sync_status, delete_status

    def sync_files(self, dry_run: bool = False):
        """Sync files that need updating and clean up orphaned remote files"""
        sync_status, delete_status = self.get_sync_status()
        files_to_sync = {f: s for f, s in sync_status.items() if s['needs_sync']}
        
        # Track operation counts for summary
        summary = {
            'uploaded': 0,
            'replaced': 0,
            'deleted': 0,
            'failed': 0,
            'skipped': len(sync_status) - len(files_to_sync),
            'errors': []
        }
        
        if dry_run:
            print(f"\nWould perform the following operations:")
            
            if files_to_sync:
                print("\nFiles to sync:")
                for filepath, info in files_to_sync.items():
                    action = "Upload new file" if info['action'] == 'upload' else "Replace existing file"
                    print(f"  {filepath} - {action}")
            
            if delete_status:
                print("\nRemote files to delete:")
                for filepath in delete_status:
                    print(f"  {filepath}")
                    
            return
        
        # First, handle file uploads and replacements
        for filepath, info in files_to_sync.items():
            try:
                print(f"\nSyncing {filepath}...")
                
                # If replacing, delete old file first
                if info['action'] == 'replace':
                    print(f"  Deleting old remote version...")
                    self.api_client.delete_file(info['remote_id'])
                
                # Upload new version
                print(f"  Uploading new version...")
                self.api_client.upload_file(filepath, local_path=filepath)
                print(f"Successfully synced {filepath}")
                
                # Update summary
                if info['action'] == 'upload':
                    summary['uploaded'] += 1
                else:
                    summary['replaced'] += 1
                    
            except Exception as e:
                error_msg = f"Error syncing {filepath}: {str(e)}"
                print(error_msg)
                summary['failed'] += 1
                summary['errors'].append(error_msg)

        # Then, clean up orphaned remote files
        if delete_status:
            print("\nCleaning up remote files...")
            for filepath, info in delete_status.items():
                try:
                    print(f"  Deleting {filepath}...")
                    self.api_client.delete_file(info['id'])
                    summary['deleted'] += 1
                except Exception as e:
                    error_msg = f"Error deleting {filepath}: {str(e)}"
                    print(error_msg)
                    summary['failed'] += 1
                    summary['errors'].append(error_msg)

        # Print summary
        print("\nSync Summary:")
        print(f"  {summary['uploaded']} files uploaded")
        print(f"  {summary['replaced']} files replaced")
        print(f"  {summary['deleted']} remote files deleted")
        print(f"  {summary['skipped']} files skipped (up to date)")
        print(f"  {summary['failed']} operations failed")
        
        if summary['errors']:
            print("\nErrors encountered:")
            for error in summary['errors']:
                print(f"  {error}")