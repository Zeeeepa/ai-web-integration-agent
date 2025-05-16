@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo Cookie Extraction and API Setup Utility
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    goto :end
)

REM Create directory for cookies if it doesn't exist
echo Creating cookie directory...
mkdir "%USERPROFILE%\.freeloader" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Cookie directory created.
) else (
    echo [OK] Cookie directory already exists.
)

REM Check for Chrome installation
echo Checking for Chrome installation...
if exist "%LOCALAPPDATA%\Google\Chrome\User Data" (
    echo [OK] Chrome installation found.
) else (
    echo [WARNING] Chrome installation not found in standard location.
    echo If Chrome is installed in a custom location, the cookie extraction might fail.
)

REM Check for required packages
echo Checking for required packages...
pip show openai >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing OpenAI client...
    pip install openai
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install OpenAI client.
        goto :end
    ) else (
        echo [OK] OpenAI client installed.
    )
) else (
    echo [OK] OpenAI client already installed.
)

REM Check for ai-gateway and chatgpt-adapter repositories
echo Checking for backend repositories...
set GATEWAY_FOUND=0
set ADAPTER_FOUND=0

if exist "..\ai-gateway" (
    set GATEWAY_FOUND=1
    echo [OK] ai-gateway repository found.
) else (
    echo [WARNING] ai-gateway repository not found in parent directory.
    echo You may need to clone it from https://github.com/Zeeeepa/ai-gateway
)

if exist "..\chatgpt-adapter" (
    set ADAPTER_FOUND=1
    echo [OK] chatgpt-adapter repository found.
) else (
    echo [WARNING] chatgpt-adapter repository not found in parent directory.
    echo You may need to clone it from https://github.com/Zeeeepa/chatgpt-adapter
)

echo.
echo ===================================================
echo Cookie Extraction Options
echo ===================================================
echo.
echo 1. Try Chrome cookie extraction (standard method)
echo 2. Try Chrome cookie extraction (alternative method)
echo 3. Try Firefox cookie extraction
echo 4. Try Edge cookie extraction
echo 5. Manual cookie entry
echo 6. Exit
echo.

set /p CHOICE=Enter your choice (1-6): 

if "%CHOICE%"=="1" (
    call :extract_chrome_standard
) else if "%CHOICE%"=="2" (
    call :extract_chrome_alternative
) else if "%CHOICE%"=="3" (
    call :extract_firefox
) else if "%CHOICE%"=="4" (
    call :extract_edge
) else if "%CHOICE%"=="5" (
    call :manual_cookie_entry
) else if "%CHOICE%"=="6" (
    goto :end
) else (
    echo Invalid choice. Please try again.
    goto :end
)

echo.
echo ===================================================
echo Start OpenAI API Adapter
echo ===================================================
echo.
echo 1. Start OpenAI API adapter for Claude (ai-gateway backend)
echo 2. Start OpenAI API adapter for GitHub Copilot (chatgpt-adapter backend)
echo 3. Exit
echo.

set /p API_CHOICE=Enter your choice (1-3): 

if "%API_CHOICE%"=="1" (
    call :start_claude_api
) else if "%API_CHOICE%"=="2" (
    call :start_copilot_api
) else if "%API_CHOICE%"=="3" (
    goto :end
) else (
    echo Invalid choice. Please try again.
    goto :end
)

goto :end

:extract_chrome_standard
echo.
echo Extracting cookies from Chrome (standard method)...
echo.
echo Select domain:
echo 1. claude.ai
echo 2. github.com
echo 3. Other (specify)
echo.
set /p DOMAIN_CHOICE=Enter your choice (1-3): 

if "%DOMAIN_CHOICE%"=="1" (
    set DOMAIN=claude.ai
) else if "%DOMAIN_CHOICE%"=="2" (
    set DOMAIN=github.com
) else if "%DOMAIN_CHOICE%"=="3" (
    set /p DOMAIN=Enter domain (e.g., example.com): 
) else (
    echo Invalid choice. Using github.com as default.
    set DOMAIN=github.com
)

echo Importing cookies for %DOMAIN% from Chrome...
python freeloader_cli_main.py openai import-cookies --browser chrome --domain %DOMAIN%
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Standard method failed. Try alternative method.
) else (
    echo [OK] Cookies imported successfully.
)
goto :eof

