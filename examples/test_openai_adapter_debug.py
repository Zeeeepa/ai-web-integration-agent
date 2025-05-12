import os
import sys
import json
import requests
import time
import argparse
from pathlib import Path

def check_cookie_file():
    """Check if the cookie file exists and has content."""
    cookie_path = os.path.join(os.path.expanduser("~"), ".freeloader", "cookies.json")
    
    if not os.path.exists(cookie_path):
        print("[ERROR] Cookie file not found at:", cookie_path)
        return False
    
    try:
        with open(cookie_path, 'r') as f:
            cookies = json.load(f)
        
        if not cookies:
            print("[WARNING] Cookie file exists but is empty.")
            return False
        
        domains = list(cookies.keys())
        if not domains:
            print("[WARNING] No domains found in cookie file.")
            return False
        
        print(f"[OK] Cookie file found with {len(domains)} domains:")
        for domain in domains:
            print(f"  - {domain}: {len(cookies[domain])} cookies")
        
        return True
    except json.JSONDecodeError:
        print("[ERROR] Cookie file exists but is not valid JSON.")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to read cookie file: {str(e)}")
        return False

def check_backend_services():
    """Check if backend services are running."""
    services = [
        {"name": "ai-gateway", "url": "http://localhost:8080", "required_for": "Claude"},
        {"name": "chatgpt-adapter", "url": "http://localhost:8081", "required_for": "GitHub Copilot"}
    ]
    
    all_running = True
    
    for service in services:
        try:
            response = requests.get(service["url"], timeout=2)
            if response.status_code < 400:
                print(f"[OK] {service['name']} is running at {service['url']}")
            else:
                print(f"[WARNING] {service['name']} returned status code {response.status_code}")
                all_running = False
        except requests.exceptions.RequestException:
            print(f"[WARNING] {service['name']} is not running at {service['url']}")
            all_running = False
    
    return all_running

def check_openai_adapter(port=8000):
    """Check if the OpenAI API adapter is running."""
    url = f"http://127.0.0.1:{port}/v1/models"
    
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"[OK] OpenAI API adapter is running at http://127.0.0.1:{port}")
            models = response.json().get("data", [])
            if models:
                print(f"  Available models: {', '.join(model['id'] for model in models)}")
            return True
        else:
            print(f"[WARNING] OpenAI API adapter returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"[WARNING] OpenAI API adapter is not running at http://127.0.0.1:{port}")
        return False

def test_chat_completion(port=8000, model=None):
    """Test the chat completions endpoint."""
    url = f"http://127.0.0.1:{port}/v1/chat/completions"
    
    # Get available models first
    try:
        models_response = requests.get(f"http://127.0.0.1:{port}/v1/models", timeout=5)
        available_models = [model['id'] for model in models_response.json().get("data", [])]
        
        if not model and available_models:
            model = available_models[0]
            print(f"[INFO] Using model: {model}")
        elif not model:
            model = "claude-3-opus-20240229"  # Default fallback
            print(f"[INFO] No models available, using default: {model}")
    except Exception as e:
        model = "claude-3-opus-20240229"  # Default fallback
        print(f"[WARNING] Failed to get models, using default: {model}")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, please respond with a short greeting and the current date and time if you know it."}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    print("\n[TEST] Testing chat completions endpoint...")
    print(f"[INFO] Request to: {url}")
    print(f"[INFO] Using model: {model}")
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=data, timeout=30)
        elapsed_time = time.time() - start_time
        
        print(f"[INFO] Response time: {elapsed_time:.2f} seconds")
        print(f"[INFO] Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"[OK] Chat completion successful!")
            print(f"\nResponse content:\n{content}\n")
            return True
        else:
            print(f"[ERROR] Chat completion failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Chat completion request failed: {str(e)}")
        return False

def test_streaming_chat_completion(port=8000, model=None):
    """Test the streaming chat completions endpoint."""
    url = f"http://127.0.0.1:{port}/v1/chat/completions"
    
    # Get available models first
    try:
        models_response = requests.get(f"http://127.0.0.1:{port}/v1/models", timeout=5)
        available_models = [model['id'] for model in models_response.json().get("data", [])]
        
        if not model and available_models:
            model = available_models[0]
            print(f"[INFO] Using model: {model}")
        elif not model:
            model = "claude-3-opus-20240229"  # Default fallback
            print(f"[INFO] No models available, using default: {model}")
    except Exception as e:
        model = "claude-3-opus-20240229"  # Default fallback
        print(f"[WARNING] Failed to get models, using default: {model}")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Count from 1 to 5 and explain why counting is important."}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
        "stream": True
    }
    
    print("\n[TEST] Testing streaming chat completions endpoint...")
    print(f"[INFO] Request to: {url}")
    print(f"[INFO] Using model: {model}")
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=data, timeout=30, stream=True)
        
        if response.status_code == 200:
            print(f"[OK] Streaming chat completion started!")
            print("\nStreaming response:")
            
            full_content = ""
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]  # Remove 'data: ' prefix
                        if line == '[DONE]':
                            break
                        try:
                            chunk = json.loads(line)
                            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                print(content, end='', flush=True)
                                full_content += content
                        except json.JSONDecodeError:
                            pass
            
            elapsed_time = time.time() - start_time
            print(f"\n\n[INFO] Streaming completed in {elapsed_time:.2f} seconds")
            return True
        else:
            print(f"[ERROR] Streaming chat completion failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Streaming chat completion request failed: {str(e)}")
        return False

