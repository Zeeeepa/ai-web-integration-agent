#!/bin/bash

# OpenAI API Adapter Diagnostic and Repair Tool

echo "==================================================="
echo "OpenAI API Adapter Diagnostic and Repair Tool"
echo "==================================================="
echo

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python is not installed."
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
else
    echo "[OK] Python is installed."
fi

# Check pip installation
echo "Checking pip installation..."
if ! python3 -m pip --version &> /dev/null; then
    echo "[ERROR] pip is not installed."
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install pip."
        exit 1
    fi
else
    echo "[OK] pip is installed."
fi

# Install required packages
echo "Installing required packages..."
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[WARNING] Some packages failed to install."
else
    echo "[OK] Required packages installed."
fi

# Install OpenAI client for testing
echo "Installing OpenAI client for testing..."
python3 -m pip install openai
if [ $? -ne 0 ]; then
    echo "[WARNING] Failed to install OpenAI client."
else
    echo "[OK] OpenAI client installed."
fi

# Create cookie directory if it doesn't exist
echo "Creating cookie directory..."
mkdir -p ~/.freeloader
echo "[OK] Cookie directory created or already exists."

# Check if cookies exist
echo "Checking for cookies..."
if [ -f ~/.freeloader/cookies.json ]; then
    echo "[OK] Cookie file exists."
else
    echo "[WARNING] Cookie file does not exist."
    echo "Creating empty cookie file..."
    echo "{}" > ~/.freeloader/cookies.json
    echo "[OK] Empty cookie file created."
fi

# Check if backend services are running
echo "Checking if backend services are running..."

# Check ai-gateway
if curl -s http://localhost:8080/v1/models &> /dev/null; then
    echo "[OK] ai-gateway is running at http://localhost:8080"
    ai_gateway_running=1
else
    echo "[WARNING] ai-gateway is not running at http://localhost:8080"
    ai_gateway_running=0
fi

# Check chatgpt-adapter
if curl -s http://localhost:8081/v1/models &> /dev/null; then
    echo "[OK] chatgpt-adapter is running at http://localhost:8081"
    chatgpt_adapter_running=1
else
    echo "[WARNING] chatgpt-adapter is not running at http://localhost:8081"
    chatgpt_adapter_running=0
fi

# Check if OpenAI API adapter is running
echo "Checking if OpenAI API adapter is running..."
if curl -s http://127.0.0.1:8000/v1/models &> /dev/null; then
    echo "[OK] OpenAI API adapter is running at http://127.0.0.1:8000"
    adapter_running=1
else
    echo "[WARNING] OpenAI API adapter is not running at http://127.0.0.1:8000"
    adapter_running=0
fi

echo
echo "==================================================="
echo "Diagnostic Results"
echo "==================================================="
echo

if [ $ai_gateway_running -eq 0 ]; then
    echo "[ISSUE] ai-gateway is not running."
    echo "You need to start ai-gateway before using the OpenAI API adapter."
    echo
fi

if [ $chatgpt_adapter_running -eq 0 ]; then
    echo "[ISSUE] chatgpt-adapter is not running."
    echo "You need to start chatgpt-adapter before using the OpenAI API adapter with GitHub Copilot."
    echo
fi

if [ $adapter_running -eq 0 ]; then
    echo "[ISSUE] OpenAI API adapter is not running."
    echo "You need to start the OpenAI API adapter."
    echo
fi

echo
echo "==================================================="
echo "Recommended Actions"
echo "==================================================="
echo

echo "1. Import cookies from Chrome for Claude:"
echo "   python3 freeloader_cli_main.py openai import-cookies --browser chrome --domain claude.ai"
echo
echo "2. Import cookies from Chrome for GitHub:"
echo "   python3 freeloader_cli_main.py openai import-cookies --browser chrome --domain github.com"
echo
echo "3. Start the OpenAI API adapter for Claude:"
echo "   python3 freeloader_cli_main.py openai start --backend ai-gateway --port 8000"
echo
echo "4. Start the OpenAI API adapter for GitHub Copilot:"
echo "   python3 freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8001"
echo
echo "5. Test the OpenAI API adapter:"
echo "   python3 examples/test_openai_adapter_debug.py"
echo

menu() {
    echo "==================================================="
    echo "What would you like to do?"
    echo "==================================================="
    echo
    echo "1. Import cookies from Chrome for Claude"
    echo "2. Import cookies from Chrome for GitHub"
    echo "3. Start OpenAI API adapter for Claude"
    echo "4. Start OpenAI API adapter for GitHub Copilot"
    echo "5. Run diagnostic test"
    echo "6. Exit"
    echo

    read -p "Enter your choice (1-6): " choice

    case $choice in
        1)
            echo
            echo "Importing cookies from Chrome for Claude..."
            python3 freeloader_cli_main.py openai import-cookies --browser chrome --domain claude.ai
            echo
            read -p "Press Enter to continue..."
            clear
            menu
            ;;
        2)
            echo
            echo "Importing cookies from Chrome for GitHub..."
            python3 freeloader_cli_main.py openai import-cookies --browser chrome --domain github.com
            echo
            read -p "Press Enter to continue..."
            clear
            menu
            ;;
        3)
            echo
            echo "Starting OpenAI API adapter for Claude..."
            gnome-terminal -- bash -c "python3 freeloader_cli_main.py openai start --backend ai-gateway --port 8000; read -p 'Press Enter to close...'" 2>/dev/null || \
            xterm -e "python3 freeloader_cli_main.py openai start --backend ai-gateway --port 8000; read -p 'Press Enter to close...'" 2>/dev/null || \
            terminal -e "python3 freeloader_cli_main.py openai start --backend ai-gateway --port 8000; read -p 'Press Enter to close...'" 2>/dev/null || \
            python3 freeloader_cli_main.py openai start --backend ai-gateway --port 8000
            echo
            echo "OpenAI API adapter for Claude started."
            echo
            read -p "Press Enter to continue..."
            clear
            menu
            ;;
        4)
            echo
            echo "Starting OpenAI API adapter for GitHub Copilot..."
            gnome-terminal -- bash -c "python3 freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8001; read -p 'Press Enter to close...'" 2>/dev/null || \
            xterm -e "python3 freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8001; read -p 'Press Enter to close...'" 2>/dev/null || \
            terminal -e "python3 freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8001; read -p 'Press Enter to close...'" 2>/dev/null || \
            python3 freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8001
            echo
            echo "OpenAI API adapter for GitHub Copilot started."
            echo
            read -p "Press Enter to continue..."
            clear
            menu
            ;;
        5)
            echo
            echo "Running diagnostic test..."
            python3 examples/test_openai_adapter_debug.py
            echo
            read -p "Press Enter to continue..."
            clear
            menu
            ;;
        6)
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            read -p "Press Enter to continue..."
            clear
            menu
            ;;
    esac
}

menu

