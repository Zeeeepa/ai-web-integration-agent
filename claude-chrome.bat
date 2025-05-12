@echo off
echo Setting up Claude OpenAI API endpoint using Chrome cookies...

REM Create directory for cookies if it doesn't exist
mkdir "%USERPROFILE%\.freeloader" 2>nul

REM Import cookies from Chrome for claude.ai
python freeloader_cli_main.py openai import-cookies --browser chrome --domain claude.ai

REM Start the OpenAI API server with ai-gateway backend
start "Claude OpenAI API" cmd /c "python freeloader_cli_main.py openai start --backend ai-gateway --port 8000 --host 127.0.0.1 && pause"

echo.
echo Claude OpenAI API endpoint is now running!
echo.
echo Base URL: http://127.0.0.1:8000/v1
echo.
echo Available endpoints:
echo   - GET  /v1/models
echo   - POST /v1/chat/completions
echo   - POST /v1/embeddings
echo.
echo Example curl command:
echo curl -X POST http://127.0.0.1:8000/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"claude-3-opus\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello, Claude!\"}]}"
echo.
echo Press Ctrl+C in the other window to stop the server when done.