def run_diagnostics():
    """Run all diagnostic tests."""
    print("===================================================")
    print("OpenAI API Adapter Diagnostic Tool")
    print("===================================================")
    print()
    
    # Check for OpenAI client
    try:
        import openai
        print("[OK] OpenAI client installed.")
    except ImportError:
        print("[WARNING] OpenAI client not installed. Installing...")
        os.system("pip install openai")
    
    # Check cookie directory and file
    cookie_dir = os.path.join(os.path.expanduser("~"), ".freeloader")
    print("Checking cookie directory...")
    if not os.path.exists(cookie_dir):
        print("Creating cookie directory...")
        os.makedirs(cookie_dir, exist_ok=True)
        print("[OK] Cookie directory created.")
    else:
        print("[OK] Cookie directory already exists.")
    
    print("Checking for cookies...")
    cookie_file = os.path.join(cookie_dir, "cookies.json")
    if not os.path.exists(cookie_file):
        print("[WARNING] Cookie file does not exist.")
        print("Creating empty cookie file...")
        with open(cookie_file, 'w') as f:
            json.dump({}, f)
        print("[OK] Empty cookie file created.")
    else:
        check_cookie_file()
    
    # Check backend services
    print("Checking if backend services are running...")
    check_backend_services()
    
    # Check OpenAI API adapter
    print("Checking if OpenAI API adapter is running...")
    adapter_running = check_openai_adapter()
    
    # Print diagnostic results
    print("\n===================================================")
    print("Diagnostic Results")
    print("===================================================")
    print()
    
    # Check for ai-gateway
    try:
        response = requests.get("http://localhost:8080", timeout=2)
        if response.status_code < 400:
            print("[OK] ai-gateway is running.")
        else:
            print("[ISSUE] ai-gateway is returning errors.")
            print("You need to check ai-gateway logs for more information.")
    except requests.exceptions.RequestException:
        print("[ISSUE] ai-gateway is not running.")
        print("You need to start ai-gateway before using the OpenAI API adapter.")
    
    # Check for chatgpt-adapter
    try:
        response = requests.get("http://localhost:8081", timeout=2)
        if response.status_code < 400:
            print("[OK] chatgpt-adapter is running.")
        else:
            print("[ISSUE] chatgpt-adapter is returning errors.")
            print("You need to check chatgpt-adapter logs for more information.")
    except requests.exceptions.RequestException:
        print("[ISSUE] chatgpt-adapter is not running.")
        print("You need to start chatgpt-adapter before using the OpenAI API adapter with GitHub Copilot.")
    
    # Check for OpenAI API adapter
    if adapter_running:
        print("[OK] OpenAI API adapter is running.")
    else:
        print("[ISSUE] OpenAI API adapter is not running.")
        print("You need to start the OpenAI API adapter.")
    
    # Print recommended actions
    print("\n===================================================")
    print("Recommended Actions")
    print("===================================================")
    print()
    
    if not os.path.exists(cookie_file) or os.path.getsize(cookie_file) == 0 or not check_cookie_file():
        print("1. Import cookies from Chrome for Claude:")
        print("   python freeloader_cli_main.py openai import-cookies --browser chrome --domain claude.ai")
        print()
        print("2. Import cookies from Chrome for GitHub:")
        print("   python freeloader_cli_main.py openai import-cookies --browser chrome --domain github.com")
        print()
    
    try:
        requests.get("http://localhost:8080", timeout=2)
    except requests.exceptions.RequestException:
        print("3. Start the OpenAI API adapter for Claude:")
        print("   python freeloader_cli_main.py openai start --backend ai-gateway --port 8000")
        print()
    
    try:
        requests.get("http://localhost:8081", timeout=2)
    except requests.exceptions.RequestException:
        print("4. Start the OpenAI API adapter for GitHub Copilot:")
        print("   python freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8001")
        print()
    
    print("5. Test the OpenAI API adapter:")
    print("   python examples/test_openai_adapter_debug.py")
    print()
    
    return adapter_running

