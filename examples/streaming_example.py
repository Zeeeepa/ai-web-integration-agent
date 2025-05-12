#!/usr/bin/env python3
"""
Example of using the OpenAI API adapter with streaming.
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
    
    # Make a streaming chat completion request
    response = requests.post(
        f"{api_base}/chat/completions",
        json={
            "model": "claude-3-opus",  # Or any supported model
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a short poem about AI."}
            ],
            "stream": True
        },
        stream=True
    )
    
    if response.status_code == 200:
        print("Streaming response:")
        
        # Process the streaming response
        for line in response.iter_lines():
            if line:
                # Remove the "data: " prefix
                line = line.decode('utf-8')
                if line.startswith("data: "):
                    line = line[6:]
                
                # Skip the "[DONE]" message
                if line == "[DONE]":
                    continue
                
                try:
                    # Parse the JSON
                    data = json.loads(line)
                    
                    # Extract the content delta
                    if "choices" in data and len(data["choices"]) > 0:
                        delta = data["choices"][0].get("delta", {})
                        if "content" in delta:
                            print(delta["content"], end="", flush=True)
                except json.JSONDecodeError:
                    print(f"Error parsing JSON: {line}")
        
        print("\n\nStreaming complete.")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()

