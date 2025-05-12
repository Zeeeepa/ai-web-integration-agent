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

