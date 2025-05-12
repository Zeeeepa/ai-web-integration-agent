#!/usr/bin/env python3
"""
Example of using the OpenAI API adapter with a Python client.
"""
import os
import sys
import json
import requests

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    """Main entry point."""
    # API endpoint
    api_base = "http://localhost:8000/v1"
    
    # Make a chat completion request
    response = requests.post(
        f"{api_base}/chat/completions",
        json={
            "model": "claude-3-opus",  # Or any supported model
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"}
            ]
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("Response:")
        print(json.dumps(result, indent=2))
        
        # Extract the assistant's message
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0]["message"]["content"]
            print("\nAssistant's response:")
            print(message)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()

