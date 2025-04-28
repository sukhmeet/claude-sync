# Updated src/claude_sync/utils/ignore_parser.py

import os
import fnmatch
from typing import List, Tuple

class GitignoreParser:
    def __init__(self, ignore_file: str = ".syncignore"):
        self.ignore_file = ignore_file
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> List[Tuple[bool, str]]:
        """Load patterns as tuples of (is_include, pattern)"""
        patterns = []
        if os.path.exists(self.ignore_file):
            with open(self.ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        is_include = line.startswith('!')
                        pattern = line[1:] if is_include else line
                        
                        # Remove leading slash if present (makes pattern relative to root)
                        if pattern.startswith('/'):
                            pattern = pattern[1:]
                            
                        # Add pattern to list
                        patterns.append((is_include, pattern))
        return patterns

    def should_ignore(self, filepath: str) -> bool:
        """
        Determine if a file should be ignored.
        Returns True if the file should be ignored, False if it should be included.
        """
        if not self.patterns:
            return False

        # Default to not ignoring anything
        should_exclude = False

        # Normalize path separators to forward slashes
        filepath = filepath.replace('\\', '/')
        
        # Check all patterns in order
        for is_include, pattern in self.patterns:
            # Handle different pattern types
            
            # Case 1: Directory-specific pattern with **
            if '**' in pattern:
                # Replace ** with a wildcard that matches anything
                regex_pattern = pattern.replace('**', '*')
                if fnmatch.fnmatch(filepath, regex_pattern):
                    should_exclude = not is_include
                    continue
            
            # Case 2: Pattern with trailing slash (directory only)
            if pattern.endswith('/'):
                # For directories, check if the path starts with the pattern
                dir_pattern = pattern[:-1]  # Remove trailing slash
                
                # More explicit check for files inside directory
                if (filepath == dir_pattern or 
                    filepath.startswith(f"{dir_pattern}/") or 
                    f"/{dir_pattern}/" in filepath):
                    should_exclude = not is_include
                    continue
            
            # Case 3: Standard file pattern
            if fnmatch.fnmatch(filepath, pattern) or fnmatch.fnmatch(os.path.basename(filepath), pattern):
                should_exclude = not is_include
                continue
                
            # Case 4: Pattern might be for a subdirectory
            if '/' in pattern:
                # Check if any part of the path matches the pattern
                parts = filepath.split('/')
                for i in range(len(parts)):
                    subpath = '/'.join(parts[i:])
                    if fnmatch.fnmatch(subpath, pattern):
                        should_exclude = not is_include
                        break
            
            # Case 5: Handle directory patterns that should match all contents
            if not pattern.endswith('/*') and not pattern.endswith('/**'):
                # If this pattern is a directory name
                if os.path.sep not in pattern and filepath.startswith(f"{pattern}/"):
                    should_exclude = not is_include
                    continue
                
                # Check if this file is in a directory that matches the pattern
                path_parts = filepath.split('/')
                for i in range(len(path_parts)):
                    if fnmatch.fnmatch(path_parts[i], pattern):
                        should_exclude = not is_include
                        break
        
        return should_exclude
    
    def debug_patterns(self) -> List[str]:
        """Return loaded patterns for debugging"""
        return [f"{'Include' if is_include else 'Exclude'}: {pattern}" 
                for is_include, pattern in self.patterns]