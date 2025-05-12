#!/usr/bin/env python3
"""
Comprehensive debug script for the OpenAI API adapter.
This script tests the adapter with detailed error reporting.
"""
import sys
import os
import json
import logging
import requests
import traceback
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("openai_adapter_debug")

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = ["flask", "requests", "openai"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} is NOT installed")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Installing missing packages...")
        
        for package in missing_packages:
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"✅ Successfully installed {package}")
            except Exception as e:
                logger.error(f"❌ Failed to install {package}: {str(e)}")
    
    return len(missing_packages) == 0

def check_cookie_store():
    """Check if the cookie store exists and is valid."""
    cookie_store_path = os.path.expanduser("~/.freeloader/cookies.json")
    
    if not os.path.exists(cookie_store_path):
        logger.warning(f"⚠️ Cookie store not found at {cookie_store_path}")
        
        # Create empty cookie store
        os.makedirs(os.path.dirname(cookie_store_path), exist_ok=True)
        with open(cookie_store_path, 'w') as f:
            json.dump({}, f)
        
        logger.info(f"✅ Created empty cookie store at {cookie_store_path}")
        return False
    
    try:
        with open(cookie_store_path, 'r') as f:
            cookies = json.load(f)
        
        logger.info(f"✅ Cookie store found at {cookie_store_path}")
        
        # Check if there are any cookies
        if not cookies:
            logger.warning("⚠️ Cookie store is empty")
            return False
        
        # Check if there are cookies for claude.ai or github.com
        domains = list(cookies.keys())
        logger.info(f"📋 Domains with cookies: {', '.join(domains)}")
        
        if "claude.ai" not in domains and "github.com" not in domains:
            logger.warning("⚠️ No cookies found for claude.ai or github.com")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error reading cookie store: {str(e)}")
        return False

