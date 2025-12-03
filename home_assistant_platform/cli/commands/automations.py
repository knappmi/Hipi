"""Automation management commands"""

import click
import json
from pathlib import Path
from home_assistant_platform.cli.commands.base import get_client, format_json


@click.group()
def automations_group():
    """Automation management commands"""
    pass


@automations_group.command('list')
@click.option('--format', 'output_format', type=click.Choice(['json', 'table']), default='table', help='Output format')
@click.pass_context
def list_automations(ctx, output_format):
    """List all automations"""
    client = get_client(ctx)
    automations = client.get('automation/automations')
    
    if output_format == 'json':
        click.echo(format_json(automations))
    else:
        if not automations:
            click.echo("No automations found")
            return
        
        click.echo("\nAutomations:")
        click.echo("-" * 80)
        for automation in automations:
            name = automation.get('name', 'Unknown')
            automation_id = automation.get('id', 'N/A')
            enabled = automation.get('enabled', False)
            status = "✓ Enabled" if enabled else "✗ Disabled"
            click.echo(f"  {name} ({automation_id})")
            click.echo(f"    Status: {status}")
            if 'trigger' in automation:
                click.echo(f"    Trigger: {automation['trigger']}")
            click.echo()


@automations_group.command('create')
@click.option('--file', 'file_path', type=click.Path(exists=True), help='JSON file with automation definition')
@click.option('--name', help='Automation name')
@click.option('--trigger', help='Trigger condition')
@click.option('--action', help='Action to execute')
@click.pass_context
def create_automation(ctx, file_path, name, trigger, action):
    """Create a new automation"""
    client = get_client(ctx)
    
    if file_path:
        with open(file_path, 'r') as f:
            automation_data = json.load(f)
    else:
        if not name or not trigger or not action:
            raise click.ClickException("Either --file or --name, --trigger, and --action must be provided")
        automation_data = {
            'name': name,
            'trigger': trigger,
            'action': action
        }
    
    result = client.post('automation/automations', json_data=automation_data)
    click.echo(f"✓ Created automation: {result.get('name', 'Unknown')}")


@automations_group.command('enable')
@click.argument('automation_id', type=int)
@click.pass_context
def enable_automation(ctx, automation_id):
    """Enable an automation"""
    client = get_client(ctx)
    result = client.post(f'automation/automations/{automation_id}/enable')
    click.echo(f"✓ Enabled automation {automation_id}")


@automations_group.command('disable')
@click.argument('automation_id', type=int)
@click.pass_context
def disable_automation(ctx, automation_id):
    """Disable an automation"""
    client = get_client(ctx)
    result = client.post(f'automation/automations/{automation_id}/disable')
    click.echo(f"✓ Disabled automation {automation_id}")


@automations_group.command('patterns')
@click.pass_context
def list_patterns(ctx):
    """List detected patterns"""
    client = get_client(ctx)
    patterns = client.get('automation/patterns')
    click.echo(format_json(patterns))


@automations_group.command('suggestions')
@click.pass_context
def list_suggestions(ctx):
    """List automation suggestions"""
    client = get_client(ctx)
    suggestions = client.get('automation/suggestions')
    click.echo(format_json(suggestions))

