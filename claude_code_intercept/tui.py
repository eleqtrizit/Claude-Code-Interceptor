"""Terminal User Interface for Claude Code Interceptor configuration."""

import sys

import requests
from rich.console import Console
from rich.prompt import Prompt

from claude_code_intercept.config import ConfigManager
from claude_code_intercept.utils.models_fetch import fetch_models, list_models


class ConfigTUI:
    """Terminal User Interface for managing Claude Code Interceptor configuration."""

    def __init__(self):
        """Initialize the TUI with a ConfigManager and Rich console."""
        self.config_manager = ConfigManager()
        self.console = Console()

    def run(self) -> None:
        """Run the main TUI loop."""
        while True:
            self._show_main_menu()
            choice = Prompt.ask("[bold cyan]Select an option[/bold cyan]", choices=["1", "2", "3", "q", "Q"])

            if choice.lower() == 'q':
                self.console.print("[green]Goodbye![/green]")
                sys.exit(0)
            elif choice == "1":
                self._add_provider()
            elif choice == "2":
                self._list_providers()
            elif choice == "3":
                self._delete_provider()

    def _show_main_menu(self) -> None:
        """Display the main menu."""
        self.console.clear()
        self.console.print("[bold blue]Claude Code Interceptor Configuration[/bold blue]")
        self.console.print("=" * 40)
        self.console.print("1. Add Provider")
        self.console.print("2. List Providers")
        self.console.print("3. Delete Provider")
        self.console.print("Q. Quit")
        self.console.print()

    def _add_provider(self) -> None:
        """Add a new provider."""
        self.console.clear()
        self.console.print("[bold blue]Add Provider[/bold blue]")
        self.console.print("-" * 20)

        # Get provider name
        name = Prompt.ask("[bold cyan]Enter provider name[/bold cyan]")
        if not name:
            self.console.print("[red]Provider name cannot be empty.[/red]")
            Prompt.ask("Press Enter to continue...")
            return

        # Get base URL
        base_url = Prompt.ask("[bold cyan]Enter base URL[/bold cyan]")
        if not base_url:
            self.console.print("[red]Base URL cannot be empty.[/red]")
            Prompt.ask("Press Enter to continue...")
            return

        # Validate the provider by fetching models
        self.console.print("[yellow]Validating provider...[/yellow]")
        try:
            models_data = fetch_models(base_url)
            model_list = list_models(base_url) if models_data else []

            if not model_list:
                self.console.print("[red]No models found, not saving provider[/red]")
                Prompt.ask("Press Enter to continue...")
                return

            # Add provider to config
            success = self.config_manager.add_provider(name, base_url)
            if success:
                self.console.print(
                    f"[green]Provider '{name}' added successfully with {len(model_list)} models.[/green]")
            else:
                self.console.print("[red]Failed to add provider.[/red]")
        except requests.RequestException as e:
            self.console.print(f"[red]Error connecting to provider: {str(e)}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error adding provider: {str(e)}[/red]")

        Prompt.ask("Press Enter to continue...")

    def _list_providers(self) -> None:
        """List all configured providers."""
        self.console.clear()
        self.console.print("[bold blue]Configured Providers[/bold blue]")
        self.console.print("-" * 25)

        providers = self.config_manager.config.get('providers', {})
        current_provider = self.config_manager.config.get('current_provider')

        if not providers:
            self.console.print("[yellow]No providers configured.[/yellow]")
        else:
            for name, provider in providers.items():
                is_current = " ([bold green]*current[/bold green])" if name == current_provider else ""
                self.console.print(f"[bold]{name}{is_current}[/bold]")
                self.console.print(f"  URL: {provider['base_url']}")
                self.console.print(f"  Models: {len(provider['models'])}")
                if provider['models']:
                    # Show first 5 models
                    models_to_show = provider['models'][:5]
                    models_str = ", ".join(models_to_show)
                    if len(provider['models']) > 5:
                        models_str += f", ... ({len(provider['models']) - 5} more)"
                    self.console.print(f"  Available: {models_str}")
                self.console.print()

        Prompt.ask("Press Enter to continue...")

    def _delete_provider(self) -> None:
        """Delete a provider."""
        self.console.clear()
        self.console.print("[bold blue]Delete Provider[/bold blue]")
        self.console.print("-" * 20)

        providers = self.config_manager.config.get('providers', {})
        if not providers:
            self.console.print("[yellow]No providers configured.[/yellow]")
            Prompt.ask("Press Enter to continue...")
            return

        # List providers for selection
        provider_names = list(providers.keys())
        for i, name in enumerate(provider_names, 1):
            is_current = " (*current)" if name == self.config_manager.config.get('current_provider') else ""
            self.console.print(f"{i}. {name}{is_current}")

        # Get user choice
        choice = Prompt.ask("[bold cyan]Enter provider number to delete[/bold cyan] (or 'q' to cancel)",
                            choices=[str(i) for i in range(1, len(provider_names) + 1)] + ['q'])

        if choice.lower() == 'q':
            return

        # Delete the selected provider
        provider_index = int(choice) - 1
        provider_name = provider_names[provider_index]

        # Confirm deletion
        confirm = Prompt.ask(f"[bold red]Are you sure you want to delete '{provider_name}'?[/bold red] (y/N)",
                             choices=['y', 'n'], default='n')

        if confirm.lower() == 'y':
            self.config_manager.remove_provider(provider_name)
            self.console.print(f"[green]Provider '{provider_name}' deleted.[/green]")
        else:
            self.console.print("[yellow]Deletion cancelled.[/yellow]")

        Prompt.ask("Press Enter to continue...")
