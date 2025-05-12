"""
Bridge for BrokeDev integration within the freeloader framework.
"""
import os
import logging
import subprocess
import json
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class BrokeDevBridge:
    """Bridge for BrokeDev integration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the BrokeDev bridge.
        
        Args:
            config_path: Path to the BrokeDev config file
        """
        from freeloader.brokedev.integration.config import BrokeDevConfig
        self.config = BrokeDevConfig(config_path)
    
    def extract_cookies(self, browser: str, domain: str) -> List[Dict[str, Any]]:
        """
        Extract cookies from a browser using BrokeDev.
        
        Args:
            browser: The browser to extract from ('chrome', 'firefox', etc.)
            domain: The domain to extract cookies for
            
        Returns:
            List of cookie dictionaries
        """
        try:
            # Check if the BrokeDev cookie extraction script exists
            script_dir = self.config.get('python_scripts_dir', './python')
            script_path = os.path.join(script_dir, 'extract_cookies.py')
            
            if not os.path.exists(script_path):
                # Create the script if it doesn't exist
                self._create_cookie_extraction_script(script_path)
            
            # Run the script
            cmd = [
                'python', script_path,
                '--browser', browser,
                '--domain', domain
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Error extracting cookies: {result.stderr}")
                return []
            
            # Parse the output
            try:
                cookies = json.loads(result.stdout)
                return cookies
            except json.JSONDecodeError:
                logger.error(f"Error parsing cookie extraction output: {result.stdout}")
                return []
        
        except Exception as e:
            logger.error(f"Error extracting cookies with BrokeDev: {str(e)}")
            return []
    
    def _create_cookie_extraction_script(self, script_path: str):
        """
        Create the cookie extraction script.
        
        Args:
            script_path: Path to create the script at
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            
            # Script content
            script_content = '''#!/usr/bin/env python3
"""
Cookie extraction script for BrokeDev integration.
"""
import argparse
import json
import os
import sqlite3
import tempfile
import shutil
import sys
from typing import Dict, Any, List

def extract_cookies(browser: str, domain: str) -> List[Dict[str, Any]]:
    """
    Extract cookies from a browser.
    
    Args:
        browser: The browser to extract from ('chrome', 'firefox', etc.)
        domain: The domain to extract cookies for
        
    Returns:
        List of cookie dictionaries
    """
    if browser.lower() == 'firefox':
        return extract_firefox_cookies(domain)
    elif browser.lower() == 'chrome':
        return extract_chrome_cookies(domain)
    elif browser.lower() == 'edge':
        return extract_edge_cookies(domain)
    elif browser.lower() == 'safari':
        return extract_safari_cookies(domain)
    else:
        print(f"Unsupported browser: {browser}", file=sys.stderr)
        return []

def extract_firefox_cookies(domain: str) -> List[Dict[str, Any]]:
    """
    Extract cookies from Firefox.
    
    Args:
        domain: The domain to extract cookies for
        
    Returns:
        List of cookie dictionaries
    """
    try:
        # Find Firefox profile directory
        profile_dir = _find_firefox_profile()
        if not profile_dir:
            print("Firefox profile not found", file=sys.stderr)
            return []
        
        # Copy cookies.sqlite to a temporary file
        cookies_path = os.path.join(profile_dir, "cookies.sqlite")
        if not os.path.exists(cookies_path):
            print(f"Cookies file not found: {cookies_path}", file=sys.stderr)
            return []
        
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as temp_file:
            temp_path = temp_file.name
        
        shutil.copy2(cookies_path, temp_path)
        
        # Query the database
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        
        # Prepare domain pattern for SQL LIKE
        domain_pattern = f"%{domain}%"
        
        cursor.execute(
            "SELECT name, value, host, path, expiry, isSecure, isHttpOnly "
            "FROM moz_cookies "
            "WHERE host LIKE ?",
            (domain_pattern,)
        )
        
        cookies = []
        for row in cursor.fetchall():
            name, value, host, path, expiry, is_secure, is_http_only = row
            cookies.append({
                "name": name,
                "value": value,
                "domain": host,
                "path": path,
                "expires": expiry,
                "secure": bool(is_secure),
                "httpOnly": bool(is_http_only)
            })
        
        conn.close()
        os.unlink(temp_path)
        
        return cookies
    
    except Exception as e:
        print(f"Error extracting Firefox cookies: {str(e)}", file=sys.stderr)
        return []

def extract_chrome_cookies(domain: str) -> List[Dict[str, Any]]:
    """
    Extract cookies from Chrome.
    
    Args:
        domain: The domain to extract cookies for
        
    Returns:
        List of cookie dictionaries
    """
    try:
        # Find Chrome profile directory
        profile_dir = _find_chrome_profile()
        if not profile_dir:
            print("Chrome profile not found", file=sys.stderr)
            return []
        
        # Copy cookies.sqlite to a temporary file
        cookies_path = os.path.join(profile_dir, "Cookies")
        if not os.path.exists(cookies_path):
            print(f"Cookies file not found: {cookies_path}", file=sys.stderr)
            return []
        
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as temp_file:
            temp_path = temp_file.name
        
        shutil.copy2(cookies_path, temp_path)
        
        # Query the database
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        
        # Prepare domain pattern for SQL LIKE
        domain_pattern = f"%{domain}%"
        
        cursor.execute(
            "SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly "
            "FROM cookies "
            "WHERE host_key LIKE ?",
            (domain_pattern,)
        )
        
        cookies = []
        for row in cursor.fetchall():
            name, value, host, path, expiry, is_secure, is_http_only = row
            cookies.append({
                "name": name,
                "value": value,
                "domain": host,
                "path": path,
                "expires": expiry,
                "secure": bool(is_secure),
                "httpOnly": bool(is_http_only)
            })
        
        conn.close()
        os.unlink(temp_path)
        
        return cookies
    
    except Exception as e:
        print(f"Error extracting Chrome cookies: {str(e)}", file=sys.stderr)
        return []

def extract_edge_cookies(domain: str) -> List[Dict[str, Any]]:
    """
    Extract cookies from Edge.
    
    Args:
        domain: The domain to extract cookies for
        
    Returns:
        List of cookie dictionaries
    """
    try:
        # Edge uses the same format as Chrome
        # Find Edge profile directory
        profile_dir = _find_edge_profile()
        if not profile_dir:
            print("Edge profile not found", file=sys.stderr)
            return []
        
        # Copy cookies.sqlite to a temporary file
        cookies_path = os.path.join(profile_dir, "Cookies")
        if not os.path.exists(cookies_path):
            print(f"Cookies file not found: {cookies_path}", file=sys.stderr)
            return []
        
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as temp_file:
            temp_path = temp_file.name
        
        shutil.copy2(cookies_path, temp_path)
        
        # Query the database
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        
        # Prepare domain pattern for SQL LIKE
        domain_pattern = f"%{domain}%"
        
        cursor.execute(
            "SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly "
            "FROM cookies "
            "WHERE host_key LIKE ?",
            (domain_pattern,)
        )
        
        cookies = []
        for row in cursor.fetchall():
            name, value, host, path, expiry, is_secure, is_http_only = row
            cookies.append({
                "name": name,
                "value": value,
                "domain": host,
                "path": path,
                "expires": expiry,
                "secure": bool(is_secure),
                "httpOnly": bool(is_http_only)
            })
        
        conn.close()
        os.unlink(temp_path)
        
        return cookies
    
    except Exception as e:
        print(f"Error extracting Edge cookies: {str(e)}", file=sys.stderr)
        return []

def extract_safari_cookies(domain: str) -> List[Dict[str, Any]]:
    """
    Extract cookies from Safari.
    
    Args:
        domain: The domain to extract cookies for
        
    Returns:
        List of cookie dictionaries
    """
    try:
        # Safari cookies are stored in a binary plist file
        # This is a simplified implementation
        if not os.path.exists("/usr/bin/plutil"):
            print("plutil not found, cannot extract Safari cookies", file=sys.stderr)
            return []
        
        cookies_path = os.path.expanduser("~/Library/Cookies/Cookies.binarycookies")
        if not os.path.exists(cookies_path):
            print(f"Cookies file not found: {cookies_path}", file=sys.stderr)
            return []
        
        # Convert binary plist to JSON using plutil
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        subprocess.run(["/usr/bin/plutil", "-convert", "json", "-o", temp_path, cookies_path])
        
        # Read the JSON file
        with open(temp_path, 'r') as f:
            data = json.load(f)
        
        # Filter cookies by domain
        cookies = []
        for cookie in data.get("Cookies", []):
            if domain in cookie.get("Domain", ""):
                cookies.append({
                    "name": cookie.get("Name"),
                    "value": cookie.get("Value"),
                    "domain": cookie.get("Domain"),
                    "path": cookie.get("Path"),
                    "expires": cookie.get("Expires"),
                    "secure": cookie.get("Secure", False),
                    "httpOnly": cookie.get("HttpOnly", False)
                })
        
        os.unlink(temp_path)
        
        return cookies
    
    except Exception as e:
        print(f"Error extracting Safari cookies: {str(e)}", file=sys.stderr)
        return []

def _find_firefox_profile():
    """Find the Firefox profile directory."""
    try:
        # Check common locations
        locations = [
            os.path.expanduser("~/.mozilla/firefox"),  # Linux
            os.path.expanduser("~/Library/Application Support/Firefox/Profiles"),  # macOS
            os.path.join(os.environ.get("APPDATA", ""), "Mozilla", "Firefox", "Profiles")  # Windows
        ]
        
        for location in locations:
            if os.path.exists(location):
                # Find the default profile
                profiles_ini = os.path.join(os.path.dirname(location), "profiles.ini")
                if os.path.exists(profiles_ini):
                    # Parse profiles.ini to find the default profile
                    with open(profiles_ini, 'r') as f:
                        lines = f.readlines()
                    
                    current_profile = {}
                    profiles = []
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith("[Profile"):
                            if current_profile:
                                profiles.append(current_profile)
                            current_profile = {}
                        elif "=" in line and current_profile is not None:
                            key, value = line.split("=", 1)
                            current_profile[key.strip()] = value.strip()
                    
                    if current_profile:
                        profiles.append(current_profile)
                    
                    # Find the default profile
                    for profile in profiles:
                        if profile.get("Default") == "1" or profile.get("Name") == "default":
                            if "Path" in profile:
                                if profile.get("IsRelative") == "1":
                                    return os.path.join(os.path.dirname(location), profile["Path"])
                                else:
                                    return profile["Path"]
                
                # If no default profile found, just return the first profile directory
                for item in os.listdir(location):
                    if os.path.isdir(os.path.join(location, item)) and item.endswith(".default"):
                        return os.path.join(location, item)
        
        return None
    
    except Exception as e:
        print(f"Error finding Firefox profile: {str(e)}", file=sys.stderr)
        return None

def _find_chrome_profile():
    """Find the Chrome profile directory."""
    try:
        # Check common locations
        locations = [
            os.path.expanduser("~/.config/google-chrome/Default"),  # Linux
            os.path.expanduser("~/Library/Application Support/Google/Chrome/Default"),  # macOS
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "Default")  # Windows
        ]
        
        for location in locations:
            if os.path.exists(location):
                return location
        
        return None
    
    except Exception as e:
        print(f"Error finding Chrome profile: {str(e)}", file=sys.stderr)
        return None

def _find_edge_profile():
    """Find the Edge profile directory."""
    try:
        # Check common locations
        locations = [
            os.path.expanduser("~/.config/microsoft-edge/Default"),  # Linux
            os.path.expanduser("~/Library/Application Support/Microsoft Edge/Default"),  # macOS
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data", "Default")  # Windows
        ]
        
        for location in locations:
            if os.path.exists(location):
                return location
        
        return None
    
    except Exception as e:
        print(f"Error finding Edge profile: {str(e)}", file=sys.stderr)
        return None

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Extract cookies from a browser")
    parser.add_argument("--browser", required=True, help="Browser to extract from")
    parser.add_argument("--domain", required=True, help="Domain to extract cookies for")
    args = parser.parse_args()
    
    cookies = extract_cookies(args.browser, args.domain)
    print(json.dumps(cookies))

if __name__ == "__main__":
    main()
'''
            
            # Write the script
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make the script executable
            os.chmod(script_path, 0o755)
        
        except Exception as e:
            logger.error(f"Error creating cookie extraction script: {str(e)}")
    
    def launch_browser(self, url: str, headless: bool = False) -> bool:
        """
        Launch a browser using BrokeDev.
        
        Args:
            url: The URL to open
            headless: Whether to run in headless mode
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if the BrokeDev browser launch script exists
            script_dir = self.config.get('python_scripts_dir', './python')
            script_path = os.path.join(script_dir, 'launch_browser.py')
            
            if not os.path.exists(script_path):
                # Create the script if it doesn't exist
                self._create_browser_launch_script(script_path)
            
            # Run the script
            cmd = [
                'python', script_path,
                '--url', url
            ]
            
            if headless:
                cmd.append('--headless')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Error launching browser: {result.stderr}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error launching browser with BrokeDev: {str(e)}")
            return False
    
    def _create_browser_launch_script(self, script_path: str):
        """
        Create the browser launch script.
        
        Args:
            script_path: Path to create the script at
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            
            # Script content
            script_content = '''#!/usr/bin/env python3
"""
Browser launch script for BrokeDev integration.
"""
import argparse
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def launch_browser(url: str, headless: bool = False) -> bool:
    """
    Launch a browser.
    
    Args:
        url: The URL to open
        headless: Whether to run in headless mode
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Set up Chrome options
        options = Options()
        
        if headless:
            options.add_argument("--headless")
        
        # Add anti-bot measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Create the driver
        driver = webdriver.Chrome(options=options)
        
        # Set the window size
        driver.set_window_size(1280, 800)
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load
        time.sleep(5)
        
        # Take a screenshot
        screenshot_dir = os.path.expanduser("~/.brokedev/screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, "browser.png")
        driver.save_screenshot(screenshot_path)
        
        # Close the browser
        driver.quit()
        
        return True
    
    except Exception as e:
        print(f"Error launching browser: {str(e)}", file=sys.stderr)
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Launch a browser")
    parser.add_argument("--url", required=True, help="URL to open")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    args = parser.parse_args()
    
    success = launch_browser(args.url, args.headless)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
'''
            
            # Write the script
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make the script executable
            os.chmod(script_path, 0o755)
        
        except Exception as e:
            logger.error(f"Error creating browser launch script: {str(e)}")

