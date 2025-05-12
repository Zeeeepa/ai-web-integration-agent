# AI Web Integration Agent

A tool for integrating web-based AI services with OpenAI-compatible API endpoints.

## Features

- Convert web-based AI services (Claude, Copilot, etc.) to OpenAI API format
- Support for both [ai-gateway](https://github.com/Zeeeepa/ai-gateway) and [chatgpt-adapter](https://github.com/Zeeeepa/chatgpt-adapter) backends
- Cookie-based authentication for web services
- Browser cookie extraction utilities
- CLI interface for easy management
- Comprehensive error handling and debugging tools
- Self-healing deployment scripts

## Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/ai-web-integration-agent.git
cd ai-web-integration-agent

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start with Batch Scripts

For Windows users, we provide ready-to-use batch scripts:

1. **Standard Scripts**:
   - `claude-chrome.bat` - Sets up Claude with Chrome cookies on port 8000
   - `copilot-chrome.bat` - Sets up GitHub Copilot with Chrome cookies on port 8001

2. **Debug Scripts** (with comprehensive error handling):
   - `claude-chrome-debug.bat` - Debug version with detailed logging and error recovery
   - `copilot-chrome-debug.bat` - Debug version with detailed logging and error recovery

3. **Utility Scripts**:
   - `troubleshoot.bat` - Diagnoses common issues with your setup
   - `ai-api-launcher.bat` - Unified launcher with menu for all options

Example:
```batch
# Launch the unified menu
ai-api-launcher.bat

# Or run individual scripts directly
claude-chrome-debug.bat
```

### Starting the OpenAI API Server Manually

```bash
# Using ai-gateway backend
python freeloader_cli_main.py openai start --backend ai-gateway --port 8000

# Using chatgpt-adapter backend
python freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8000
```

### Importing Cookies for Authentication

```bash
# Extract cookies from Firefox for claude.ai
python freeloader_cli_main.py openai import-cookies --browser firefox --domain claude.ai

# Extract cookies from Chrome for github.com
python freeloader_cli_main.py openai import-cookies --browser chrome --domain github.com
```

### Using the OpenAI API

Once the server is running, you can use any OpenAI API client to interact with it:

```python
import openai

# Configure the client to use your local server
openai.api_key = "dummy-key"  # Any value will work
openai.api_base = "http://localhost:8000/v1"

# Make a chat completion request
response = openai.ChatCompletion.create(
    model="claude-3-opus",  # Or any supported model
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
```

## Troubleshooting

If you encounter issues, try the following:

1. Run `troubleshoot.bat` to diagnose common problems
2. Check the log files in `%USERPROFILE%\.freeloader\`
3. Use the debug versions of the batch scripts for more detailed error information
4. Make sure you're logged into the respective services in your browser
5. Try closing all browser windows before extracting cookies
6. Check if the ports (8000, 8001) are already in use by other applications

## Backend Options

### ai-gateway

[ai-gateway](https://github.com/Zeeeepa/ai-gateway) is a Rust-based gateway that provides a unified interface to various LLMs using the OpenAI API format. It supports:

- OpenAI models
- Anthropic Claude models
- Google Gemini models
- And more

### chatgpt-adapter

[chatgpt-adapter](https://github.com/Zeeeepa/chatgpt-adapter) is a Go-based adapter that converts various web-based AI chat interfaces to the OpenAI API format. It supports:

- OpenAI
- Coze
- DeepSeek
- Cursor
- Windsurf
- Qodo
- Blackbox
- You.com
- Grok
- Bing

## Advanced Configuration

### BrokeDev Integration

The tool includes integration with BrokeDev for advanced browser automation and cookie extraction:

```bash
# Extract cookies using BrokeDev
python freeloader_cli_main.py brokedev extract-cookies --browser firefox --domain claude.ai

# Launch a browser using BrokeDev
python freeloader_cli_main.py brokedev launch-browser --url https://claude.ai

# Manage BrokeDev configuration
python freeloader_cli_main.py brokedev config --get browser.headless
python freeloader_cli_main.py brokedev config --set browser.headless=true
```

## License

MIT
