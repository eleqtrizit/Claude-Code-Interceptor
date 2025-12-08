"""Display utilities for Claude Code Interceptor."""

from typing import Dict, List

from rich.console import Console
from rich.table import Table

from claude_code_intercept.config import ConfigManager


def display_env_vars_and_command(env_vars: Dict[str, str], command_args: List[str]) -> None:
    """
    Display environment variables and command information.

    :param env_vars: Dictionary of environment variables
    :type env_vars: Dict[str, str]
    :param command_args: List of command arguments
    :type command_args: List[str]
    """
    console = Console()

    if env_vars:
        console.print("[bold blue]Environment Variables:[/bold blue]")
        for key, value in env_vars.items():
            console.print(f"  {key}={value}")
        console.print()

    if command_args:
        console.print("[bold blue]Command:[/bold blue]")
        console.print(f"  claude {' '.join(command_args)}")
    else:
        console.print("[bold blue]Command:[/bold blue]")
        console.print("  claude")


def display_configs_table(config_manager: ConfigManager) -> None:
    """
    Display saved configurations in a table.

    :param config_manager: Configuration manager instance
    :type config_manager: ConfigManager
    """
    console = Console()

    configs = config_manager.config.get('configs', {})

    if not configs:
        console.print("[yellow]No saved configurations found.[/yellow]")
        return

    table = Table(title="Saved Configurations")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Provider", style="magenta")
    table.add_column("Haiku Model", style="green")
    table.add_column("Sonnet Model", style="green")
    table.add_column("Opus Model", style="green")
    table.add_column("Default", style="bold")

    default_config = config_manager.config.get('default_config')

    for name, config in configs.items():
        is_default = "[bold green]✓[/bold green]" if name == default_config else ""
        table.add_row(
            name,
            config.get('provider', 'N/A'),
            config.get('models', {}).get('haiku', 'N/A'),
            config.get('models', {}).get('sonnet', 'N/A'),
            config.get('models', {}).get('opus', 'N/A'),
            is_default
        )

    console.print(table)
