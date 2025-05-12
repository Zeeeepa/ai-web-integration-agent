# Testing the OpenAI API Adapter

This guide will help you test the OpenAI API adapter that you've successfully set up. Based on your console output, your Claude OpenAI API endpoint is running at `http://127.0.0.1:8000`.

## Available Endpoints

As shown in your console output, the following endpoints are available:
- GET `/v1/models` - List available models
- POST `/v1/chat/completions` - Generate chat completions
- POST `/v1/embeddings` - Generate embeddings

## Testing Methods

### 1. Using cURL

#### List Models
```bash
curl http://127.0.0.1:8000/v1/models
```

#### Chat Completions
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20240229",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "temperature": 0.7,
    "stream": false
  }'
```

#### Streaming Chat Completions
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20240229",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Write a short poem about AI."}
    ],
    "temperature": 0.7,
    "stream": true
  }'
```

#### Generate Embeddings
```bash
curl http://127.0.0.1:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20240229",
    "input": "The quick brown fox jumps over the lazy dog."
  }'
```

### 2. Using Python

Create a file named `test_claude_api.py` with the following content:

```python
import openai
import json

# Configure the client to use your local endpoint
client = openai.OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="dummy-key"  # The adapter doesn't check API keys
)

# List models
models = client.models.list()
print("Available models:")
print(json.dumps(models.model_dump(), indent=2))
print("\n" + "-"*50 + "\n")

# Chat completion
chat_completion = client.chat.completions.create(
    model="claude-3-opus-20240229",  # This can be any model name, the adapter will use the configured backend
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the capital of France?"}
    ],
    temperature=0.7,
)
print("Chat completion response:")
print(json.dumps(chat_completion.model_dump(), indent=2))
print("\n" + "-"*50 + "\n")

# Streaming chat completion
print("Streaming chat completion:")
stream = client.chat.completions.create(
    model="claude-3-opus-20240229",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Count from 1 to 5."}
    ],
    temperature=0.7,
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
print("\n\n" + "-"*50 + "\n")

# Embeddings
embedding = client.embeddings.create(
    model="claude-3-opus-20240229",
    input="The quick brown fox jumps over the lazy dog."
)
print("Embedding response:")
print(json.dumps(embedding.model_dump(), indent=2))
```

Run the script:
```bash
python test_claude_api.py
```

### 3. Using JavaScript/Node.js

Create a file named `test_claude_api.js` with the following content:

```javascript
const { OpenAI } = require('openai');

// Configure the client to use your local endpoint
const openai = new OpenAI({
  baseURL: 'http://127.0.0.1:8000/v1',
  apiKey: 'dummy-key', // The adapter doesn't check API keys
});

async function runTests() {
  try {
    // List models
    console.log('Fetching available models...');
    const models = await openai.models.list();
    console.log('Available models:', JSON.stringify(models, null, 2));
    console.log('-'.repeat(50));

    // Chat completion
    console.log('Testing chat completion...');
    const completion = await openai.chat.completions.create({
      model: 'claude-3-opus-20240229', // This can be any model name
      messages: [
        { role: 'system', content: 'You are a helpful assistant.' },
        { role: 'user', content: 'What is the capital of Japan?' },
      ],
      temperature: 0.7,
    });
    console.log('Chat completion response:', JSON.stringify(completion, null, 2));
    console.log('-'.repeat(50));

    // Streaming chat completion
    console.log('Testing streaming chat completion...');
    const stream = await openai.chat.completions.create({
      model: 'claude-3-opus-20240229',
      messages: [
        { role: 'system', content: 'You are a helpful assistant.' },
        { role: 'user', content: 'Write a haiku about programming.' },
      ],
      temperature: 0.7,
      stream: true,
    });

    console.log('Streaming response:');
    let streamedText = '';
    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content || '';
      streamedText += content;
      process.stdout.write(content);
    }
    console.log('\n');
    console.log('-'.repeat(50));

    // Embeddings
    console.log('Testing embeddings...');
    const embedding = await openai.embeddings.create({
      model: 'claude-3-opus-20240229',
      input: 'The quick brown fox jumps over the lazy dog.',
    });
    console.log('Embedding response:', JSON.stringify(embedding, null, 2));

  } catch (error) {
    console.error('Error:', error);
  }
}

runTests();
```

Run the script:
```bash
npm install openai
node test_claude_api.js
```

## Troubleshooting

If you encounter any issues:

1. **Connection Refused**: Make sure the server is running and the port is correct.
2. **Authentication Errors**: The adapter doesn't check API keys, so any value should work.
3. **Model Not Found**: The adapter will use the configured backend regardless of the model name provided.
4. **Cookie Issues**: If you get authentication errors from the backend service, try reimporting cookies:
   ```bash
   python freeloader_cli_main.py openai import-cookies --browser chrome --domain claude.ai
   ```

## Notes

- The adapter translates OpenAI API requests to the appropriate format for the backend service (ai-gateway or chatgpt-adapter).
- For production use, consider using a proper WSGI server as mentioned in the warning message.
- The server is running in debug mode, which is not recommended for production environments.

