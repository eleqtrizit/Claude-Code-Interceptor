"""Terminal User Interface for Claude Code Interceptor configuration."""

import os
import sys
from abc import ABC, abstractmethod
from typing import List, Optional

import inquirer
import requests
from rich.console import Console
from rich.prompt import Prompt

from cci.config import ConfigManager
from cci.utils.config_utils import normalize_config_name
from cci.utils.models_fetch import fetch_models, list_models


class PromptHandler(ABC):
    """Abstract base class for handling user prompts in different environments."""

    @abstractmethod
    def select_option(self, message: str, choices: List[str], default: Optional[str] = None) -> str:
        """Select an option from a list of choices."""
        pass

    @abstractmethod
    def select_provider(self, providers: List[str]) -> str:
        """Select a provider from a list of providers."""
        pass

    @abstractmethod
    def select_model(self, model_type: str, models: List[str]) -> Optional[str]:
        """Select a model for a specific type from a list of models."""
        pass

    @abstractmethod
    def select_config(self, configs: List[str], default_config: Optional[str] = None) -> str:
        """Select a configuration from a list of configurations."""
        pass

    @abstractmethod
    def confirm_action(self, message: str, default: str = "n") -> bool:
        """Confirm an action with the user."""
        pass

    @abstractmethod
    def get_input(self, message: str) -> str:
        """Get input from the user."""
        pass

    @abstractmethod
    def show_menu(self) -> str:
        """Show the main menu and get user selection."""
        pass

    @abstractmethod
    def clear_screen(self) -> None:
        """Clear the screen."""
        pass

    @abstractmethod
    def print_message(self, message: str, style: str = "") -> None:
        """Print a message to the console."""
        pass

    @abstractmethod
    def wait_for_continue(self) -> None:
        """Wait for the user to press Enter to continue."""
        pass


class InquirerPromptHandler(PromptHandler):
    """Prompt handler for normal operation using inquirer."""

    def __init__(self, console: Console):
        self.console = console

    def select_option(self, message: str, choices: List[str], default: Optional[str] = None) -> str:
        questions = [
            inquirer.List('option',
                          message=message,
                          choices=choices,
                          default=default)
        ]
        try:
            answers = inquirer.prompt(questions)
            if answers is None:
                raise KeyboardInterrupt
            return answers['option']
        except KeyboardInterrupt:
            self.console.print("\n[green]Goodbye![/green]")
            sys.exit(0)

    def select_provider(self, providers: List[str]) -> str:
        return self.select_option("Select provider", providers)

    def select_model(self, model_type: str, models: List[str]) -> Optional[str]:
        choices = ['None'] + models
        selected = self.select_option(f"Select model for {model_type.capitalize()}", choices)
        return selected if selected != 'None' else None

    def select_config(self, configs: List[str], default_config: Optional[str] = None) -> str:
        # Mark the current default config
        choices = []
        for name in configs:
            is_default = " (*default)" if name == default_config else ""
            choices.append(f"{name}{is_default}")

        selected = self.select_option("Select configuration to set as default", choices)
        # Extract the config name (remove the default marker if present)
        return selected.split(" (*default)")[0]

    def confirm_action(self, message: str, default: str = "n") -> bool:
        questions = [
            inquirer.Confirm('confirm',
                             message=message,
                             default=default.lower() == 'y')
        ]
        try:
            answers = inquirer.prompt(questions)
            if answers is None:
                raise KeyboardInterrupt
            return answers['confirm']
        except KeyboardInterrupt:
            self.console.print("\n[green]Goodbye![/green]")
            sys.exit(0)

    def get_input(self, message: str) -> str:
        questions = [
            inquirer.Text('input',
                          message=message)
        ]
        try:
            answers = inquirer.prompt(questions)
            if answers is None:
                raise KeyboardInterrupt
            return answers['input']
        except KeyboardInterrupt:
            self.console.print("\n[green]Goodbye![/green]")
            sys.exit(0)

    def show_menu(self) -> str:
        self.console.clear()
        self.console.print("[bold blue]Claude Code Interceptor Configuration[/bold blue]")
        self.console.print("=" * 40)
        self.console.print("[dim](Press Ctrl+C at any time to quit)[/dim]")
        self.console.print()

        choices = [
            'Add Provider',
            'List Providers',
            'Delete Provider',
            'Create Config',
            'List Configs',
            'Set Default Config',
            'Delete Config',
            'Quit'
        ]
        selected = self.select_option("Select an option", choices)
        # Map the selection to the corresponding action
        action_map = {
            'Add Provider': '1',
            'List Providers': '2',
            'Delete Provider': '3',
            'Create Config': '4',
            'List Configs': '5',
            'Set Default Config': '6',
            'Delete Config': '7',
            'Quit': 'q'
        }
        return action_map.get(selected, 'q')

    def clear_screen(self) -> None:
        self.console.clear()

    def print_message(self, message: str, style: str = "") -> None:
        if style:
            self.console.print(f"[{style}]{message}[/{style}]")
        else:
            self.console.print(message)

    def wait_for_continue(self) -> None:
        # Simply wait for user to press Enter
        try:
            input("Press Enter to continue...")
        except KeyboardInterrupt:
            self.console.print("\n[green]Goodbye![/green]")
            sys.exit(0)