:extract_chrome_alternative
echo.
echo Extracting cookies from Chrome (alternative method)...
echo.
echo This method uses a direct approach to extract cookies from Chrome's database.
echo.
echo Select domain:
echo 1. claude.ai
echo 2. github.com
echo 3. Other (specify)
echo.
set /p DOMAIN_CHOICE=Enter your choice (1-3): 

if "%DOMAIN_CHOICE%"=="1" (
    set DOMAIN=claude.ai
) else if "%DOMAIN_CHOICE%"=="2" (
    set DOMAIN=github.com
) else if "%DOMAIN_CHOICE%"=="3" (
    set /p DOMAIN=Enter domain (e.g., example.com): 
) else (
    echo Invalid choice. Using github.com as default.
    set DOMAIN=github.com
)

REM Create a temporary Python script to extract cookies directly
echo import os, json, sqlite3, shutil, datetime, sys > extract_cookies.py
echo from pathlib import Path >> extract_cookies.py
echo. >> extract_cookies.py
echo # Domain to extract cookies for >> extract_cookies.py
echo domain = "%DOMAIN%" >> extract_cookies.py
echo. >> extract_cookies.py
echo # Path to Chrome cookies database >> extract_cookies.py
echo chrome_path = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data", "Default", "Network", "Cookies") >> extract_cookies.py
echo. >> extract_cookies.py
echo # Create a copy of the database (Chrome locks the original) >> extract_cookies.py
echo temp_path = os.path.join(os.environ["TEMP"], "chrome_cookies_temp.db") >> extract_cookies.py
echo. >> extract_cookies.py
echo try: >> extract_cookies.py
echo     # Make a copy of the database >> extract_cookies.py
echo     shutil.copy2(chrome_path, temp_path) >> extract_cookies.py
echo     print(f"[OK] Copied Chrome cookies database to temporary location") >> extract_cookies.py
echo. >> extract_cookies.py
echo     # Connect to the database copy >> extract_cookies.py
echo     conn = sqlite3.connect(temp_path) >> extract_cookies.py
echo     cursor = conn.cursor() >> extract_cookies.py
echo. >> extract_cookies.py
echo     # Query for cookies matching the domain >> extract_cookies.py
echo     cursor.execute( >> extract_cookies.py
echo         "SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly " >> extract_cookies.py
echo         "FROM cookies WHERE host_key LIKE ? OR host_key LIKE ?", >> extract_cookies.py
echo         (f"%{domain}", f"%.{domain}") >> extract_cookies.py
echo     ) >> extract_cookies.py
echo. >> extract_cookies.py
echo     cookies = cursor.fetchall() >> extract_cookies.py
echo     conn.close() >> extract_cookies.py
echo. >> extract_cookies.py
echo     if not cookies: >> extract_cookies.py
echo         print(f"[WARNING] No cookies found for {domain} in Chrome") >> extract_cookies.py
echo         sys.exit(1) >> extract_cookies.py
echo. >> extract_cookies.py
echo     # Format cookies for the freeloader format >> extract_cookies.py
echo     cookie_dict = {} >> extract_cookies.py
echo     for name, value, host_key, path, expires_utc, is_secure, is_httponly in cookies: >> extract_cookies.py
echo         # Convert Chrome's weird timestamp to a normal one >> extract_cookies.py
echo         # Chrome stores timestamps as microseconds since Jan 1, 1601 >> extract_cookies.py
echo         chrome_epoch = datetime.datetime(1601, 1, 1) >> extract_cookies.py
echo         expires = chrome_epoch + datetime.timedelta(microseconds=expires_utc) >> extract_cookies.py
echo         unix_timestamp = int((expires - datetime.datetime(1970, 1, 1)).total_seconds()) >> extract_cookies.py
echo. >> extract_cookies.py
echo         cookie = { >> extract_cookies.py
echo             "name": name, >> extract_cookies.py
echo             "value": value, >> extract_cookies.py
echo             "domain": host_key, >> extract_cookies.py
echo             "path": path, >> extract_cookies.py
echo             "expires": unix_timestamp, >> extract_cookies.py
echo             "secure": bool(is_secure), >> extract_cookies.py
echo             "httpOnly": bool(is_httponly) >> extract_cookies.py
echo         } >> extract_cookies.py
echo. >> extract_cookies.py
echo         if domain not in cookie_dict: >> extract_cookies.py
echo             cookie_dict[domain] = [] >> extract_cookies.py
echo         cookie_dict[domain].append(cookie) >> extract_cookies.py
echo. >> extract_cookies.py
echo     # Save to freeloader cookie format >> extract_cookies.py
echo     cookie_file = os.path.join(os.environ["USERPROFILE"], ".freeloader", "cookies.json") >> extract_cookies.py
echo. >> extract_cookies.py
echo     # Load existing cookies if file exists >> extract_cookies.py
echo     if os.path.exists(cookie_file): >> extract_cookies.py
echo         try: >> extract_cookies.py
echo             with open(cookie_file, "r") as f: >> extract_cookies.py
echo                 existing_cookies = json.load(f) >> extract_cookies.py
echo         except json.JSONDecodeError: >> extract_cookies.py
echo             existing_cookies = {} >> extract_cookies.py
echo     else: >> extract_cookies.py
echo         existing_cookies = {} >> extract_cookies.py
echo. >> extract_cookies.py
echo     # Update with new cookies >> extract_cookies.py
echo     existing_cookies.update(cookie_dict) >> extract_cookies.py
echo. >> extract_cookies.py
echo     # Save updated cookies >> extract_cookies.py
echo     with open(cookie_file, "w") as f: >> extract_cookies.py
echo         json.dump(existing_cookies, f) >> extract_cookies.py
echo. >> extract_cookies.py
echo     print(f"[OK] Successfully extracted {len(cookie_dict[domain])} cookies for {domain}") >> extract_cookies.py
echo     print(f"[OK] Cookies saved to {cookie_file}") >> extract_cookies.py
echo. >> extract_cookies.py
echo except Exception as e: >> extract_cookies.py
echo     print(f"[ERROR] {str(e)}") >> extract_cookies.py
echo     sys.exit(1) >> extract_cookies.py
echo finally: >> extract_cookies.py
echo     # Clean up temporary file >> extract_cookies.py
echo     if os.path.exists(temp_path): >> extract_cookies.py
echo         try: >> extract_cookies.py
echo             os.remove(temp_path) >> extract_cookies.py
echo         except: >> extract_cookies.py
echo             pass >> extract_cookies.py

