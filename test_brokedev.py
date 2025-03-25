#!/usr/bin/env python3
"""
Test BrokeDev integration with the freeloader framework.
"""
import os
import sys
from freeloader.brokedev.integration.bridge import BrokeDevBridge
from freeloader.brokedev.integration.config import BrokeDevConfig

def test_config_loading():
    """Test that configuration loads properly."""
    config = BrokeDevConfig()
    print("Configuration loaded successfully:")
    print(f"- Browser User Data Dir: {config.get('browser.user_data_dir')}")
    print(f"- Screenshot Dir: {config.get('browser.screenshot_dir')}")
    print(f"- Claude URL: {config.get('claude.url')}")
    return True

def test_cookie_extraction():
    """Test cookie extraction functionality."""
    try:
        bridge = BrokeDevBridge()
        print("Attempting to extract Firefox cookies...")
        cookies = bridge.extract_cookies(browser="firefox", domain="github.com")
        print(f"Successfully extracted {len(cookies)} cookies")
        return True
    except Exception as e:
        print(f"Error extracting cookies: {e}")
        return False

if __name__ == "__main__":
    print("Testing BrokeDev integration...")
    
    tests = [
        ("Config Loading", test_config_loading),
        ("Cookie Extraction", test_cookie_extraction),
    ]
    
    success = True
    for name, test_func in tests:
        print(f"\n=== Testing {name} ===")
        try:
            result = test_func()
            if result:
                print(f"✅ {name} test succeeded")
            else:
                print(f"❌ {name} test failed")
                success = False
        except Exception as e:
            print(f"❌ {name} test threw an exception: {e}")
            success = False
    
    sys.exit(0 if success else 1)