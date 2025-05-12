"""
CLI commands for BrokeDev integration.
"""
import click
import logging
import os
import sys
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

@click.group(name="brokedev")
def brokedev_cli():
    """BrokeDev integration commands."""
    pass

@brokedev_cli.command(name="extract-cookies")
@click.option("--browser", type=click.Choice(["chrome", "firefox", "edge", "safari"]), 
              required=True, help="Browser to extract cookies from")
@click.option("--domain", type=str, required=True, 
              help="Domain to extract cookies for")
@click.option("--output", type=str, default=None, 
              help="Output file path (JSON format)")
def extract_cookies(browser: str, domain: str, output: Optional[str]):
    """Extract cookies from a browser."""
    try:
        from freeloader.brokedev.integration.bridge import BrokeDevBridge
        
        click.echo(f"Extracting cookies for {domain} from {browser}...")
        
        bridge = BrokeDevBridge()
        cookies = bridge.extract_cookies(browser=browser, domain=domain)
        
        if cookies:
            click.echo(f"Successfully extracted {len(cookies)} cookies")
            
            if output:
                import json
                with open(output, 'w') as f:
                    json.dump(cookies, f, indent=2)
                click.echo(f"Cookies saved to {output}")
            else:
                import json
                click.echo(json.dumps(cookies, indent=2))
        else:
            click.echo("No cookies extracted")
    
    except Exception as e:
        logger.error(f"Error extracting cookies: {str(e)}")
        sys.exit(1)

@brokedev_cli.command(name="launch-browser")
@click.option("--url", type=str, required=True, 
              help="URL to open")
@click.option("--headless/--no-headless", default=False, 
              help="Run in headless mode")
def launch_browser(url: str, headless: bool):
    """Launch a browser using BrokeDev."""
    try:
        from freeloader.brokedev.integration.bridge import BrokeDevBridge
        
        click.echo(f"Launching browser for {url}...")
        
        bridge = BrokeDevBridge()
        success = bridge.launch_browser(url=url, headless=headless)
        
        if success:
            click.echo("Browser launched successfully")
        else:
            click.echo("Failed to launch browser")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error launching browser: {str(e)}")
        sys.exit(1)

@brokedev_cli.command(name="config")
@click.option("--get", type=str, default=None, 
              help="Get a configuration value")
@click.option("--set", type=str, default=None, 
              help="Set a configuration value (format: key=value)")
@click.option("--config-path", type=str, default=None, 
              help="Path to the configuration file")
def config(get: Optional[str], set: Optional[str], config_path: Optional[str]):
    """Manage BrokeDev configuration."""
    try:
        from freeloader.brokedev.integration.config import BrokeDevConfig
        
        config = BrokeDevConfig(config_path=config_path)
        
        if get:
            value = config.get(get)
            click.echo(f"{get} = {value}")
        
        elif set:
            if '=' not in set:
                click.echo("Invalid format for --set. Use key=value")
                sys.exit(1)
            
            key, value = set.split('=', 1)
            
            # Try to convert value to appropriate type
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            
            config.set(key, value)
            click.echo(f"Set {key} = {value}")
        
        else:
            # Print all configuration
            import yaml
            click.echo(yaml.dump(config.config_data, default_flow_style=False))
    
    except Exception as e:
        logger.error(f"Error managing configuration: {str(e)}")
        sys.exit(1)

