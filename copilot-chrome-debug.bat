@echo off
setlocal enabledelayedexpansion

:: Set error logging file
set "LOG_FILE=%USERPROFILE%\.freeloader\copilot_error.log"
set "DEBUG_MODE=1"
set "PORT=8001"
set "HOST=127.0.0.1"
set "BACKEND=chatgpt-adapter"
set "DOMAIN=github.com"
set "BROWSER=chrome"
set "MAX_RETRIES=3"
set "RETRY_DELAY=5"
set "PYTHON_CMD=python"

:: Create header for log file
echo ---------------------------------------- > "%LOG_FILE%"
echo GitHub Copilot OpenAI API Deployment Log >> "%LOG_FILE%"
echo Started at: %date% %time% >> "%LOG_FILE%"
echo ---------------------------------------- >> "%LOG_FILE%"

:: Display banner
echo.
echo ===================================================
echo  GitHub Copilot OpenAI API Endpoint Setup - Debug Mode
echo ===================================================
echo.

:: Check if Python is installed
call :log_info "Checking Python installation..."
%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    call :log_error "Python is not installed or not in PATH. Please install Python 3.7+ and try again."
    call :display_error "Python is not installed or not in PATH"
    call :suggest_fix "Install Python 3.7+ from https://www.python.org/downloads/"
    call :suggest_fix "Make sure Python is added to your PATH during installation"
    goto :error_exit
)

:: Check if required packages are installed
call :log_info "Checking required packages..."
%PYTHON_CMD% -c "import click" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    call :log_warning "Required packages not found. Attempting to install..."
    call :install_requirements
    if %ERRORLEVEL% NEQ 0 (
        call :log_error "Failed to install required packages."
        call :display_error "Failed to install required packages"
        call :suggest_fix "Try running: pip install -r requirements.txt"
        goto :error_exit
    )
)

:: Create directory for cookies if it doesn't exist
call :log_info "Setting up cookie directory..."
if not exist "%USERPROFILE%\.freeloader" (
    mkdir "%USERPROFILE%\.freeloader" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        call :log_error "Failed to create directory: %USERPROFILE%\.freeloader"
        call :display_error "Failed to create cookie directory"
        call :suggest_fix "Check if you have write permissions to %USERPROFILE%"
        goto :error_exit
    )
)

:: Check if Chrome is installed
call :log_info "Checking Chrome installation..."
if "%BROWSER%"=="chrome" (
    reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            call :log_warning "Chrome not found in registry. Will attempt to continue anyway..."
            call :display_warning "Chrome not detected in standard location"
            call :suggest_fix "Make sure Chrome is installed if cookie extraction fails"
        )
    )
)

:: Check if chatgpt-adapter backend is available
call :log_info "Checking for %BACKEND% backend..."
if "%BACKEND%"=="chatgpt-adapter" (
    %PYTHON_CMD% -c "import importlib.util; print(importlib.util.find_spec('freeloader.openai_adapter.adapter') is not None)" | findstr "True" >nul
    if %ERRORLEVEL% NEQ 0 (
        call :log_warning "chatgpt-adapter backend may not be properly installed. Will attempt to continue..."
        call :display_warning "chatgpt-adapter backend may not be properly installed"
        call :suggest_fix "If server fails to start, try reinstalling the package"
    )
)

:: Import cookies from Chrome for github.com
call :log_info "Importing cookies from %BROWSER% for %DOMAIN%..."
echo.
echo [1/3] Importing cookies from %BROWSER% for %DOMAIN%...
set retry_count=0

