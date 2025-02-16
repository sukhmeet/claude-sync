# Claude Sync

A file synchronization utility for Claude AI projects that helps you manage and sync your files with Claude's context window.

## Features

- Bi-directional sync between local files and Claude AI
- Smart file tracking with timestamp-based change detection
- Gitignore-style file filtering with `.syncignore`
- Automatic session management
- Debug mode for troubleshooting
- Dry-run capability to preview sync operations
- Comprehensive sync status reporting

## Installation

```bash
pip install claude-sync
```

## Configuration

The tool maintains configuration in two locations:
- Project-specific: `.sync_config.json` in your project directory
- Global: `~/.claude-sync.config` for shared settings like session keys

### First-time Setup

1. Run any claude-sync command to trigger setup:
```bash
claude-sync --status
```

2. You'll be prompted for:
- Organization ID (found in your Claude AI URL)
- Project ID (found in your Claude AI project URL)
- Base URL (defaults to https://claude.ai)
- Session Key (automatically extracted after you copy a cURL command from Chrome DevTools - see "Getting Your Session Key" section below)

### Getting Your Session Key

1. Open Chrome DevTools (F12 or Command+Option+I)
2. Go to the Network tab
3. Visit or refresh claude.ai
4. Find any recent request (e.g. 'chat' or 'account_profile')
5. Right-click the request → Copy → Copy as cURL
6. The tool will automatically extract the session key from your clipboard

### Creating a .syncignore File

Create a `.syncignore` file in your project root to exclude files from syncing:

```
# Example .syncignore
*.pyc
__pycache__/*
.sync_*
.git/*
.env
*.egg-info
dist/
build/
node_modules/
```

Supports gitignore-style patterns:
- Use `*` for wildcards
- Use `**` for recursive matching
- Start with `!` to negate a pattern

## Usage

### View Sync Status
```bash
claude-sync --status
```
Shows:
- Files that need syncing
- Last sync time for each file
- Summary of total files and their states

### List Remote Files
```bash
claude-sync --list-remote
```
Displays:
- All files currently in your Claude project
- Creation/update timestamps
- Total file count

### Preview Sync Operations
```bash
claude-sync --dry-run
```
Shows what would happen during sync:
- Files that would be uploaded
- Files that would be replaced
- Remote files that would be deleted

### Perform Sync
```bash
claude-sync --sync
```
Performs full synchronization:
- Uploads new files
- Updates changed files
- Removes deleted files from remote
- Provides detailed operation summary

### Debug Mode
```bash
claude-sync --status --debug
```
Adds detailed logging for troubleshooting:
- File scanning process
- API responses
- Timing information

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Session key may have expired
   - Follow the session key extraction steps above
   - Ensure you have the correct organization and project IDs

2. **Sync Issues**
   - Check .syncignore patterns
   - Use --debug flag for detailed logging
   - Verify file permissions

3. **Installation Issues**
   - Ensure you have Python 3.7+
   - Check for conflicting packages
   - Try installing in a fresh virtual environment

## License

MIT License - See LICENSE file for details