"""Main CLI entry point"""

import click
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from home_assistant_platform.cli.commands import devices, automations, scenes, logs, config, plugins


@click.group()
@click.version_option(version="1.0.0")
@click.pass_context
def cli(ctx):
    """Home Assistant Platform CLI - Command-line interface for managing the platform"""
    ctx.ensure_object(dict)
    # Set default API URL
    ctx.obj['api_url'] = 'http://localhost:8000/api/v1'


# Register command groups
cli.add_command(devices.devices_group, name='devices')
cli.add_command(automations.automations_group, name='automations')
cli.add_command(scenes.scenes_group, name='scenes')
cli.add_command(logs.logs_group, name='logs')
cli.add_command(config.config_group, name='config')
cli.add_command(plugins.plugins_group, name='plugins')


if __name__ == '__main__':
    cli()

