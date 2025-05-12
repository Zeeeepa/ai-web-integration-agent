@echo off
echo Setting up GitHub Copilot OpenAI API endpoint using Chrome cookies...

REM Create directory for cookies if it doesn't exist
mkdir "%USERPROFILE%\.freeloader" 2>nul

REM Import cookies from Chrome for github.com
python freeloader_cli_main.py openai import-cookies --browser chrome --domain github.com

REM Start the OpenAI API server with chatgpt-adapter backend on a different port
start "Copilot OpenAI API" cmd /c "python freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8001 --host 127.0.0.1 && pause"

echo.
echo GitHub Copilot OpenAI API endpoint is now running!
echo.
echo Base URL: http://127.0.0.1:8001/v1
echo.
echo Available endpoints:
echo   - GET  /v1/models
echo   - POST /v1/chat/completions
echo   - POST /v1/embeddings
echo.
echo Example curl command:
echo curl -X POST http://127.0.0.1:8001/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"gpt-4\",\"messages\":[{\"role\":\"user\",\"content\":\"Write a function to calculate Fibonacci numbers\"}]}"
echo.
echo Press Ctrl+C in the other window to stop the server when done.

