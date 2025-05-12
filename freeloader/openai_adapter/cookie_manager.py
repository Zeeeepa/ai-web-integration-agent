"""
Cookie management for the OpenAI API adapter.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CookieManager:
    """
    Manages cookies for authentication with web-based AI services.
    """
    
    def __init__(self, cookie_store_path: Optional[str] = None):
        """
        Initialize the cookie manager.
        
        Args:
            cookie_store_path: Path to the cookie store file
        """
        self.cookie_store_path = cookie_store_path or os.path.expanduser("~/.freeloader/cookies.json")
        self.cookies = self._load_cookies()
    
    def _load_cookies(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load cookies from the cookie store."""
        try:
            if os.path.exists(self.cookie_store_path):
                with open(self.cookie_store_path, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logger.error(f"Error loading cookies: {str(e)}")
            return {}
    
    def _save_cookies(self):
        """Save cookies to the cookie store."""
        try:
            os.makedirs(os.path.dirname(self.cookie_store_path), exist_ok=True)
            with open(self.cookie_store_path, 'w') as f:
                json.dump(self.cookies, f)
        except Exception as e:
            logger.error(f"Error saving cookies: {str(e)}")
    
    def add_cookies(self, domain: str, cookies: List[Dict[str, Any]]):
        """
        Add cookies for a domain.
        
        Args:
            domain: The domain to add cookies for
            cookies: List of cookie dictionaries
        """
        self.cookies[domain] = cookies
        self._save_cookies()
    
    def get_cookies_for_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get cookies for a domain.
        
        Args:
            domain: The domain to get cookies for
            
        Returns:
            List of cookie dictionaries
        """
        return self.cookies.get(domain, [])
    
    def clear_cookies(self, domain: Optional[str] = None):
        """
        Clear cookies.
        
        Args:
            domain: The domain to clear cookies for, or None to clear all cookies
        """
        if domain:
            if domain in self.cookies:
                del self.cookies[domain]
        else:
            self.cookies = {}
        
        self._save_cookies()
    
    def import_from_browser(self, browser: str, domain: str, 
                           bridge = None) -> List[Dict[str, Any]]:
        """
        Import cookies from a browser.
        
        Args:
            browser: The browser to import from ('chrome', 'firefox', etc.)
            domain: The domain to import cookies for
            bridge: Optional BrokeDevBridge instance
            
        Returns:
            List of imported cookies
        """
        try:
            if bridge:
                # Use BrokeDevBridge if available
                cookies = bridge.extract_cookies(browser=browser, domain=domain)
            else:
                # Try to use built-in cookie extraction
                from freeloader.browser_cookies import extract_cookies
                cookies = extract_cookies(browser=browser, domain=domain)
            
            if cookies:
                self.add_cookies(domain, cookies)
                return cookies
            else:
                logger.warning(f"No cookies found for {domain} in {browser}")
                return []
        
        except ImportError:
            logger.error("Cookie extraction module not available")
            return []
        
        except Exception as e:
            logger.error(f"Error importing cookies: {str(e)}")
            return []

