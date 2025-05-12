"""
OpenAI API adapter implementation for web-based AI services.
"""
import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from flask import Flask, request, jsonify, Response, stream_with_context
import threading
import time

# Configure logging
logger = logging.getLogger(__name__)

class OpenAIAdapter:
    """
    Adapter that converts web-based AI service interactions to OpenAI API format.
    Can be configured to use either ai-gateway or chatgpt-adapter as the backend.
    """
    
    def __init__(self, 
                 backend: str = "ai-gateway", 
                 backend_url: Optional[str] = None,
                 host: str = "127.0.0.1", 
                 port: int = 8000,
                 cookie_manager = None):
        """
        Initialize the OpenAI API adapter.
        
        Args:
            backend: The backend to use ('ai-gateway' or 'chatgpt-adapter')
            backend_url: URL of the backend service (if None, uses default)
            host: Host to bind the server to
            port: Port to bind the server to
            cookie_manager: Optional cookie manager for authentication
        """
        self.backend = backend
        self.backend_url = backend_url
        self.host = host
        self.port = port
        self.cookie_manager = cookie_manager
        self.app = Flask(__name__)
        self.setup_routes()
        
        # Set default backend URLs if not provided
        if not self.backend_url:
            if self.backend == "ai-gateway":
                self.backend_url = "http://localhost:8080"
            else:  # chatgpt-adapter
                self.backend_url = "http://localhost:8081"
    
    def setup_routes(self):
        """Set up the Flask routes for the OpenAI API."""
        
        @self.app.route('/v1/models', methods=['GET'])
        def list_models():
            """List available models."""
            models = self._get_available_models()
            return jsonify({"object": "list", "data": models})
        
        @self.app.route('/v1/chat/completions', methods=['POST'])
        def chat_completions():
            """Handle chat completions endpoint."""
            try:
                data = request.json
                stream = data.get('stream', False)
                
                if stream:
                    return Response(
                        stream_with_context(self._stream_response(data)),
                        content_type='text/event-stream'
                    )
                else:
                    response = self._process_completion_request(data)
                    return jsonify(response)
            
            except Exception as e:
                logger.error(f"Error in chat completions: {str(e)}")
                return jsonify({
                    "error": {
                        "message": str(e),
                        "type": "server_error",
                        "code": 500
                    }
                }), 500
        
        @self.app.route('/v1/embeddings', methods=['POST'])
        def embeddings():
            """Handle embeddings endpoint."""
            try:
                data = request.json
                response = self._process_embedding_request(data)
                return jsonify(response)
            
            except Exception as e:
                logger.error(f"Error in embeddings: {str(e)}")
                return jsonify({
                    "error": {
                        "message": str(e),
                        "type": "server_error",
                        "code": 500
                    }
                }), 500
    
    def _get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models based on the backend."""
        # This is a simplified implementation
        if self.backend == "ai-gateway":
            # ai-gateway typically supports these models
            return [
                {"id": "gpt-3.5-turbo", "object": "model", "created": int(time.time()), "owned_by": "openai"},
                {"id": "gpt-4", "object": "model", "created": int(time.time()), "owned_by": "openai"},
                {"id": "claude-3-opus", "object": "model", "created": int(time.time()), "owned_by": "anthropic"},
                {"id": "claude-3-sonnet", "object": "model", "created": int(time.time()), "owned_by": "anthropic"},
                {"id": "gemini-pro", "object": "model", "created": int(time.time()), "owned_by": "google"}
            ]
        else:  # chatgpt-adapter
            # chatgpt-adapter typically supports these models
            return [
                {"id": "gpt-3.5-turbo", "object": "model", "created": int(time.time()), "owned_by": "openai"},
                {"id": "gpt-4", "object": "model", "created": int(time.time()), "owned_by": "openai"},
                {"id": "claude-3", "object": "model", "created": int(time.time()), "owned_by": "anthropic"},
                {"id": "coze", "object": "model", "created": int(time.time()), "owned_by": "coze"},
                {"id": "deepseek", "object": "model", "created": int(time.time()), "owned_by": "deepseek"},
                {"id": "cursor", "object": "model", "created": int(time.time()), "owned_by": "cursor"},
                {"id": "windsurf", "object": "model", "created": int(time.time()), "owned_by": "windsurf"},
                {"id": "qodo", "object": "model", "created": int(time.time()), "owned_by": "qodo"},
                {"id": "blackbox", "object": "model", "created": int(time.time()), "owned_by": "blackbox"},
                {"id": "you", "object": "model", "created": int(time.time()), "owned_by": "you.com"},
                {"id": "grok", "object": "model", "created": int(time.time()), "owned_by": "xai"},
                {"id": "bing", "object": "model", "created": int(time.time()), "owned_by": "microsoft"}
            ]
    
    def _process_completion_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a chat completion request.
        
        Args:
            data: The request data in OpenAI API format
            
        Returns:
            Response in OpenAI API format
        """
        model = data.get('model', 'gpt-3.5-turbo')
        messages = data.get('messages', [])
        
        # Handle different backends
        if self.backend == "ai-gateway":
            return self._process_with_ai_gateway(model, messages, data)
        else:  # chatgpt-adapter
            return self._process_with_chatgpt_adapter(model, messages, data)
    
    def _process_with_ai_gateway(self, model: str, messages: List[Dict[str, Any]], 
                                data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request using ai-gateway backend."""
        # ai-gateway already uses OpenAI API format, so we can forward the request directly
        headers = {'Content-Type': 'application/json'}
        
        # Add authentication if cookie manager is available
        if self.cookie_manager:
            cookies = self.cookie_manager.get_cookies_for_domain(self._extract_domain(self.backend_url))
            if cookies:
                headers['Cookie'] = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
        
        response = requests.post(
            f"{self.backend_url}/v1/chat/completions",
            json=data,
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Error from ai-gateway: {response.text}")
            raise Exception(f"Backend error: {response.status_code}")
        
        return response.json()
    
    def _process_with_chatgpt_adapter(self, model: str, messages: List[Dict[str, Any]], 
                                     data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request using chatgpt-adapter backend."""
        # chatgpt-adapter also uses OpenAI API format, so we can forward the request directly
        headers = {'Content-Type': 'application/json'}
        
        # Add authentication if cookie manager is available
        if self.cookie_manager:
            cookies = self.cookie_manager.get_cookies_for_domain(self._extract_domain(self.backend_url))
            if cookies:
                headers['Cookie'] = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
        
        # Map model names if needed
        mapped_model = self._map_model_for_chatgpt_adapter(model)
        data['model'] = mapped_model
        
        response = requests.post(
            f"{self.backend_url}/v1/chat/completions",
            json=data,
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Error from chatgpt-adapter: {response.text}")
            raise Exception(f"Backend error: {response.status_code}")
        
        return response.json()
    
    def _map_model_for_chatgpt_adapter(self, model: str) -> str:
        """Map OpenAI model names to chatgpt-adapter model names if needed."""
        # This mapping depends on the specific implementation of chatgpt-adapter
        # For now, we'll use a simple mapping
        model_mapping = {
            "gpt-3.5-turbo": "gpt-3.5-turbo",
            "gpt-4": "gpt-4",
            "claude-3-opus": "claude-3",
            "claude-3-sonnet": "claude-3",
            # Add more mappings as needed
        }
        return model_mapping.get(model, model)
    
    def _stream_response(self, data: Dict[str, Any]):
        """
        Stream response for chat completions.
        
        Args:
            data: The request data
            
        Yields:
            Streaming response in OpenAI API format
        """
        model = data.get('model', 'gpt-3.5-turbo')
        messages = data.get('messages', [])
        
        # Prepare the request for streaming
        data['stream'] = True
        
        headers = {'Content-Type': 'application/json'}
        
        # Add authentication if cookie manager is available
        if self.cookie_manager:
            domain = self._extract_domain(self.backend_url)
            cookies = self.cookie_manager.get_cookies_for_domain(domain) if domain else []
            if cookies:
                headers['Cookie'] = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
        
        # Handle different backends
        if self.backend == "ai-gateway":
            url = f"{self.backend_url}/v1/chat/completions"
        else:  # chatgpt-adapter
            url = f"{self.backend_url}/v1/chat/completions"
            # Map model names if needed
            data['model'] = self._map_model_for_chatgpt_adapter(model)
        
        # Make the streaming request
        with requests.post(url, json=data, headers=headers, stream=True) as response:
            if response.status_code != 200:
                logger.error(f"Error from backend: {response.text}")
                yield f"data: {json.dumps({'error': {'message': f'Backend error: {response.status_code}'}})}\n\n"
                return
            
            # Forward the streaming response
            for line in response.iter_lines():
                if line:
                    yield f"{line.decode('utf-8')}\n\n"
    
    def _process_embedding_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an embedding request.
        
        Args:
            data: The request data in OpenAI API format
            
        Returns:
            Response in OpenAI API format
        """
        # Handle different backends
        if self.backend == "ai-gateway":
            headers = {'Content-Type': 'application/json'}
            
            # Add authentication if cookie manager is available
            if self.cookie_manager:
                cookies = self.cookie_manager.get_cookies_for_domain(self._extract_domain(self.backend_url))
                if cookies:
                    headers['Cookie'] = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
            
            response = requests.post(
                f"{self.backend_url}/v1/embeddings",
                json=data,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error from ai-gateway: {response.text}")
                raise Exception(f"Backend error: {response.status_code}")
            
            return response.json()
        else:
            # chatgpt-adapter might not support embeddings
            # Return a mock response for now
            return {
                "object": "list",
                "data": [
                    {
                        "object": "embedding",
                        "embedding": [0.0] * 1536,  # Mock embedding vector
                        "index": 0
                    }
                ],
                "model": data.get("model", "text-embedding-ada-002"),
                "usage": {
                    "prompt_tokens": 0,
                    "total_tokens": 0
                }
            }
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception as e:
            logger.error(f"Error extracting domain: {str(e)}")
            return None
    
    def start(self, debug: bool = False, threaded: bool = False):
        """
        Start the OpenAI API adapter server.
        
        Args:
            debug: Whether to run in debug mode
            threaded: Whether to run in a separate thread
        """
        if threaded:
            thread = threading.Thread(target=self.app.run, 
                                     kwargs={'host': self.host, 'port': self.port, 'debug': debug})
            thread.daemon = True
            thread.start()
            return thread
        else:
            self.app.run(host=self.host, port=self.port, debug=debug)

