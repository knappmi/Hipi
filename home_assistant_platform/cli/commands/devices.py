"""Device management commands"""

import click
from typing import Optional
from home_assistant_platform.cli.commands.base import get_client, format_json


@click.group()
def devices_group():
    """Device management commands"""
    pass


@devices_group.command('list')
@click.option('--format', 'output_format', type=click.Choice(['json', 'table']), default='table', help='Output format')
@click.pass_context
def list_devices(ctx, output_format):
    """List all devices"""
    client = get_client(ctx)
    devices = client.get('devices')
    
    if output_format == 'json':
        click.echo(format_json(devices))
    else:
        if not devices:
            click.echo("No devices found")
            return
        
        click.echo("\nDevices:")
        click.echo("-" * 80)
        for device in devices:
            state = device.get('state', 'unknown')
            name = device.get('name', 'Unknown')
            device_id = device.get('id', 'N/A')
            device_type = device.get('device_type', 'unknown')
            click.echo(f"  {name} ({device_id})")
            click.echo(f"    Type: {device_type}")
            click.echo(f"    State: {state}")
            if 'brightness' in device:
                click.echo(f"    Brightness: {device['brightness']}%")
            click.echo()


@devices_group.command('get')
@click.argument('device_id')
@click.pass_context
def get_device(ctx, device_id):
    """Get device details"""
    client = get_client(ctx)
    device = client.get(f'devices/{device_id}')
    click.echo(format_json(device))


@devices_group.command('turn-on')
@click.argument('device_id')
@click.option('--brightness', type=int, help='Brightness level (0-100)')
@click.pass_context
def turn_on(ctx, device_id, brightness):
    """Turn on a device"""
    client = get_client(ctx)
    data = {}
    if brightness is not None:
        data['brightness'] = brightness
    
    result = client.post(f'devices/{device_id}/control', json_data={'action': 'turn_on', **data})
    click.echo(f"✓ Turned on {device_id}")
    if brightness:
        click.echo(f"  Brightness set to {brightness}%")


@devices_group.command('turn-off')
@click.argument('device_id')
@click.pass_context
def turn_off(ctx, device_id):
    """Turn off a device"""
    client = get_client(ctx)
    result = client.post(f'devices/{device_id}/control', json_data={'action': 'turn_off'})
    click.echo(f"✓ Turned off {device_id}")


@devices_group.command('set-brightness')
@click.argument('device_id')
@click.argument('brightness', type=click.IntRange(0, 100))
@click.pass_context
def set_brightness(ctx, device_id, brightness):
    """Set device brightness"""
    client = get_client(ctx)
    result = client.post(f'devices/{device_id}/control', json_data={'action': 'set_brightness', 'brightness': brightness})
    click.echo(f"✓ Set brightness to {brightness}% for {device_id}")


@devices_group.command('discover')
@click.pass_context
def discover_devices(ctx):
    """Discover new devices"""
    client = get_client(ctx)
    click.echo("Discovering devices...")
    result = client.post('devices/discover')
    click.echo(f"✓ Discovery started")
    click.echo(f"  Found {result.get('count', 0)} devices")

