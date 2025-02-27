# Update to src/claude_sync/cli/main.py

import argparse
from claude_sync.core.syncer import FileSyncer
from datetime import datetime
import os

def format_time(time_str: str) -> str:
    """Format time string to be more readable"""
    if time_str == 'Never':
        return time_str
    try:
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return time_str

def main():
    parser = argparse.ArgumentParser(description='File sync utility for Claude API')
    parser.add_argument('--status', action='store_true', help='Show sync status of all files')
    parser.add_argument('--list-remote', action='store_true', help='List files on remote')
    parser.add_argument('--sync', action='store_true', help='Sync files to remote')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be synced without actually syncing')
    parser.add_argument('--debug', action='store_true', help='Show debug information')
    
    args = parser.parse_args()
    
    syncer = FileSyncer(debug=args.debug)
    
    if args.status:
        sync_status, delete_status = syncer.get_sync_status()
        
        # If first run, just exit since the summary was already shown
        if syncer.first_run or not sync_status:
            return
        
        # Count statistics
        total_files = len(sync_status)
        needs_sync = sum(1 for info in sync_status.values() if info['needs_sync'])
        up_to_date = total_files - needs_sync
        
        # Print file statuses in a table format
        print("\nLocal File Status:")
        
        # Headers with status first, then last sync time, then filename
        print(f"{'Status':<15} {'Last Sync':<25} File")
        print("-" * 80)  # Table separator
        
        for filepath, info in sorted(sync_status.items()):
            last_sync = format_time(info['last_sync'])
            sync_state = "Needs sync" if info['needs_sync'] else "Up to date"
            print(f"{sync_state:<15} {last_sync:<25} {filepath}")
        
        # Print files to be deleted if any
        if delete_status:
            print("\nRemote Files to Delete:")
            for filepath in sorted(delete_status.keys()):
                print(f"  {filepath}")
        
        # Print summary
        print(f"\nSummary:")
        print(f"Total files:  {total_files}")
        print(f"Need sync:    {needs_sync}")
        print(f"Up to date:   {up_to_date}")
        if delete_status:
            print(f"To delete:    {len(delete_status)}")
    
    elif args.list_remote:
        # If first run, just handle the first-run scenario in get_sync_status
        if syncer.first_run:
            syncer.get_sync_status()
            return
            
        remote_files = syncer.api_client.list_remote_files()
        
        if not remote_files:
            print("\nNo files found on remote.")
            return
            
        # Print table header
        print("\nRemote Files:")
        print(f"{'Created At':<25} File Name")
        print("-" * 65)
        
        # Sort files by name for consistent display
        for file in sorted(remote_files, key=lambda x: x['file_name']):
            created_at = format_time(file['created_at'])
            print(f"{created_at:<25} {file['file_name']}")
            
        # Print summary
        print(f"\nTotal files: {len(remote_files)}")
    
    elif args.sync or args.dry_run:
        # Get sync status first
        sync_status, delete_status = syncer.get_sync_status()
        
        # If first run, just exit since the summary was already shown
        if syncer.first_run or not sync_status:
            return
            
        files_to_sync = {f: s for f, s in sync_status.items() if s['needs_sync']}
        
        # Show what will be synced
        if files_to_sync:
            print("\nFiles to sync:")
            for filepath, info in files_to_sync.items():
                action = "Upload new file" if info['action'] == 'upload' else "Replace existing file"
                print(f"  {filepath} - {action}")
        
        if delete_status:
            print("\nRemote files to delete:")
            for filepath in delete_status:
                print(f"  {filepath}")
                
        if not files_to_sync and not delete_status:
            print("\nNo changes to sync.")
            return
            
        # For dry-run, stop here
        if args.dry_run:
            return
            
        # For actual sync, ask for confirmation
        print(f"\nSummary of changes:")
        print(f"  Files to upload/update: {len(files_to_sync)}")
        print(f"  Remote files to delete: {len(delete_status)}")
        
        response = input("\nDo you want to proceed with these changes? [y/N] ").lower().strip()
        if response != 'y':
            print("Sync cancelled.")
            return
            
        # Proceed with sync
        print("\nStarting sync...")
        syncer.sync_files(dry_run=False)
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()