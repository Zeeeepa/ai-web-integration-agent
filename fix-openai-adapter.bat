@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo OpenAI API Adapter Diagnostic and Repair Tool
echo ===================================================
echo.

:: Check Python installation
echo Checking Python installation...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    goto :end
) else (
    echo [OK] Python is installed.
)

:: Check pip installation
echo Checking pip installation...
python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip is not installed.
    echo Installing pip...
    python -m ensurepip --upgrade
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install pip.
        goto :end
    )
) else (
    echo [OK] pip is installed.
)

:: Install required packages
echo Installing required packages...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some packages failed to install.
) else (
    echo [OK] Required packages installed.
)

:: Install OpenAI client for testing
echo Installing OpenAI client for testing...
python -m pip install openai
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Failed to install OpenAI client.
) else (
    echo [OK] OpenAI client installed.
)

:: Create cookie directory if it doesn't exist
echo Creating cookie directory...
mkdir "%USERPROFILE%\.freeloader" 2>nul
echo [OK] Cookie directory created or already exists.

:: Check if cookies exist
echo Checking for cookies...
if exist "%USERPROFILE%\.freeloader\cookies.json" (
    echo [OK] Cookie file exists.
) else (
    echo [WARNING] Cookie file does not exist.
    echo Creating empty cookie file...
    echo {} > "%USERPROFILE%\.freeloader\cookies.json"
    echo [OK] Empty cookie file created.
)

:: Check if backend services are running
echo Checking if backend services are running...

:: Check ai-gateway
curl -s http://localhost:8080/v1/models >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] ai-gateway is not running at http://localhost:8080
    set ai_gateway_running=0
) else (
    echo [OK] ai-gateway is running at http://localhost:8080
    set ai_gateway_running=1
)

:: Check chatgpt-adapter
curl -s http://localhost:8081/v1/models >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] chatgpt-adapter is not running at http://localhost:8081
    set chatgpt_adapter_running=0
) else (
    echo [OK] chatgpt-adapter is running at http://localhost:8081
    set chatgpt_adapter_running=1
)

:: Check if OpenAI API adapter is running
echo Checking if OpenAI API adapter is running...
curl -s http://127.0.0.1:8000/v1/models >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] OpenAI API adapter is not running at http://127.0.0.1:8000
    set adapter_running=0
) else (
    echo [OK] OpenAI API adapter is running at http://127.0.0.1:8000
    set adapter_running=1
)

echo.
echo ===================================================
echo Diagnostic Results
echo ===================================================
echo.

if !ai_gateway_running!==0 (
    echo [ISSUE] ai-gateway is not running.
    echo You need to start ai-gateway before using the OpenAI API adapter.
    echo.
)

if !chatgpt_adapter_running!==0 (
    echo [ISSUE] chatgpt-adapter is not running.
    echo You need to start chatgpt-adapter before using the OpenAI API adapter with GitHub Copilot.
    echo.
)

if !adapter_running!==0 (
    echo [ISSUE] OpenAI API adapter is not running.
    echo You need to start the OpenAI API adapter.
    echo.
)

echo.
echo ===================================================
echo Recommended Actions
echo ===================================================
echo.

echo 1. Import cookies from Chrome for Claude:
echo    python freeloader_cli_main.py openai import-cookies --browser chrome --domain claude.ai
echo.
echo 2. Import cookies from Chrome for GitHub:
echo    python freeloader_cli_main.py openai import-cookies --browser chrome --domain github.com
echo.
echo 3. Start the OpenAI API adapter for Claude:
echo    python freeloader_cli_main.py openai start --backend ai-gateway --port 8000
echo.
echo 4. Start the OpenAI API adapter for GitHub Copilot:
echo    python freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8001
echo.
echo 5. Test the OpenAI API adapter:
echo    python examples/test_openai_adapter_debug.py
echo.

echo ===================================================
echo What would you like to do?
echo ===================================================
echo.
echo 1. Import cookies from Chrome for Claude
echo 2. Import cookies from Chrome for GitHub
echo 3. Start OpenAI API adapter for Claude
echo 4. Start OpenAI API adapter for GitHub Copilot
echo 5. Run diagnostic test
echo 6. Exit
echo.

set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" (
    echo.
    echo Importing cookies from Chrome for Claude...
    python freeloader_cli_main.py openai import-cookies --browser chrome --domain claude.ai
    echo.
    pause
    goto :menu
)

if "%choice%"=="2" (
    echo.
    echo Importing cookies from Chrome for GitHub...
    python freeloader_cli_main.py openai import-cookies --browser chrome --domain github.com
    echo.
    pause
    goto :menu
)

if "%choice%"=="3" (
    echo.
    echo Starting OpenAI API adapter for Claude...
    start "Claude OpenAI API" cmd /c "python freeloader_cli_main.py openai start --backend ai-gateway --port 8000 && pause"
    echo.
    echo OpenAI API adapter for Claude started in a new window.
    echo.
    pause
    goto :menu
)

if "%choice%"=="4" (
    echo.
    echo Starting OpenAI API adapter for GitHub Copilot...
    start "GitHub Copilot OpenAI API" cmd /c "python freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8001 && pause"
    echo.
    echo OpenAI API adapter for GitHub Copilot started in a new window.
    echo.
    pause
    goto :menu
)

if "%choice%"=="5" (
    echo.
    echo Running diagnostic test...
    python examples/test_openai_adapter_debug.py
    echo.
    pause
    goto :menu
)

if "%choice%"=="6" (
    goto :end
)

:menu
cls
goto :start

:end
echo.
echo ===================================================
echo Thank you for using the OpenAI API Adapter Diagnostic and Repair Tool
echo ===================================================
echo.
pause

