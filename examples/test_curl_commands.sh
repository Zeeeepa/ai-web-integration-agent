#!/bin/bash
# Test script for the OpenAI API adapter

# Base URL for the API
BASE_URL="http://127.0.0.1:8000"

echo "Testing OpenAI API adapter at $BASE_URL"
echo "========================================"

# Test 1: List models
echo -e "\n1. Testing GET /v1/models endpoint:"
curl -s "$BASE_URL/v1/models" | jq .

# Test 2: Chat completions
echo -e "\n2. Testing POST /v1/chat/completions endpoint:"
curl -s "$BASE_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20240229",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "temperature": 0.7,
    "stream": false
  }' | jq .

# Test 3: Streaming chat completions
echo -e "\n3. Testing streaming chat completions:"
echo "curl -s \"$BASE_URL/v1/chat/completions\" -H \"Content-Type: application/json\" -d '{\"model\": \"claude-3-opus-20240229\", \"messages\": [{\"role\": \"system\", \"content\": \"You are a helpful assistant.\"}, {\"role\": \"user\", \"content\": \"Write a short poem about AI.\"}], \"temperature\": 0.7, \"stream\": true}'"
echo "Note: Run this command manually to see streaming output"

# Test 4: Embeddings
echo -e "\n4. Testing POST /v1/embeddings endpoint:"
curl -s "$BASE_URL/v1/embeddings" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-opus-20240229",
    "input": "The quick brown fox jumps over the lazy dog."
  }' | jq .

echo -e "\nAll tests completed!"

