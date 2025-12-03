"""Scene management commands"""

import click
import json
from pathlib import Path
from home_assistant_platform.cli.commands.base import get_client, format_json


@click.group()
def scenes_group():
    """Scene management commands"""
    pass


@scenes_group.command('list')
@click.option('--format', 'output_format', type=click.Choice(['json', 'table']), default='table', help='Output format')
@click.pass_context
def list_scenes(ctx, output_format):
    """List all scenes"""
    client = get_client(ctx)
    scenes = client.get('scenes/scenes')
    
    if output_format == 'json':
        click.echo(format_json(scenes))
    else:
        if not scenes:
            click.echo("No scenes found")
            return
        
        click.echo("\nScenes:")
        click.echo("-" * 80)
        for scene in scenes:
            name = scene.get('name', 'Unknown')
            scene_id = scene.get('id', 'N/A')
            device_count = len(scene.get('device_states', []))
            click.echo(f"  {name} ({scene_id})")
            click.echo(f"    Devices: {device_count}")
            if 'description' in scene:
                click.echo(f"    Description: {scene['description']}")
            click.echo()


@scenes_group.command('create')
@click.option('--file', 'file_path', type=click.Path(exists=True), help='JSON file with scene definition')
@click.option('--name', help='Scene name')
@click.option('--devices', help='JSON array of device states')
@click.pass_context
def create_scene(ctx, file_path, name, devices):
    """Create a new scene"""
    client = get_client(ctx)
    
    if file_path:
        with open(file_path, 'r') as f:
            scene_data = json.load(f)
    else:
        if not name:
            raise click.ClickException("Either --file or --name must be provided")
        device_states = []
        if devices:
            device_states = json.loads(devices)
        scene_data = {
            'name': name,
            'device_states': device_states
        }
    
    result = client.post('scenes/scenes', json_data=scene_data)
    click.echo(f"✓ Created scene: {result.get('name', 'Unknown')}")


@scenes_group.command('activate')
@click.argument('scene_id', type=int)
@click.pass_context
def activate_scene(ctx, scene_id):
    """Activate a scene"""
    client = get_client(ctx)
    result = client.post(f'scenes/scenes/{scene_id}/activate')
    click.echo(f"✓ Activated scene {scene_id}")


@scenes_group.command('get')
@click.argument('scene_id', type=int)
@click.pass_context
def get_scene(ctx, scene_id):
    """Get scene details"""
    client = get_client(ctx)
    scene = client.get(f'scenes/scenes/{scene_id}')
    click.echo(format_json(scene))