echo Running alternative cookie extraction method...
python extract_cookies.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Alternative method also failed. Try manual cookie entry.
) else (
    echo [OK] Cookies extracted using alternative method.
)

REM Clean up the temporary script
del extract_cookies.py
goto :eof

:extract_firefox
echo.
echo Extracting cookies from Firefox...
echo.
echo Select domain:
echo 1. claude.ai
echo 2. github.com
echo 3. Other (specify)
echo.
set /p DOMAIN_CHOICE=Enter your choice (1-3): 

if "%DOMAIN_CHOICE%"=="1" (
    set DOMAIN=claude.ai
) else if "%DOMAIN_CHOICE%"=="2" (
    set DOMAIN=github.com
) else if "%DOMAIN_CHOICE%"=="3" (
    set /p DOMAIN=Enter domain (e.g., example.com): 
) else (
    echo Invalid choice. Using github.com as default.
    set DOMAIN=github.com
)

echo Importing cookies for %DOMAIN% from Firefox...
python freeloader_cli_main.py openai import-cookies --browser firefox --domain %DOMAIN%
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Firefox cookie extraction failed. Try manual cookie entry.
) else (
    echo [OK] Cookies imported successfully.
)
goto :eof

:extract_edge
echo.
echo Extracting cookies from Edge...
echo.
echo Select domain:
echo 1. claude.ai
echo 2. github.com
echo 3. Other (specify)
echo.
set /p DOMAIN_CHOICE=Enter your choice (1-3): 

if "%DOMAIN_CHOICE%"=="1" (
    set DOMAIN=claude.ai
) else if "%DOMAIN_CHOICE%"=="2" (
    set DOMAIN=github.com
) else if "%DOMAIN_CHOICE%"=="3" (
    set /p DOMAIN=Enter domain (e.g., example.com): 
) else (
    echo Invalid choice. Using github.com as default.
    set DOMAIN=github.com
)

