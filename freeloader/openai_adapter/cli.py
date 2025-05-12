"""
Command-line interface for the OpenAI API adapter.
"""
import click
import logging
import os
import sys
from typing import Optional

from .adapter import OpenAIAdapter
from .cookie_manager import CookieManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@click.group(name="openai")
def openai_cli():
    """OpenAI API adapter commands."""
    pass

@openai_cli.command(name="start")
@click.option("--backend", type=click.Choice(["ai-gateway", "chatgpt-adapter"]), 
              default="ai-gateway", help="Backend to use")
@click.option("--backend-url", type=str, default=None, 
              help="URL of the backend service")
@click.option("--host", type=str, default="127.0.0.1", 
              help="Host to bind the server to")
@click.option("--port", type=int, default=8000, 
              help="Port to bind the server to")
@click.option("--debug/--no-debug", default=False, 
              help="Run in debug mode")
@click.option("--use-cookies/--no-cookies", default=True, 
              help="Use cookies for authentication")
@click.option("--cookie-store", type=str, default=None, 
              help="Path to the cookie store file")
def start_server(backend: str, backend_url: Optional[str], host: str, port: int, 
                debug: bool, use_cookies: bool, cookie_store: Optional[str]):
    """Start the OpenAI API adapter server."""
    try:
        click.echo(f"Starting OpenAI API adapter with {backend} backend...")
        
        # Initialize cookie manager if needed
        cookie_manager = None
        if use_cookies:
            cookie_manager = CookieManager(cookie_store_path=cookie_store)
            click.echo(f"Using cookie store at {cookie_manager.cookie_store_path}")
        
        # Initialize and start the adapter
        adapter = OpenAIAdapter(
            backend=backend,
            backend_url=backend_url,
            host=host,
            port=port,
            cookie_manager=cookie_manager
        )
        
        click.echo(f"Server running at http://{host}:{port}")
        click.echo("Available endpoints:")
        click.echo("  - GET  /v1/models")
        click.echo("  - POST /v1/chat/completions")
        click.echo("  - POST /v1/embeddings")
        click.echo("Press Ctrl+C to stop the server")
        
        adapter.start(debug=debug)
    
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)

@openai_cli.command(name="import-cookies")
@click.option("--browser", type=click.Choice(["chrome", "firefox", "edge", "safari"]), 
              required=True, help="Browser to import cookies from")
@click.option("--domain", type=str, required=True, 
              help="Domain to import cookies for")
@click.option("--cookie-store", type=str, default=None, 
              help="Path to the cookie store file")
@click.option("--use-brokedev/--no-brokedev", default=True, 
              help="Use BrokeDevBridge for cookie extraction")
def import_cookies(browser: str, domain: str, cookie_store: Optional[str], 
                  use_brokedev: bool):
    """Import cookies from a browser."""
    try:
        click.echo(f"Importing cookies for {domain} from {browser}...")
        
        # Initialize cookie manager
        cookie_manager = CookieManager(cookie_store_path=cookie_store)
        
        # Initialize BrokeDevBridge if needed
        bridge = None
        if use_brokedev:
            try:
                from freeloader.brokedev.integration.bridge import BrokeDevBridge
                bridge = BrokeDevBridge()
                click.echo("Using BrokeDevBridge for cookie extraction")
            except ImportError:
                click.echo("BrokeDevBridge not available, falling back to built-in extraction")
        
        # Import cookies
        cookies = cookie_manager.import_from_browser(browser=browser, domain=domain, bridge=bridge)
        
        if cookies:
            click.echo(f"Successfully imported {len(cookies)} cookies for {domain}")
        else:
            click.echo(f"No cookies imported for {domain}")
    
    except Exception as e:
        logger.error(f"Error importing cookies: {str(e)}")
        sys.exit(1)

@openai_cli.command(name="clear-cookies")
@click.option("--domain", type=str, default=None, 
              help="Domain to clear cookies for, or all if not specified")
@click.option("--cookie-store", type=str, default=None, 
              help="Path to the cookie store file")
def clear_cookies(domain: Optional[str], cookie_store: Optional[str]):
    """Clear cookies."""
    try:
        # Initialize cookie manager
        cookie_manager = CookieManager(cookie_store_path=cookie_store)
        
        # Clear cookies
        cookie_manager.clear_cookies(domain=domain)
        
        if domain:
            click.echo(f"Cleared cookies for {domain}")
        else:
            click.echo("Cleared all cookies")
    
    except Exception as e:
        logger.error(f"Error clearing cookies: {str(e)}")
        sys.exit(1)

