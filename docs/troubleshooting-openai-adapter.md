# Troubleshooting the OpenAI API Adapter

This guide will help you diagnose and fix issues with the OpenAI API adapter for web-based AI services.

## Prerequisites

Before using the OpenAI API adapter, make sure you have:

1. Installed all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Installed the OpenAI Python client (optional, for testing):
   ```bash
   pip install openai
   ```

3. Set up the backend services:
   - For Claude: [ai-gateway](https://github.com/Zeeeepa/ai-gateway)
   - For GitHub Copilot: [chatgpt-adapter](https://github.com/Zeeeepa/chatgpt-adapter)

## Common Issues and Solutions

### 1. "Connection refused" error

**Symptoms:**
- Error message: "Connection refused"
- Cannot connect to the OpenAI API adapter server

**Possible causes:**
- The OpenAI API adapter server is not running
- The server is running on a different port
- A firewall is blocking the connection

**Solutions:**
- Start the server:
  ```bash
  python freeloader_cli_main.py openai start --backend ai-gateway --port 8000
  ```
- Check if the server is running:
  ```bash
  curl http://127.0.0.1:8000/v1/models
  ```
- Try a different port:
  ```bash
  python freeloader_cli_main.py openai start --backend ai-gateway --port 8001
  ```

### 2. "Backend error" message

**Symptoms:**
- Error message: "Backend error: 404" or similar
- The OpenAI API adapter server is running, but requests fail

**Possible causes:**
- The backend service (ai-gateway or chatgpt-adapter) is not running
- The backend service is running on a different port
- The backend service URL is incorrect

**Solutions:**
- Start the backend service:
  - For ai-gateway:
    ```bash
    cd ai-gateway
    cargo run --release
    ```
  - For chatgpt-adapter:
    ```bash
    cd chatgpt-adapter
    node index.js
    ```
- Specify the correct backend URL:
  ```bash
  python freeloader_cli_main.py openai start --backend ai-gateway --backend-url http://localhost:8080
  ```

### 3. Authentication issues

**Symptoms:**
- Error message: "Unauthorized" or similar
- The backend service returns an authentication error

**Possible causes:**
- No cookies imported for the domain
- Cookies are expired or invalid
- The cookie store file is corrupted

**Solutions:**
- Import cookies from your browser:
  ```bash
  python freeloader_cli_main.py openai import-cookies --browser chrome --domain claude.ai
  ```
- Check if cookies were imported successfully:
  ```bash
  cat ~/.freeloader/cookies.json
  ```
- Clear and reimport cookies:
  ```bash
  python freeloader_cli_main.py openai clear-cookies
  python freeloader_cli_main.py openai import-cookies --browser chrome --domain claude.ai
  ```

### 4. Missing dependencies

**Symptoms:**
- Error message: "ModuleNotFoundError: No module named 'flask'" or similar
- The server fails to start

**Solutions:**
- Install the required dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Install specific missing dependencies:
  ```bash
  pip install flask requests openai
  ```

### 5. Cookie extraction issues

**Symptoms:**
- Error message: "Error importing cookies" or similar
- No cookies are imported

**Possible causes:**
- The browser is not supported
- The browser profile cannot be found
- The cookie database is locked

**Solutions:**
- Close all browser windows before importing cookies
- Try a different browser:
  ```bash
  python freeloader_cli_main.py openai import-cookies --browser firefox --domain claude.ai
  ```
- Manually export cookies using a browser extension and import them

## Advanced Troubleshooting

### Running the Debug Script

We've provided a comprehensive debug script that can help diagnose issues:

```bash
python examples/test_openai_adapter_debug.py
```

This script will:
1. Check if all required dependencies are installed
2. Check if the cookie store exists and is valid
3. Check if the backend services are running
4. Check if the OpenAI API adapter server is running
5. Test chat completion and streaming
6. Provide recommendations based on the results

### Checking Backend Services

To check if the backend services are running:

```bash
# For ai-gateway
curl http://localhost:8080/v1/models

# For chatgpt-adapter
curl http://localhost:8081/v1/models
```

### Enabling Debug Mode

To get more detailed logs, start the server in debug mode:

```bash
python freeloader_cli_main.py openai start --backend ai-gateway --debug
```

### Checking Port Availability

To check if a port is already in use:

```bash
# On Linux/macOS
lsof -i :8000

# On Windows
netstat -ano | findstr :8000
```

## Setting Up Backend Services

### Setting Up ai-gateway

1. Clone the repository:
   ```bash
   git clone https://github.com/Zeeeepa/ai-gateway.git
   cd ai-gateway
   ```

2. Build the project:
   ```bash
   cargo build --release
   ```

3. Start the server:
   ```bash
   ./target/release/ai-gateway
   ```

### Setting Up chatgpt-adapter

1. Clone the repository:
   ```bash
   git clone https://github.com/Zeeeepa/chatgpt-adapter.git
   cd chatgpt-adapter
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the server:
   ```bash
   node index.js
   ```

## Testing the OpenAI API Adapter

### Using curl

```bash
# List models
curl http://127.0.0.1:8000/v1/models

# Chat completion
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20240229",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "temperature": 0.7
  }'
```

### Using the OpenAI Python Client

```python
import openai

client = openai.OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="dummy-key"  # The adapter doesn't check API keys
)

# List models
models = client.models.list()
print(models)

# Chat completion
chat_completion = client.chat.completions.create(
    model="claude-3-opus-20240229",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ],
    temperature=0.7,
)
print(chat_completion.choices[0].message.content)
```

## Still Having Issues?

If you're still experiencing problems after trying the solutions above:

1. Check the server logs for more detailed error messages
2. Try running the server with different backends and configurations
3. Make sure your browser cookies are valid by logging into the service manually
4. Check if the backend services are working correctly by testing them directly