echo Importing cookies for %DOMAIN% from Edge...
python freeloader_cli_main.py openai import-cookies --browser edge --domain %DOMAIN%
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Edge cookie extraction failed. Try manual cookie entry.
) else (
    echo [OK] Cookies imported successfully.
)
goto :eof

:manual_cookie_entry
echo.
echo Manual Cookie Entry
echo.
echo This will help you manually enter cookies from your browser.
echo.
echo Select domain:
echo 1. claude.ai
echo 2. github.com
echo 3. Other (specify)
echo.
set /p DOMAIN_CHOICE=Enter your choice (1-3): 

if "%DOMAIN_CHOICE%"=="1" (
    set DOMAIN=claude.ai
) else if "%DOMAIN_CHOICE%"=="2" (
    set DOMAIN=github.com
) else if "%DOMAIN_CHOICE%"=="3" (
    set /p DOMAIN=Enter domain (e.g., example.com): 
) else (
    echo Invalid choice. Using github.com as default.
    set DOMAIN=github.com
)

echo.
echo To get cookies manually:
echo 1. Open your browser and go to %DOMAIN%
echo 2. Log in if you haven't already
echo 3. Open Developer Tools (F12 or right-click and select "Inspect")
echo 4. Go to the "Application" tab (Chrome/Edge) or "Storage" tab (Firefox)
echo 5. Select "Cookies" in the left sidebar and click on the domain
echo.
echo Now we'll create a cookie file with the essential cookies.
echo.

REM Create a temporary Python script for manual cookie entry
echo import os, json, sys > manual_cookies.py
echo from pathlib import Path >> manual_cookies.py
echo. >> manual_cookies.py
echo # Domain to create cookies for >> manual_cookies.py
echo domain = "%DOMAIN%" >> manual_cookies.py
echo. >> manual_cookies.py
echo cookie_file = os.path.join(os.environ["USERPROFILE"], ".freeloader", "cookies.json") >> manual_cookies.py
echo. >> manual_cookies.py
echo # Load existing cookies if file exists >> manual_cookies.py
echo if os.path.exists(cookie_file): >> manual_cookies.py
echo     try: >> manual_cookies.py
echo         with open(cookie_file, "r") as f: >> manual_cookies.py
echo             existing_cookies = json.load(f) >> manual_cookies.py
echo     except json.JSONDecodeError: >> manual_cookies.py
echo         existing_cookies = {} >> manual_cookies.py
echo else: >> manual_cookies.py
echo     existing_cookies = {} >> manual_cookies.py
echo. >> manual_cookies.py
echo # Initialize domain in cookie dict if not exists >> manual_cookies.py
echo if domain not in existing_cookies: >> manual_cookies.py
echo     existing_cookies[domain] = [] >> manual_cookies.py
echo. >> manual_cookies.py
echo print(f"Manual cookie entry for {domain}") >> manual_cookies.py
echo print("Enter 'done' when finished adding cookies") >> manual_cookies.py
echo. >> manual_cookies.py
echo cookie_count = 0 >> manual_cookies.py
echo while True: >> manual_cookies.py
echo     print("\nEnter cookie details (or 'done' to finish):") >> manual_cookies.py
echo     name_input = input("Cookie Name: ").strip() >> manual_cookies.py
echo     if name_input.lower() == 'done': >> manual_cookies.py
echo         break >> manual_cookies.py
echo. >> manual_cookies.py
echo     value = input("Cookie Value: ").strip() >> manual_cookies.py
echo     path = input("Path (default is /): ").strip() or "/" >> manual_cookies.py
echo     secure = input("Secure (y/n, default is y): ").strip().lower() != 'n' >> manual_cookies.py
echo     httponly = input("HttpOnly (y/n, default is y): ").strip().lower() != 'n' >> manual_cookies.py
echo. >> manual_cookies.py
echo     # Create cookie object >> manual_cookies.py
echo     cookie = { >> manual_cookies.py
echo         "name": name_input, >> manual_cookies.py
echo         "value": value, >> manual_cookies.py
echo         "domain": f".{domain}" if not domain.startswith('.') else domain, >> manual_cookies.py
echo         "path": path, >> manual_cookies.py
echo         "expires": 1893456000,  # Some date in the future (2030) >> manual_cookies.py
echo         "secure": secure, >> manual_cookies.py
echo         "httpOnly": httponly >> manual_cookies.py
echo     } >> manual_cookies.py
echo. >> manual_cookies.py
echo     # Add to cookies list >> manual_cookies.py
echo     existing_cookies[domain].append(cookie) >> manual_cookies.py
echo     cookie_count += 1 >> manual_cookies.py
echo     print(f"Added cookie: {name_input}") >> manual_cookies.py
echo. >> manual_cookies.py
echo if cookie_count == 0: >> manual_cookies.py
echo     print("No cookies were added.") >> manual_cookies.py
echo     sys.exit(1) >> manual_cookies.py
echo. >> manual_cookies.py
echo # Save updated cookies >> manual_cookies.py
echo with open(cookie_file, "w") as f: >> manual_cookies.py
echo     json.dump(existing_cookies, f) >> manual_cookies.py
echo. >> manual_cookies.py
echo print(f"[OK] Successfully added {cookie_count} cookies for {domain}") >> manual_cookies.py
echo print(f"[OK] Cookies saved to {cookie_file}") >> manual_cookies.py

