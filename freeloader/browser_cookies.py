"""
Browser cookie extraction utilities.
"""
import os
import json
import logging
import sqlite3
import tempfile
import shutil
import subprocess
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

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
        logger.error(f"Unsupported browser: {browser}")
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
            logger.error("Firefox profile not found")
            return []
        
        # Copy cookies.sqlite to a temporary file
        cookies_path = os.path.join(profile_dir, "cookies.sqlite")
        if not os.path.exists(cookies_path):
            logger.error(f"Cookies file not found: {cookies_path}")
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
        logger.error(f"Error extracting Firefox cookies: {str(e)}")
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
            logger.error("Chrome profile not found")
            return []
        
        # Copy cookies.sqlite to a temporary file
        cookies_path = os.path.join(profile_dir, "Cookies")
        if not os.path.exists(cookies_path):
            logger.error(f"Cookies file not found: {cookies_path}")
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
        logger.error(f"Error extracting Chrome cookies: {str(e)}")
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
            logger.error("Edge profile not found")
            return []
        
        # Copy cookies.sqlite to a temporary file
        cookies_path = os.path.join(profile_dir, "Cookies")
        if not os.path.exists(cookies_path):
            logger.error(f"Cookies file not found: {cookies_path}")
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
        logger.error(f"Error extracting Edge cookies: {str(e)}")
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
            logger.error("plutil not found, cannot extract Safari cookies")
            return []
        
        cookies_path = os.path.expanduser("~/Library/Cookies/Cookies.binarycookies")
        if not os.path.exists(cookies_path):
            logger.error(f"Cookies file not found: {cookies_path}")
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
        logger.error(f"Error extracting Safari cookies: {str(e)}")
        return []

def _find_firefox_profile() -> Optional[str]:
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
        logger.error(f"Error finding Firefox profile: {str(e)}")
        return None

def _find_chrome_profile() -> Optional[str]:
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
        logger.error(f"Error finding Chrome profile: {str(e)}")
        return None

def _find_edge_profile() -> Optional[str]:
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
        logger.error(f"Error finding Edge profile: {str(e)}")
        return None

