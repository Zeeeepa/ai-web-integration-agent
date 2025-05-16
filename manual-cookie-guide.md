# Manual Cookie Extraction Guide

This guide will help you manually extract and set up cookies for the OpenAI API adapter when automatic extraction fails.

## Why Cookies Are Needed

The OpenAI API adapter needs browser cookies to authenticate with web services like Claude.ai or GitHub. These cookies contain your login session information, allowing the adapter to make requests on your behalf.

## Method 1: Using Developer Tools

### For Chrome/Edge:

1. Open Chrome or Edge and navigate to the website (e.g., claude.ai or github.com)
2. Make sure you're logged in
3. Press F12 or right-click and select "Inspect" to open Developer Tools
4. Go to the "Application" tab
5. In the left sidebar, expand "Storage" and click on "Cookies"
6. Click on the domain (e.g., claude.ai)
7. You'll see a list of cookies - look for authentication cookies like:
   - For Claude: `sessionKey`, `intercom-session-*`, etc.
   - For GitHub: `user_session`, `dotcom_user`, etc.
8. For each important cookie, note down:
   - Name
   - Value
   - Domain
   - Path (usually "/")

### For Firefox:

1. Open Firefox and navigate to the website
2. Make sure you're logged in
3. Press F12 or right-click and select "Inspect" to open Developer Tools
4. Go to the "Storage" tab
5. In the left sidebar, expand "Cookies" and click on the domain
6. Note down the important cookies as described above

## Method 2: Using the Manual Cookie Entry Script

1. Run the `cookie-extraction-fix.bat` script
2. Choose option 5 for "Manual cookie entry"
3. Select the domain you want to add cookies for
4. Follow the prompts to enter each cookie's details
5. Enter "done" when you've added all necessary cookies

## Method 3: Directly Editing the Cookie File

1. Open the cookie file located at:
   - Windows: `%USERPROFILE%\.freeloader\cookies.json`
   - macOS/Linux: `~/.freeloader/cookies.json`

2. If the file doesn't exist, create it with this structure:
   ```json
   {
     "claude.ai": [
       {
         "name": "cookie_name",
         "value": "cookie_value",
         "domain": ".claude.ai",
         "path": "/",
         "expires": 1893456000,
         "secure": true,
         "httpOnly": true
       }
     ]
   }
   ```

3. Replace `cookie_name` and `cookie_value` with the actual cookie details
4. Add as many cookies as needed within the array

## Essential Cookies

### For Claude.ai:
- `sessionKey` - Main authentication cookie
- Any cookies starting with `intercom-` or `__cf_`

### For GitHub:
- `user_session` - Main authentication cookie
- `dotcom_user` - Your GitHub username
- `logged_in` - Login status

## Testing Your Cookies

After setting up cookies, test the connection:

1. Run the diagnostic tool:
   ```
   python examples/test_openai_adapter_debug.py
   ```

2. Start the OpenAI API adapter:
   ```
   python freeloader_cli_main.py openai start --backend ai-gateway --port 8000
   ```

3. Test a simple chat completion:
   ```
   curl http://127.0.0.1:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "claude-3-opus-20240229",
       "messages": [
         {"role": "user", "content": "Hello, how are you?"}
       ]
     }'
   ```

## Troubleshooting

- **No cookies found**: Make sure you're logged into the website before extracting cookies
- **Authentication errors**: Some cookies might be missing or expired - try logging out and back in
- **Backend service not running**: Make sure ai-gateway or chatgpt-adapter is running
- **Cookie extraction fails**: Try a different browser or the manual entry method

## Security Note

Cookies contain sensitive authentication information. Never share your cookie file with others, and be cautious when copying cookie values.