:retry_import_cookies
%PYTHON_CMD% freeloader_cli_main.py openai import-cookies --browser %BROWSER% --domain %DOMAIN% 2>> "%LOG_FILE%"
if %ERRORLEVEL% NEQ 0 (
    set /a retry_count+=1
    if !retry_count! LEQ %MAX_RETRIES% (
        call :log_warning "Cookie import failed. Retrying (!retry_count!/%MAX_RETRIES%)..."
        call :display_warning "Cookie import failed. Retrying (!retry_count!/%MAX_RETRIES%)..."
        timeout /t %RETRY_DELAY% /nobreak >nul
        goto :retry_import_cookies
    ) else (
        call :log_error "Failed to import cookies after %MAX_RETRIES% attempts."
        call :display_error "Failed to import cookies from %BROWSER%"
        call :suggest_fix "Make sure you're logged into %DOMAIN% in %BROWSER%"
        call :suggest_fix "Make sure you have GitHub Copilot access in your account"
        call :suggest_fix "Try closing all %BROWSER% windows and try again"
        call :suggest_fix "Check the log file: %LOG_FILE%"
        goto :error_exit
    )
)

echo [✓] Successfully imported cookies from %BROWSER%
echo.

:: Start the OpenAI API server with chatgpt-adapter backend
call :log_info "Starting OpenAI API server with %BACKEND% backend on %HOST%:%PORT%..."
echo [2/3] Starting OpenAI API server with %BACKEND% backend...
echo [3/3] Server will be available at http://%HOST%:%PORT%/v1

:: Start the server in a new window with error handling
start "Copilot OpenAI API" cmd /c "echo Starting GitHub Copilot OpenAI API server... & %PYTHON_CMD% freeloader_cli_main.py openai start --backend %BACKEND% --port %PORT% --host %HOST% --debug 2>> "%LOG_FILE%" || (echo Server crashed! Check %LOG_FILE% for details. & pause & exit /b 1) & echo Server running successfully! & pause"

:: Wait a moment to allow the server to start
timeout /t 2 /nobreak >nul

:: Check if the server is running by attempting to connect to it
call :log_info "Verifying server is running..."
curl -s -o nul -w "%%{http_code}" http://%HOST%:%PORT%/v1/models >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    call :log_warning "Could not verify server is running. It may still be starting up..."
    call :display_warning "Could not verify server is running"
    call :suggest_fix "Check the server window for any error messages"
    call :suggest_fix "If server fails to start, check the log file: %LOG_FILE%"
) else (
    call :log_info "Server verified running at http://%HOST%:%PORT%/v1"
)

:: Display success message
echo.
echo ===================================================
echo  GitHub Copilot OpenAI API endpoint is now running!
echo ===================================================
echo.
echo Base URL: http://%HOST%:%PORT%/v1
echo.
echo Available endpoints:
echo   - GET  /v1/models
echo   - POST /v1/chat/completions
echo   - POST /v1/embeddings
echo.
echo Example curl command:
echo curl -X POST http://%HOST%:%PORT%/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"gpt-4\",\"messages\":[{\"role\":\"user\",\"content\":\"Write a function to calculate Fibonacci numbers\"}]}"
echo.
echo Debug log: %LOG_FILE%
echo.
echo Press Ctrl+C in the server window to stop the server when done.
goto :eof

:: ===== FUNCTIONS =====

:log_info
echo [INFO] [%date% %time%] %~1 >> "%LOG_FILE%"
if "%DEBUG_MODE%"=="1" echo [INFO] %~1
exit /b 0

:log_warning
echo [WARNING] [%date% %time%] %~1 >> "%LOG_FILE%"
if "%DEBUG_MODE%"=="1" echo [WARNING] %~1
exit /b 0

:log_error
echo [ERROR] [%date% %time%] %~1 >> "%LOG_FILE%"
if "%DEBUG_MODE%"=="1" echo [ERROR] %~1
exit /b 0

:display_error
echo.
echo [31m✘ ERROR: %~1[0m
echo.
exit /b 0

:display_warning
echo.
echo [33m⚠ WARNING: %~1[0m
echo.
exit /b 0

:suggest_fix
echo [36m  → %~1[0m
exit /b 0

:install_requirements
call :log_info "Installing required packages..."
%PYTHON_CMD% -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
exit /b %ERRORLEVEL%

:error_exit
echo.
echo [31m✘ Setup failed! See %LOG_FILE% for details.[0m
echo.
echo Press any key to exit...
pause >nul
exit /b 1

:eof
endlocal

