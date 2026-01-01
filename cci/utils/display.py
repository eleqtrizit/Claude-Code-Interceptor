"""Display utilities for Claude Code Interceptor."""

from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table

from cci.config import ConfigManager


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
            if key == "ANTHROPIC_API_KEY":
                value = f"****{value[-4:]}"
            console.print(f"  {key}={value}")
        console.print()

    if command_args:
        console.print("[bold blue]Command:[/bold blue]")
        console.print(f"  claude {' '.join(command_args)}")
    else:
        console.print("[bold blue]Command:[/bold blue]")
        console.print("  claude")


def _format_model_name(model_name: Optional[str], live_models: Optional[List[str]]) -> str:
    """
    Format model name with color (red if stale, yellow if unverified, green if valid).

    :param model_name: The model name to format
    :type model_name: Optional[str]
    :param live_models: List of live model names, or None if unavailable
    :type live_models: Optional[List[str]]
    :return: Formatted model name with Rich markup
    :rtype: str
    """
    if not model_name:
        return 'N/A'

    if live_models is None:  # API unavailable - mark as unverified
        return f"[yellow]{model_name}[/yellow]"

    if model_name in live_models:
        return model_name  # Green (from column style)
    else:
        return f"[red]{model_name}[/red]"  # Stale model


def display_configs_table(config_manager: ConfigManager) -> None:
    """
    Display saved configurations in a table with stale model detection.

    :param config_manager: Configuration manager instance
    :type config_manager: ConfigManager
    """
    console = Console()

    configs = config_manager.config.get('configs', {})

    if not configs:
        console.print("[yellow]No saved configurations found.[/yellow]")
        return

    # Cache live models per provider to avoid redundant API calls
    provider_models_cache: Dict[str, Optional[List[str]]] = {}

    table = Table(title="Saved Configurations")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Provider", style="magenta")
    table.add_column("Haiku Model", style="green")
    table.add_column("Sonnet Model", style="green")
    table.add_column("Opus Model", style="green")
    table.add_column("Default", style="bold")

    default_config = config_manager.config.get('default_config')

    for name, config in configs.items():
        provider_name = config.get('provider', 'N/A')

        # Get live models for this provider (use cache if available)
        if provider_name not in provider_models_cache:
            provider_models_cache[provider_name] = config_manager.get_live_models_for_provider(provider_name)

        live_models = provider_models_cache[provider_name]

        # Format model names with color based on validity
        haiku_model = _format_model_name(
            config.get('models', {}).get('haiku'),
            live_models
        )
        sonnet_model = _format_model_name(
            config.get('models', {}).get('sonnet'),
            live_models
        )
        opus_model = _format_model_name(
            config.get('models', {}).get('opus'),
            live_models
        )

        is_default = "[bold green]✓[/bold green]" if name == default_config else ""
        table.add_row(
            name,
            provider_name,
            haiku_model,
            sonnet_model,
            opus_model,
            is_default
        )

    console.print(table)

    # Show legend if any API calls failed
    if None in provider_models_cache.values():
        console.print(
            "\n[bold]Legend:[/bold] [green]✓ Valid[/green] | "
            "[yellow]⚠ Unverified (API unavailable)[/yellow] | "
            "[red]✗ Stale[/red]"
        )
