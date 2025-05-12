@echo off
setlocal enabledelayedexpansion

:: Set variables
set "LOG_FILE=%USERPROFILE%\.freeloader\troubleshoot.log"
set "PYTHON_CMD=python"

:: Create header for log file
echo ---------------------------------------- > "%LOG_FILE%"
echo AI Web Integration Agent Troubleshooting Log >> "%LOG_FILE%"
echo Started at: %date% %time% >> "%LOG_FILE%"
echo ---------------------------------------- >> "%LOG_FILE%"

:: Display banner
echo.
echo ===================================================
echo       AI Web Integration Agent Troubleshooter
echo ===================================================
echo.

:: Check if Python is installed
echo [1/7] Checking Python installation...
%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [31m✘ Python is not installed or not in PATH[0m
    echo   → Install Python 3.7+ from https://www.python.org/downloads/
    echo   → Make sure Python is added to your PATH during installation
    echo [Python: FAILED] >> "%LOG_FILE%"
) else (
    %PYTHON_CMD% --version >> "%LOG_FILE%" 2>&1
    echo [32m✓ Python is installed[0m
    echo [Python: OK] >> "%LOG_FILE%"
)

:: Check if pip is installed
echo.
echo [2/7] Checking pip installation...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [31m✘ pip is not installed or not working[0m
    echo   → Try reinstalling Python with pip included
    echo [pip: FAILED] >> "%LOG_FILE%"
) else (
    %PYTHON_CMD% -m pip --version >> "%LOG_FILE%" 2>&1
    echo [32m✓ pip is installed[0m
    echo [pip: OK] >> "%LOG_FILE%"
)

:: Check if required packages are installed
echo.
echo [3/7] Checking required packages...
%PYTHON_CMD% -c "import click, logging, sys" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [31m✘ Required packages are missing[0m
    echo   → Try running: pip install -r requirements.txt
    echo [Packages: FAILED] >> "%LOG_FILE%"
    %PYTHON_CMD% -c "import sys; print('Python path: ' + str(sys.path))" >> "%LOG_FILE%" 2>&1
) else (
    echo [32m✓ Basic required packages are installed[0m
    echo [Packages: OK] >> "%LOG_FILE%"
)

:: Check if freeloader module is available
echo.
echo [4/7] Checking freeloader module...
%PYTHON_CMD% -c "import importlib.util; print(importlib.util.find_spec('freeloader') is not None)" | findstr "True" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [31m✘ freeloader module is not available[0m
    echo   → Make sure you're in the correct directory
    echo   → Try reinstalling the package
    echo [freeloader: FAILED] >> "%LOG_FILE%"
) else (
    echo [32m✓ freeloader module is available[0m
    echo [freeloader: OK] >> "%LOG_FILE%"
    %PYTHON_CMD% -c "import freeloader; print('freeloader version: ' + getattr(freeloader, '__version__', 'unknown'))" >> "%LOG_FILE%" 2>&1
)

:: Check if backend modules are available
echo.
echo [5/7] Checking backend modules...
%PYTHON_CMD% -c "import importlib.util; print('ai-gateway: ' + str(importlib.util.find_spec('freeloader.openai_adapter.adapter') is not None))" >> "%LOG_FILE%" 2>&1
%PYTHON_CMD% -c "import importlib.util; print('chatgpt-adapter: ' + str(importlib.util.find_spec('freeloader.openai_adapter.adapter') is not None))" >> "%LOG_FILE%" 2>&1

%PYTHON_CMD% -c "import importlib.util; print(importlib.util.find_spec('freeloader.openai_adapter.adapter') is not None)" | findstr "True" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [31m✘ Backend modules are not available[0m
    echo   → Try reinstalling the package
    echo [Backends: FAILED] >> "%LOG_FILE%"
) else (
    echo [32m✓ Backend modules are available[0m
    echo [Backends: OK] >> "%LOG_FILE%"
)

:: Check if cookie directory exists
echo.
echo [6/7] Checking cookie directory...
if not exist "%USERPROFILE%\.freeloader" (
    echo [31m✘ Cookie directory does not exist[0m
    echo   → Run one of the setup scripts to create it
    echo   → Or manually create: %USERPROFILE%\.freeloader
    echo [Cookie directory: FAILED] >> "%LOG_FILE%"
) else (
    echo [32m✓ Cookie directory exists[0m
    echo [Cookie directory: OK] >> "%LOG_FILE%"
    dir "%USERPROFILE%\.freeloader" >> "%LOG_FILE%" 2>&1
)

:: Check if browser is installed
echo.
echo [7/7] Checking browser installations...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [33m⚠ Chrome not detected in standard location[0m
        echo   → Cookie extraction may fail if Chrome is not installed
        echo [Chrome: NOT FOUND] >> "%LOG_FILE%"
    ) else (
        echo [32m✓ Chrome is installed (user profile)[0m
        echo [Chrome: OK (user)] >> "%LOG_FILE%"
    )
) else (
    echo [32m✓ Chrome is installed (system-wide)[0m
    echo [Chrome: OK (system)] >> "%LOG_FILE%"
)

reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [33m⚠ Firefox not detected in standard location[0m
    echo [Firefox: NOT FOUND] >> "%LOG_FILE%"
) else (
    echo [32m✓ Firefox is installed[0m
    echo [Firefox: OK] >> "%LOG_FILE%"
)

:: Check network connectivity
echo.
echo [+] Checking network connectivity...
ping -n 1 claude.ai >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [33m⚠ Cannot reach claude.ai[0m
    echo   → Check your internet connection
    echo   → Check if the site is blocked by your network
    echo [Network claude.ai: FAILED] >> "%LOG_FILE%"
) else (
    echo [32m✓ Can reach claude.ai[0m
    echo [Network claude.ai: OK] >> "%LOG_FILE%"
)

ping -n 1 github.com >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [33m⚠ Cannot reach github.com[0m
    echo   → Check your internet connection
    echo   → Check if the site is blocked by your network
    echo [Network github.com: FAILED] >> "%LOG_FILE%"
) else (
    echo [32m✓ Can reach github.com[0m
    echo [Network github.com: OK] >> "%LOG_FILE%"
)

:: Check if ports are available
echo.
echo [+] Checking if ports are available...
netstat -an | findstr ":8000" >nul
if %ERRORLEVEL% EQU 0 (
    echo [33m⚠ Port 8000 is already in use[0m
    echo   → Change the port in the batch file or stop the service using this port
    echo [Port 8000: IN USE] >> "%LOG_FILE%"
) else (
    echo [32m✓ Port 8000 is available[0m
    echo [Port 8000: OK] >> "%LOG_FILE%"
)

netstat -an | findstr ":8001" >nul
if %ERRORLEVEL% EQU 0 (
    echo [33m⚠ Port 8001 is already in use[0m
    echo   → Change the port in the batch file or stop the service using this port
    echo [Port 8001: IN USE] >> "%LOG_FILE%"
) else (
    echo [32m✓ Port 8001 is available[0m
    echo [Port 8001: OK] >> "%LOG_FILE%"
)

:: Display summary
echo.
echo ===================================================
echo                 Troubleshooting Summary
echo ===================================================
echo.
echo A detailed log has been saved to:
echo %LOG_FILE%
echo.
echo Common issues and solutions:
echo.
echo 1. Cookie extraction fails:
echo   → Make sure you're logged into the service in your browser
echo   → Try closing all browser windows before running the script
echo   → Check if your browser is supported (Chrome, Firefox, Edge)
echo.
echo 2. Server fails to start:
echo   → Check if the port is already in use
echo   → Make sure all required packages are installed
echo   → Check the log file for detailed error messages
echo.
echo 3. Authentication issues:
echo   → Make sure your cookies are valid (you're logged in)
echo   → For GitHub Copilot, ensure you have an active subscription
echo   → For Claude, ensure you have access to the service
echo.
echo 4. Connection issues:
echo   → Check your internet connection
echo   → Check if the service is down or blocked by your network
echo   → Try using a VPN if the service is region-restricted
echo.
echo ===================================================
echo.
echo Press any key to exit...
pause >nul
endlocal