class TestPromptHandler(PromptHandler):
    """Prompt handler for testing environment using rich.prompt.Prompt."""

    def __init__(self, console: Console):
        self.console = console

    def select_option(self, message: str, choices: List[str], default: Optional[str] = None) -> str:
        # For testing, we display the choices and ask for input
        self.console.print(message)
        for i, choice in enumerate(choices, 1):
            self.console.print(f"{i}. {choice}")

        choice_numbers = [str(i) for i in range(1, len(choices) + 1)]
        choice = Prompt.ask("[bold cyan]Select an option[/bold cyan]", choices=choice_numbers)
        return choices[int(choice) - 1]

    def select_provider(self, providers: List[str]) -> str:
        self.console.print("Available providers:")
        for i, provider in enumerate(providers, 1):
            self.console.print(f"{i}. {provider}")

        choice = Prompt.ask("[bold cyan]Select provider[/bold cyan]",
                            choices=[str(i) for i in range(1, len(providers) + 1)])
        return providers[int(choice) - 1]

    def select_model(self, model_type: str, models: List[str]) -> Optional[str]:
        model_choices = ['None'] + models
        self.console.print(f"Available models for {model_type}:")
        for i, model in enumerate(model_choices):
            self.console.print(f"{i}. {model}")

        choice = Prompt.ask(f"[bold cyan]Select model for {model_type} (0 for None)[/bold cyan]",
                            choices=[str(i) for i in range(len(model_choices))])
        selected = model_choices[int(choice)]
        return selected if selected != 'None' else None

    def select_config(self, configs: List[str], default_config: Optional[str] = None) -> str:
        self.console.print("Available configurations:")
        for i, name in enumerate(configs, 1):
            is_default = " ([bold green]*default[/bold green])" if name == default_config else ""
            self.console.print(f"{i}. {name}{is_default}")

        choice = Prompt.ask("[bold cyan]Select configuration to set as default[/bold cyan]",
                            choices=[str(i) for i in range(1, len(configs) + 1)])
        return configs[int(choice) - 1]

    def confirm_action(self, message: str, default: str = "n") -> bool:
        confirm = Prompt.ask(f"[bold red]{message}[/bold red] (y/N)",
                             choices=['y', 'n'], default=default)
        return confirm.lower() == 'y'

    def get_input(self, message: str) -> str:
        return Prompt.ask(f"[bold cyan]{message}[/bold cyan]")

    def show_menu(self) -> str:
        self.console.clear()
        self.console.print("[bold blue]Claude Code Interceptor Configuration[/bold blue]")
        self.console.print("=" * 40)
        self.console.print("1. Add Provider")
        self.console.print("2. List Providers")
        self.console.print("3. Delete Provider")
        self.console.print("4. Create Config")
        self.console.print("5. List Configs")
        self.console.print("6. Set Default Config")
        self.console.print("7. Delete Config")
        self.console.print("Q. Quit")
        self.console.print()

        return Prompt.ask("[bold cyan]Select an option[/bold cyan]",
                          choices=["1", "2", "3", "4", "5", "6", "7", "q", "Q"])

    def clear_screen(self) -> None:
        self.console.clear()

    def print_message(self, message: str, style: str = "") -> None:
        if style:
            self.console.print(f"[{style}]{message}[/{style}]")
        else:
            self.console.print(message)

    def wait_for_continue(self) -> None:
        # Simply wait for user to press Enter
        try:
            input("Press Enter to continue...")
        except KeyboardInterrupt:
            self.console.print("\n[green]Goodbye![/green]")
            sys.exit(0)


