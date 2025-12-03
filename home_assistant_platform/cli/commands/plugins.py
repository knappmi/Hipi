"""Plugin management commands"""

import click
from home_assistant_platform.cli.commands.base import get_client, format_json


@click.group()
def plugins_group():
    """Plugin management commands"""
    pass


@plugins_group.command('list')
@click.option('--format', 'output_format', type=click.Choice(['json', 'table']), default='table', help='Output format')
@click.pass_context
def list_plugins(ctx, output_format):
    """List installed plugins"""
    client = get_client(ctx)
    plugins = client.get('plugins')
    
    if output_format == 'json':
        click.echo(format_json(plugins))
    else:
        if not plugins:
            click.echo("No plugins installed")
            return
        
        click.echo("\nPlugins:")
        click.echo("-" * 80)
        for plugin in plugins:
            name = plugin.get('name', 'Unknown')
            plugin_id = plugin.get('id', 'N/A')
            status = plugin.get('status', 'unknown')
            click.echo(f"  {name} ({plugin_id})")
            click.echo(f"    Status: {status}")
            click.echo()


@plugins_group.command('install')
@click.argument('plugin_id')
@click.pass_context
def install_plugin(ctx, plugin_id):
    """Install a plugin"""
    client = get_client(ctx)
    result = client.post(f'plugins/{plugin_id}/install')
    click.echo(f"✓ Installed plugin: {plugin_id}")


@plugins_group.command('uninstall')
@click.argument('plugin_id')
@click.pass_context
def uninstall_plugin(ctx, plugin_id):
    """Uninstall a plugin"""
    client = get_client(ctx)
    result = client.delete(f'plugins/{plugin_id}')
    click.echo(f"✓ Uninstalled plugin: {plugin_id}")


@plugins_group.command('start')
@click.argument('plugin_id')
@click.pass_context
def start_plugin(ctx, plugin_id):
    """Start a plugin"""
    client = get_client(ctx)
    result = client.post(f'plugins/{plugin_id}/start')
    click.echo(f"✓ Started plugin: {plugin_id}")


@plugins_group.command('stop')
@click.argument('plugin_id')
@click.pass_context
def stop_plugin(ctx, plugin_id):
    """Stop a plugin"""
    client = get_client(ctx)
    result = client.post(f'plugins/{plugin_id}/stop')
    click.echo(f"✓ Stopped plugin: {plugin_id}")