def interactive_menu():
    """Display an interactive menu for the user."""
    while True:
        print("\n===================================================")
        print("What would you like to do?")
        print("===================================================")
        print()
        print("1. Import cookies from Chrome for Claude")
        print("2. Import cookies from Chrome for GitHub")
        print("3. Start OpenAI API adapter for Claude")
        print("4. Start OpenAI API adapter for GitHub Copilot")
        print("5. Run diagnostic test")
        print("6. Test chat completion")
        print("7. Test streaming chat completion")
        print("8. Exit")
        print()
        
        try:
            choice = int(input("Enter your choice (1-8): "))
            
            if choice == 1:
                os.system("python freeloader_cli_main.py openai import-cookies --browser chrome --domain claude.ai")
            elif choice == 2:
                os.system("python freeloader_cli_main.py openai import-cookies --browser chrome --domain github.com")
            elif choice == 3:
                print("\nStarting OpenAI API adapter for Claude...")
                print("This will run in a new process. Press Ctrl+C to stop it when done.")
                os.system("start cmd /k python freeloader_cli_main.py openai start --backend ai-gateway --port 8000")
            elif choice == 4:
                print("\nStarting OpenAI API adapter for GitHub Copilot...")
                print("This will run in a new process. Press Ctrl+C to stop it when done.")
                os.system("start cmd /k python freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8001")
            elif choice == 5:
                run_diagnostics()
            elif choice == 6:
                port = input("Enter port (default: 8000): ") or "8000"
                test_chat_completion(int(port))
            elif choice == 7:
                port = input("Enter port (default: 8000): ") or "8000"
                test_streaming_chat_completion(int(port))
            elif choice == 8:
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress any key to continue...")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def main():
    parser = argparse.ArgumentParser(description="Test and diagnose the OpenAI API adapter")
    parser.add_argument("--port", type=int, default=8000, help="Port to test (default: 8000)")
    parser.add_argument("--model", type=str, help="Model to use for testing")
    parser.add_argument("--diagnose", action="store_true", help="Run diagnostics only")
    parser.add_argument("--test", action="store_true", help="Run chat completion test")
    parser.add_argument("--stream", action="store_true", help="Run streaming chat completion test")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_menu()
    elif args.diagnose:
        run_diagnostics()
    elif args.test:
        test_chat_completion(args.port, args.model)
    elif args.stream:
        test_streaming_chat_completion(args.port, args.model)
    else:
        # Default behavior: run diagnostics and then interactive menu
        adapter_running = run_diagnostics()
        interactive_menu()

if __name__ == "__main__":
    main()