def check_server_running(host="127.0.0.1", port=8000):
    """Check if the OpenAI API adapter server is running."""
    try:
        response = requests.get(f"http://{host}:{port}/v1/models", timeout=5)
        
        if response.status_code == 200:
            logger.info(f"✅ Server is running at http://{host}:{port}")
            logger.info(f"📋 Available models: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            logger.error(f"❌ Server returned status code {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Server is not running at http://{host}:{port}")
        return False
    
    except Exception as e:
        logger.error(f"❌ Error connecting to server: {str(e)}")
        return False

def test_chat_completion(host="127.0.0.1", port=8000):
    """Test the chat completion endpoint."""
    try:
        # Try to import openai
        try:
            import openai
            logger.info("✅ Using OpenAI Python client")
            
            # Configure the client
            client = openai.OpenAI(
                base_url=f"http://{host}:{port}/v1",
                api_key="dummy-key"  # The adapter doesn't check API keys
            )
            
            # Chat completion
            logger.info("📤 Sending chat completion request...")
            chat_completion = client.chat.completions.create(
                model="claude-3-opus-20240229",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, how are you?"}
                ],
                temperature=0.7,
            )
            
            logger.info("✅ Chat completion successful")
            logger.info(f"📋 Response: {json.dumps(chat_completion.model_dump(), indent=2)}")
            return True
        
        except ImportError:
            logger.warning("⚠️ OpenAI Python client not installed, using requests")
            
            # Use requests instead
            response = requests.post(
                f"http://{host}:{port}/v1/chat/completions",
                json={
                    "model": "claude-3-opus-20240229",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Hello, how are you?"}
                    ],
                    "temperature": 0.7
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info("✅ Chat completion successful")
                logger.info(f"📋 Response: {json.dumps(response.json(), indent=2)}")
                return True
            else:
                logger.error(f"❌ Chat completion failed with status code {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
    
    except Exception as e:
        logger.error(f"❌ Error in chat completion: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_streaming(host="127.0.0.1", port=8000):
    """Test streaming chat completion."""
    try:
        # Try to import openai
        try:
            import openai
            logger.info("✅ Using OpenAI Python client")
            
            # Configure the client
            client = openai.OpenAI(
                base_url=f"http://{host}:{port}/v1",
                api_key="dummy-key"  # The adapter doesn't check API keys
            )
            
            # Streaming chat completion
            logger.info("📤 Sending streaming chat completion request...")
            stream = client.chat.completions.create(
                model="claude-3-opus-20240229",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Count from 1 to 5."}
                ],
                temperature=0.7,
                stream=True,
            )
            
            logger.info("✅ Streaming chat completion started")
            logger.info("📋 Streaming response:")
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")
            
            print()
            logger.info("✅ Streaming chat completion finished")
            return True
        
        except ImportError:
            logger.warning("⚠️ OpenAI Python client not installed, using requests")
            
            # Use requests instead
            response = requests.post(
                f"http://{host}:{port}/v1/chat/completions",
                json={
                    "model": "claude-3-opus-20240229",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Count from 1 to 5."}
                    ],
                    "temperature": 0.7,
                    "stream": True
                },
                headers={"Content-Type": "application/json"},
                stream=True
            )
            
            if response.status_code == 200:
                logger.info("✅ Streaming chat completion started")
                logger.info("📋 Streaming response:")
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith("data: "):
                            data = line[6:]
                            if data != "[DONE]":
                                try:
                                    chunk = json.loads(data)
                                    if "choices" in chunk and chunk["choices"] and "delta" in chunk["choices"][0] and "content" in chunk["choices"][0]["delta"]:
                                        print(chunk["choices"][0]["delta"]["content"], end="")
                                except:
                                    pass
                
                print()
                logger.info("✅ Streaming chat completion finished")
                return True
            else:
                logger.error(f"❌ Streaming chat completion failed with status code {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
    
    except Exception as e:
        logger.error(f"❌ Error in streaming chat completion: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def check_backend_services():
    """Check if the backend services (ai-gateway, chatgpt-adapter) are running."""
    backends = [
        {"name": "ai-gateway", "url": "http://localhost:8080"},
        {"name": "chatgpt-adapter", "url": "http://localhost:8081"}
    ]
    
    for backend in backends:
        try:
            response = requests.get(f"{backend['url']}/v1/models", timeout=2)
            
            if response.status_code == 200:
                logger.info(f"✅ {backend['name']} is running at {backend['url']}")
                return True
            else:
                logger.warning(f"⚠️ {backend['name']} returned status code {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ {backend['name']} is not running at {backend['url']}")
        
        except Exception as e:
            logger.warning(f"⚠️ Error connecting to {backend['name']}: {str(e)}")
    
    logger.error("❌ No backend services (ai-gateway, chatgpt-adapter) are running")
    return False

def main():
    """Main function."""
    logger.info("🔍 Starting OpenAI API adapter debug")
    
    # Check dependencies
    logger.info("🔍 Checking dependencies...")
    dependencies_ok = check_dependencies()
    
    # Check cookie store
    logger.info("🔍 Checking cookie store...")
    cookie_store_ok = check_cookie_store()
    
    # Check backend services
    logger.info("🔍 Checking backend services...")
    backend_ok = check_backend_services()
    
    # Check if server is running
    logger.info("🔍 Checking if server is running...")
    server_ok = check_server_running()
    
    if server_ok:
        # Test chat completion
        logger.info("🔍 Testing chat completion...")
        chat_ok = test_chat_completion()
        
        # Test streaming
        logger.info("🔍 Testing streaming chat completion...")
        streaming_ok = test_streaming()
    else:
        chat_ok = False
        streaming_ok = False
    
    # Print summary
    logger.info("📋 Debug summary:")
    logger.info(f"Dependencies: {'✅' if dependencies_ok else '❌'}")
    logger.info(f"Cookie store: {'✅' if cookie_store_ok else '⚠️'}")
    logger.info(f"Backend services: {'✅' if backend_ok else '⚠️'}")
    logger.info(f"Server running: {'✅' if server_ok else '❌'}")
    logger.info(f"Chat completion: {'✅' if chat_ok else '❌'}")
    logger.info(f"Streaming: {'✅' if streaming_ok else '❌'}")
    
    # Print recommendations
    logger.info("📋 Recommendations:")
    
    if not dependencies_ok:
        logger.info("❌ Install missing dependencies: pip install flask requests openai")
    
    if not cookie_store_ok:
        logger.info("⚠️ Import cookies for authentication:")
        logger.info("   python freeloader_cli_main.py openai import-cookies --browser chrome --domain claude.ai")
        logger.info("   python freeloader_cli_main.py openai import-cookies --browser chrome --domain github.com")
    
    if not backend_ok:
        logger.info("❌ Start the backend services:")
        logger.info("   1. Install ai-gateway: git clone https://github.com/Zeeeepa/ai-gateway.git && cd ai-gateway && cargo build --release")
        logger.info("   2. Start ai-gateway: ./target/release/ai-gateway")
        logger.info("   3. Install chatgpt-adapter: git clone https://github.com/Zeeeepa/chatgpt-adapter.git && cd chatgpt-adapter && npm install")
        logger.info("   4. Start chatgpt-adapter: node index.js")
    
    if not server_ok:
        logger.info("❌ Start the OpenAI API adapter server:")
        logger.info("   python freeloader_cli_main.py openai start --backend ai-gateway --port 8000")
    
    if not chat_ok or not streaming_ok:
        logger.info("❌ Check the server logs for errors")

if __name__ == "__main__":
    main()

