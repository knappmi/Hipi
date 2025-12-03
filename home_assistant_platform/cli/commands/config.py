"""Configuration commands"""

import click
from home_assistant_platform.cli.commands.base import get_client, format_json


@click.group()
def config_group():
    """Configuration commands"""
    pass


@config_group.command('get')
@click.argument('key', required=False)
@click.pass_context
def get_config(ctx, key):
    """Get configuration value(s)"""
    client = get_client(ctx)
    if key:
        # Get specific key (would need API endpoint)
        click.echo(f"Getting config key: {key}")
        click.echo("Not yet implemented")
    else:
        # Get all config
        settings = client.get('settings')
        click.echo(format_json(settings))


@config_group.command('set')
@click.argument('key')
@click.argument('value')
@click.pass_context
def set_config(ctx, key, value):
    """Set configuration value"""
    client = get_client(ctx)
    result = client.post('settings', json_data={key: value})
    click.echo(f"✓ Set {key} = {value}")


@config_group.command('status')
@click.pass_context
def status(ctx):
    """Show platform status"""
    client = get_client(ctx)
    status_data = client.get('status')
    click.echo("\nPlatform Status:")
    click.echo("-" * 40)
    click.echo(f"Status: {status_data.get('status', 'unknown')}")
    click.echo(f"Version: {status_data.get('version', 'unknown')}")
    if 'message' in status_data:
        click.echo(f"Message: {status_data['message']}")

