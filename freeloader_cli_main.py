"""
Main CLI entry point for freeloader with BrokeDev integration.
"""
import click
import sys
import logging

# Import all CLI command groups
from freeloader.cli.brokedev_commands import brokedev_cli
from freeloader.openai_adapter.cli import openai_cli
# Import other existing CLI command groups
# from freeloader.cli.claude_commands import claude_cli
# from freeloader.cli.config_commands import config_cli
# etc.

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

@click.group()
@click.version_option(version="0.2.0")
def cli():
    """Freeloader CLI with BrokeDev integration."""
    pass

# Add all command groups
cli.add_command(brokedev_cli)
cli.add_command(openai_cli)
# Add other existing command groups
# cli.add_command(claude_cli)
# cli.add_command(config_cli)
# etc.

if __name__ == "__main__":
    cli()
