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
                        
                        # Ensure folder patterns match full path
                        if not pattern.endswith('/*') and not pattern.endswith('/**'):
                            if os.path.sep in pattern:  # If it's a path
                                pattern = f"{pattern}/**"  # Match all contents
                            
                        patterns.append((is_include, pattern))
        return patterns

    def should_ignore(self, filepath: str) -> bool:
        """
        Determine if a file should be ignored.
        Returns True if the file should be ignored, False if it should be included.
        """
        if not self.patterns:
            return False

        # Start with default from first pattern
        # If first pattern is a negation, default to exclude
        should_exclude = True

        # Normalize path separators
        filepath = filepath.replace('\\', '/')
        
        for is_include, pattern in self.patterns:
            # Handle both exact directory matches and wildcard patterns
            if fnmatch.fnmatch(filepath, pattern) or \
               fnmatch.fnmatch(filepath, f"{pattern}/*") or \
               fnmatch.fnmatch(filepath, pattern.rstrip('/*')):
                should_exclude = not is_include
                
        return should_exclude

    def debug_patterns(self) -> List[str]:
        """Return loaded patterns for debugging"""
        return [f"{'Include' if is_include else 'Exclude'}: {pattern}" 
                for is_include, pattern in self.patterns]