echo Running manual cookie entry script...
python manual_cookies.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Manual cookie entry failed.
) else (
    echo [OK] Cookies added manually.
)

REM Clean up the temporary script
del manual_cookies.py
goto :eof

:start_claude_api
echo.
echo Starting OpenAI API adapter for Claude (ai-gateway backend)...
echo.

REM Check if ai-gateway is running
curl -s http://localhost:8080 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] ai-gateway is not running at http://localhost:8080
    
    if %GATEWAY_FOUND% EQU 1 (
        echo Would you like to start ai-gateway? (y/n)
        set /p START_GATEWAY=
        
        if /i "%START_GATEWAY%"=="y" (
            echo Starting ai-gateway in a new window...
            start cmd /k "cd ..\ai-gateway && cargo run --release"
            echo Waiting for ai-gateway to start (10 seconds)...
            timeout /t 10 /nobreak >nul
        )
    ) else (
        echo ai-gateway repository not found. Please clone it first.
    )
) else (
    echo [OK] ai-gateway is running at http://localhost:8080
)

echo Starting OpenAI API adapter for Claude...
start cmd /k "python freeloader_cli_main.py openai start --backend ai-gateway --port 8000 --host 127.0.0.1"

echo.
echo Claude OpenAI API endpoint should now be running!
echo.
echo Base URL: http://127.0.0.1:8000/v1
echo.
echo Available endpoints:
echo   - GET  /v1/models
echo   - POST /v1/chat/completions
echo   - POST /v1/embeddings
echo.
echo To test the API, run:
echo python examples/test_openai_adapter_debug.py
echo.
goto :eof

:start_copilot_api
echo.
echo Starting OpenAI API adapter for GitHub Copilot (chatgpt-adapter backend)...
echo.

REM Check if chatgpt-adapter is running
curl -s http://localhost:8081 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] chatgpt-adapter is not running at http://localhost:8081
    
    if %ADAPTER_FOUND% EQU 1 (
        echo Would you like to start chatgpt-adapter? (y/n)
        set /p START_ADAPTER=
        
        if /i "%START_ADAPTER%"=="y" (
            echo Starting chatgpt-adapter in a new window...
            start cmd /k "cd ..\chatgpt-adapter && npm start"
            echo Waiting for chatgpt-adapter to start (10 seconds)...
            timeout /t 10 /nobreak >nul
        )
    ) else (
        echo chatgpt-adapter repository not found. Please clone it first.
    )
) else (
    echo [OK] chatgpt-adapter is running at http://localhost:8081
)

echo Starting OpenAI API adapter for GitHub Copilot...
start cmd /k "python freeloader_cli_main.py openai start --backend chatgpt-adapter --port 8001 --host 127.0.0.1"

echo.
echo GitHub Copilot OpenAI API endpoint should now be running!
echo.
echo Base URL: http://127.0.0.1:8001/v1
echo.
echo Available endpoints:
echo   - GET  /v1/models
echo   - POST /v1/chat/completions
echo.
echo To test the API, run:
echo python examples/test_openai_adapter_debug.py
echo.
goto :eof

:end
echo.
echo ===================================================
echo Process completed
echo ===================================================
echo.
endlocal

