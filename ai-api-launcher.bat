@echo off
setlocal enabledelayedexpansion

:: Set title
title AI Web Integration Agent Launcher

:menu
cls
echo ===================================================
echo        AI Web Integration Agent Launcher
echo ===================================================
echo.
echo Choose an option:
echo.
echo [1] Launch Claude API (Standard)
echo [2] Launch Claude API (Debug Mode)
echo [3] Launch GitHub Copilot API (Standard)
echo [4] Launch GitHub Copilot API (Debug Mode)
echo [5] Run Troubleshooter
echo [6] View Documentation
echo [7] Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto launch_claude
if "%choice%"=="2" goto launch_claude_debug
if "%choice%"=="3" goto launch_copilot
if "%choice%"=="4" goto launch_copilot_debug
if "%choice%"=="5" goto troubleshoot
if "%choice%"=="6" goto documentation
if "%choice%"=="7" goto exit
goto menu

:launch_claude
cls
echo Launching Claude API (Standard)...
call claude-chrome.bat
goto menu

:launch_claude_debug
cls
echo Launching Claude API (Debug Mode)...
call claude-chrome-debug.bat
goto menu

:launch_copilot
cls
echo Launching GitHub Copilot API (Standard)...
call copilot-chrome.bat
goto menu

:launch_copilot_debug
cls
echo Launching GitHub Copilot API (Debug Mode)...
call copilot-chrome-debug.bat
goto menu

:troubleshoot
cls
echo Running Troubleshooter...
call troubleshoot.bat
goto menu

:documentation
cls
echo ===================================================
echo                  Documentation
echo ===================================================
echo.
echo AI Web Integration Agent provides OpenAI API-compatible
echo endpoints for web-based AI services like Claude and GitHub Copilot.
echo.
echo Available Scripts:
echo.
echo 1. claude-chrome.bat
echo    - Creates an OpenAI API endpoint for Claude using Chrome cookies
echo    - Runs on port 8000
echo.
echo 2. claude-chrome-debug.bat
echo    - Debug version with comprehensive error handling
echo    - Provides detailed logs and troubleshooting
echo.
echo 3. copilot-chrome.bat
echo    - Creates an OpenAI API endpoint for GitHub Copilot using Chrome cookies
echo    - Runs on port 8001
echo.
echo 4. copilot-chrome-debug.bat
echo    - Debug version with comprehensive error handling
echo    - Provides detailed logs and troubleshooting
echo.
echo 5. troubleshoot.bat
echo    - Diagnoses common issues with the setup
echo    - Checks dependencies, network connectivity, and more
echo.
echo Usage Examples:
echo.
echo - Python:
echo   from openai import OpenAI
echo   client = OpenAI(base_url="http://127.0.0.1:8000/v1", api_key="dummy")
echo   response = client.chat.completions.create(
echo     model="claude-3-opus",
echo     messages=[{"role": "user", "content": "Hello, Claude!"}]
echo   )
echo.
echo - cURL:
echo   curl -X POST http://127.0.0.1:8000/v1/chat/completions ^
echo     -H "Content-Type: application/json" ^
echo     -d "{\"model\":\"claude-3-opus\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello, Claude!\"}]}"
echo.
echo Press any key to return to the menu...
pause >nul
goto menu

:exit
echo Exiting...
exit /b 0

endlocal

