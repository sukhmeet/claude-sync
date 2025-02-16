import re
import pyperclip
from typing import Optional, Tuple

class ClipboardParser:
    @staticmethod
    def extract_session_key_from_curl() -> Tuple[Optional[str], str]:
        """
        Extract session key from a curl command in clipboard.
        Returns (key, status) where:
        - key is the extracted session key or None
        - status is 'same', 'new', or 'none' to indicate what was found
        """
        try:
            clipboard_content = pyperclip.paste()
            
            # Check if it's a curl command
            if not clipboard_content.strip().lower().startswith('curl'):
                return None, 'none'
                
            # Look for session key patterns
            patterns = [
                # Cookie header pattern
                r'["\']Cookie:\s*sessionKey=([^;"\']+)["\']',
                # -b/--cookie pattern
                r'-b[= ]["\']sessionKey=([^;"\']+)["\']',
                r'--cookie[= ]["\']sessionKey=([^;"\']+)["\']',
                # Raw cookie in URL
                r'sessionKey=([^&;"\']+)',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, clipboard_content, re.IGNORECASE)
                for match in matches:
                    key = match.group(1)
                    if key.startswith('sk-ant-'):
                        return key, 'new'
                    
            return None, 'none'
            
        except Exception as e:
            print(f"Error reading clipboard: {e}")
            return None, 'none'
    
    @staticmethod
    def prompt_for_curl():
        """Display instructions for getting the curl command."""
        print("\nPlease follow these steps to get a fresh session key:")
        print("1. Open Chrome DevTools (F12 or Command+Option+I)")
        print("2. Go to the Network tab")
        print("3. Visit or refresh claude.ai")
        print("4. Find any recent request (e.g. 'chat' or 'account_profile')")
        print("5. Right-click the request -> Copy -> Copy as cURL")
        print("6. Paste the copied curl command in your clipboard")
        print("\nMake sure to copy a fresh request to get a valid session key.")
        print("Press Enter when ready...")
        input()