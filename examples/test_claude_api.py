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