def get_prompt_handler(console: Console) -> PromptHandler:
    """Get the appropriate prompt handler based on the environment."""
    is_test = 'PYTEST_CURRENT_TEST' in os.environ
    if is_test:
        return TestPromptHandler(console)
    else:
        return InquirerPromptHandler(console)


class ConfigTUI:
    """Terminal User Interface for managing Claude Code Interceptor configuration."""

    def __init__(self):
        """Initialize the TUI with a ConfigManager and Rich console."""
        self.config_manager = ConfigManager()
        self.console = Console()
        self.prompt_handler = get_prompt_handler(self.console)

    def run(self) -> None:
        """Run the main TUI loop."""
        while True:
            choice = self.prompt_handler.show_menu()

            if choice.lower() == 'q':
                self.prompt_handler.print_message("Goodbye!", "green")
                sys.exit(0)
            elif choice == "1":
                self._add_provider()
            elif choice == "2":
                self._list_providers()
            elif choice == "3":
                self._delete_provider()
            elif choice == "4":
                self._create_config()
            elif choice == "5":
                self._list_configs()
            elif choice == "6":
                self._set_default_config()
            elif choice == "7":
                self._delete_config()

    def _create_config(self) -> None:
        """Create a new configuration."""
        self.prompt_handler.clear_screen()
        self.prompt_handler.print_message("Create Configuration", "bold blue")
        self.prompt_handler.print_message("-" * 25)

        # Check if we have providers
        providers = self.config_manager.config.get('providers', {})
        if not providers:
            self.prompt_handler.print_message("No providers configured. Please add a provider first.", "yellow")
            self.prompt_handler.wait_for_continue()
            return

        # Step 1: Select provider
        provider_names = list(providers.keys())
        selected_provider = self.prompt_handler.select_provider(provider_names)

        # Step 2: Select models for Haiku, Sonnet, and Opus
        available_models = self.config_manager.get_available_models(selected_provider)
        if not available_models:
            self.prompt_handler.print_message("No models available for the selected provider.", "yellow")
            self.prompt_handler.wait_for_continue()
            return

        # Model selection for each type
        model_types = ['haiku', 'sonnet', 'opus']

        for model_type in model_types:
            selected_model = self.prompt_handler.select_model(model_type, available_models)
            if selected_model is not None:
                self.config_manager.set_model(model_type, selected_model)
            else:
                self.config_manager.set_model(model_type, None)

        # Step 3: Enter configuration name
        config_name = self.prompt_handler.get_input("Enter a name for this configuration")
        if not config_name:
            self.prompt_handler.print_message("Configuration name cannot be empty.", "red")
            self.prompt_handler.wait_for_continue()
            return

        # Normalize the config name
        normalized_name = normalize_config_name(config_name)

        # Save the configuration
        self.config_manager.save_config_as(normalized_name, selected_provider)

        self.prompt_handler.print_message(f"Configuration '{normalized_name}' created successfully!", "green")
        self.prompt_handler.wait_for_continue()

    def _add_provider(self) -> None:
        """Add a new provider."""
        self.prompt_handler.clear_screen()
        self.prompt_handler.print_message("Add Provider", "bold blue")
        self.prompt_handler.print_message("-" * 20)

        # Get provider name
        name = self.prompt_handler.get_input("Enter provider name")
        if not name:
            self.prompt_handler.print_message("Provider name cannot be empty.", "red")
            self.prompt_handler.wait_for_continue()
            return

        # Get base URL
        base_url = self.prompt_handler.get_input("Enter base URL")
        if not base_url:
            self.prompt_handler.print_message("Base URL cannot be empty.", "red")
            self.prompt_handler.wait_for_continue()
            return

        # Validate the provider by fetching models
        self.prompt_handler.print_message("Validating provider...", "yellow")
        try:
            models_data = fetch_models(base_url)
            model_list = list_models(base_url) if models_data else []

            if not model_list:
                self.prompt_handler.print_message("No models found, not saving provider", "red")
                self.prompt_handler.wait_for_continue()
                return

            # Add provider to config
            success = self.config_manager.add_provider(name, base_url)
            if success:
                self.prompt_handler.print_message(
                    f"Provider '{name}' added successfully with {len(model_list)} models.", "green")
            else:
                self.prompt_handler.print_message("Failed to add provider.", "red")
        except requests.RequestException as e:
            self.prompt_handler.print_message(f"Error connecting to provider: {str(e)}", "red")
        except Exception as e:
            self.prompt_handler.print_message(f"Error adding provider: {str(e)}", "red")

        self.prompt_handler.wait_for_continue()

    def _list_providers(self) -> None:
        """List all configured providers."""
        self.prompt_handler.clear_screen()
        self.prompt_handler.print_message("Configured Providers", "bold blue")
        self.prompt_handler.print_message("-" * 25)

        providers = self.config_manager.config.get('providers', {})
        if not providers:
            self.prompt_handler.print_message("No providers configured.", "yellow")
        else:
            for name, provider in providers.items():
                self.prompt_handler.print_message(f"{name}", "bold")
                self.prompt_handler.print_message(f"  URL: {provider['base_url']}")
                self.prompt_handler.print_message(f"  Models: {len(provider['models'])}")
                if provider['models']:
                    # Show first 5 models
                    models_to_show = provider['models'][:5]
                    models_str = ", ".join(models_to_show)
                    if len(provider['models']) > 5:
                        models_str += f", ... ({len(provider['models']) - 5} more)"
                    self.prompt_handler.print_message(f"  Available: {models_str}")
                self.prompt_handler.print_message("")

        self.prompt_handler.wait_for_continue()

    def _delete_provider(self) -> None:
        """Delete a provider."""
        self.prompt_handler.clear_screen()
        self.prompt_handler.print_message("Delete Provider", "bold blue")
        self.prompt_handler.print_message("-" * 20)

        providers = self.config_manager.config.get('providers', {})
        if not providers:
            self.prompt_handler.print_message("No providers configured.", "yellow")
            self.prompt_handler.wait_for_continue()
            return

        # List providers for selection
        provider_names = list(providers.keys())
        choice = self.prompt_handler.select_option(
            "Enter provider number to delete (or 'q' to cancel)",
            provider_names + ['q']
        )

        if choice.lower() == 'q':
            return

        provider_name = choice

        # Check for associated configurations
        associated_configs = self.config_manager.get_configs_for_provider(provider_name)
        if associated_configs:
            msg = f"Warning: Provider '{provider_name}' has "
            msg += f"{len(associated_configs)} associated configuration(s):"
            self.prompt_handler.print_message(msg, "bold yellow")

            for config_name in associated_configs:
                is_default = " (*default)" if (
                    config_name == self.config_manager.config.get('default_config')) else ""
                self.prompt_handler.print_message(f"  - {config_name}{is_default}")
            self.prompt_handler.print_message("These configurations will also be deleted.", "bold yellow")

            # Additional confirmation for configs
            confirm_msg = "Are you sure you want to delete the provider and all associated configurations? (y/N)"
            if not self.prompt_handler.confirm_action(confirm_msg):
                self.prompt_handler.print_message("Deletion cancelled.", "yellow")
                self.prompt_handler.wait_for_continue()
                return

        # Confirm deletion
        confirm_msg = f"Are you sure you want to delete '{provider_name}'? (y/N)"
        if self.prompt_handler.confirm_action(confirm_msg):
            # Check if the default config will be deleted
            default_config_will_be_deleted = False
            default_config = self.config_manager.config.get('default_config')
            if default_config and default_config in associated_configs:
                default_config_will_be_deleted = True

            self.config_manager.remove_provider(provider_name)
            self.prompt_handler.print_message(
                f"Provider '{provider_name}' and associated configurations deleted.", "green")

            # Check if we need to prompt for a new default config
            if default_config_will_be_deleted:
                self._check_and_prompt_for_new_default()
        else:
            self.prompt_handler.print_message("Deletion cancelled.", "yellow")

        self.prompt_handler.wait_for_continue()

    def _set_default_config(self, no_confirm: bool = False) -> None:
        """
        Set a configuration as the default.

        :param no_confirm: If True, skip the "Press Enter to continue..." prompt
        :type no_confirm: bool
        """
        self.prompt_handler.clear_screen()
        self.prompt_handler.print_message("Set Default Configuration", "bold blue")
        self.prompt_handler.print_message("-" * 30)

        # Check if we have saved configurations
        configs = self.config_manager.config.get('configs', {})
        if not configs:
            self.prompt_handler.print_message("No configurations saved. Please create a configuration first.", "yellow")
            if not no_confirm:
                self.prompt_handler.wait_for_continue()
            return

        # List available configurations
        config_names = list(configs.keys())
        default_config = self.config_manager.config.get('default_config')
        selected_config = self.prompt_handler.select_config(config_names, default_config)

        # Set the selected configuration as default
        self.config_manager.set_default_config(selected_config)
        self.prompt_handler.print_message(f"Configuration '{selected_config}' set as default successfully!", "green")
        if not no_confirm:
            self.prompt_handler.wait_for_continue()

    def _list_configs(self) -> None:
        """List all saved configurations."""
        from cci.utils.display import display_configs_table

        self.prompt_handler.clear_screen()
        display_configs_table(self.config_manager)
        self.prompt_handler.wait_for_continue()

    def _delete_config(self) -> None:
        """Delete a saved configuration."""
        self.prompt_handler.clear_screen()
        self.prompt_handler.print_message("Delete Configuration", "bold blue")
        self.prompt_handler.print_message("-" * 25)

        configs = self.config_manager.config.get('configs', {})
        if not configs:
            self.prompt_handler.print_message("No configurations saved.", "yellow")
            self.prompt_handler.wait_for_continue()
            return

        # List configurations for selection
        config_names = list(configs.keys())
        default_config = self.config_manager.config.get('default_config')
        config_name = self.prompt_handler.select_config(config_names, default_config)

        if config_name.lower() == 'q':
            return

        # Check if this is the default config
        is_default = config_name == default_config
        if is_default:
            self.prompt_handler.print_message("Warning: This is the current default configuration.", "bold yellow")

        # Confirm deletion
        confirm_msg = f"Are you sure you want to delete '{config_name}'? (y/N)"
        if self.prompt_handler.confirm_action(confirm_msg):
            success = self.config_manager.remove_config(config_name)
            if success:
                self.prompt_handler.print_message(f"Configuration '{config_name}' deleted.", "green")

                # Check if we need to prompt for a new default config
                if is_default:
                    self._check_and_prompt_for_new_default()
            else:
                self.prompt_handler.print_message(f"Failed to delete configuration '{config_name}'.", "red")
        else:
            self.prompt_handler.print_message("Deletion cancelled.", "yellow")

        self.prompt_handler.wait_for_continue()

    def _check_and_prompt_for_new_default(self) -> None:
        """Check if there are other configs available and set default automatically or prompt user."""
        configs = self.config_manager.config.get('configs', {})
        if configs:
            if len(configs) == 1:
                # Automatically set the only available config as default
                config_name = list(configs.keys())[0]
                self.config_manager.set_default_config(config_name)
                self.prompt_handler.print_message(
                    f"Configuration '{config_name}' automatically set as default.", "green")
            else:
                # Multiple configs available, prompt user to select one
                self.prompt_handler.print_message("The default configuration has been deleted.", "yellow")
                self.prompt_handler.print_message("You must select a new default configuration:", "bold yellow")
                self._set_default_config(no_confirm=True)
        else:
            self.prompt_handler.print_message("No configurations available. Exiting with error.", "red")
            sys.exit(1)
