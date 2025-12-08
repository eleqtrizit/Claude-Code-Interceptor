# mypy: disable-error-code="assignment"
"""Terminal User Interface for Claude Code Interceptor configuration.

This module provides a text-based user interface for managing Claude Code Interceptor
configurations. It supports both interactive use (with rich prompts) and automated
testing environments through dual implementations of prompt handlers.
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import List, Optional

import inquirer  # type: ignore
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
        """Select an option from a list of choices.

        This abstract method is implemented differently by InquirerPromptHandler
        (for interactive use with arrow key navigation) and TestPromptHandler
        (for automated testing with simple numeric input) to provide appropriate
        user experiences for each environment.

        :param message: The message to display to the user
        :type message: str
        :param choices: List of available choices
        :type choices: List[str]
        :param default: Default choice (optional)
        :type default: Optional[str]
        :return: Selected option
        :rtype: str
        """
        pass

    @abstractmethod
    def select_provider(self, providers: List[str]) -> str:
        """Select a provider from a list of providers.

        This abstract method is implemented differently by InquirerPromptHandler
        (for interactive use) and TestPromptHandler (for automated testing) to provide
        appropriate user experiences for each environment.

        :param providers: List of available providers
        :type providers: List[str]
        :return: Selected provider name
        :rtype: str
        """
        pass

    @abstractmethod
    def select_model(self, model_type: str, models: List[str]) -> Optional[str]:
        """Select a model for a specific type from a list of models.

        This abstract method is implemented differently by InquirerPromptHandler
        (for interactive use) and TestPromptHandler (for automated testing) to provide
        appropriate user experiences for each environment.

        :param model_type: Type of model (haiku, sonnet, opus)
        :type model_type: str
        :param models: List of available models
        :type models: List[str]
        :return: Selected model name or None
        :rtype: Optional[str]
        """
        pass

    @abstractmethod
    def select_config(self, configs: List[str], default_config: Optional[str] = None) -> str:
        """Select a configuration from a list of configurations.

        This abstract method is implemented differently by InquirerPromptHandler
        (for interactive use) and TestPromptHandler (for automated testing) to provide
        appropriate user experiences for each environment.

        :param configs: List of available configurations
        :type configs: List[str]
        :param default_config: Name of default configuration (optional)
        :type default_config: Optional[str]
        :return: Selected configuration name
        :rtype: str
        """
        pass

    @abstractmethod
    def confirm_action(self, message: str, default: str = "n") -> bool:
        """Confirm an action with the user.

        This abstract method is implemented differently by InquirerPromptHandler
        (for interactive use) and TestPromptHandler (for automated testing) to provide
        appropriate user experiences for each environment.

        :param message: Confirmation message to display
        :type message: str
        :param default: Default response ('y' or 'n'), defaults to "n"
        :type default: str, optional
        :return: True if confirmed, False otherwise
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_input(self, message: str) -> str:
        """Get input from the user.

        This abstract method is implemented differently by InquirerPromptHandler
        (for interactive use) and TestPromptHandler (for automated testing) to provide
        appropriate user experiences for each environment.

        :param message: Message to display when requesting input
        :type message: str
        :return: User input string
        :rtype: str
        """
        pass

    @abstractmethod
    def show_menu(self) -> str:
        """Show the main menu and get user selection.

        This abstract method is implemented differently by InquirerPromptHandler
        (for interactive use) and TestPromptHandler (for automated testing) to provide
        appropriate user experiences for each environment.

        :return: Selected menu option
        :rtype: str
        """
        pass

    @abstractmethod
    def clear_screen(self) -> None:
        """Clear the screen."""
        pass

    @abstractmethod
    def print_message(self, message: str, style: str = "") -> None:
        """Print a message to the console.

        This abstract method is implemented by both InquirerPromptHandler and TestPromptHandler
        to provide consistent output formatting across different environments while maintaining
        their respective styling capabilities.

        :param message: Message to print
        :type message: str
        :param style: Style formatting (optional)
        :type style: str, optional
        :return: None
        :rtype: None
        """
        pass

    @abstractmethod
    def wait_for_continue(self) -> None:
        """Wait for the user to press Enter to continue.

        This abstract method is implemented by both InquirerPromptHandler and TestPromptHandler
        to provide a consistent way to pause execution and wait for user input across different
        environments.

        :return: None
        :rtype: None
        """
        pass


class InquirerPromptHandler(PromptHandler):
    """Prompt handler for normal operation using inquirer.

    This implementation uses the inquirer library for rich, interactive terminal prompts
    with features like arrow key navigation and searchable dropdowns. It's designed for
    optimal user experience in interactive environments.

    Corresponds to TestPromptHandler which provides the same functionality but uses
    simplified prompts suitable for automated testing environments.
    """

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
        if not models:
            self.console.print(f"No models available for {model_type}.", "yellow")
            return None

        # Require user to select a model (no "None" option)
        selected = self.select_option(f"Select model for {model_type.capitalize()}", models)
        return selected

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
        """Display main menu using inquirer library for interactive selection.

        This implementation provides a rich interactive experience with arrow key navigation
        and searchable dropdowns, optimized for human users in interactive environments.
        Corresponds to TestPromptHandler.show_menu() which serves the same purpose but
        uses simplified prompts for automated testing.

        :return: Selected menu option identifier
        :rtype: str
        """
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
    """Prompt handler for testing environment using rich.prompt.Prompt.

    This implementation uses rich.prompt.Prompt for simplified input/output handling
    that's easier to test and automate in CI/CD environments. It's designed for
    reliability in automated testing scenarios rather than interactive user experience.

    Corresponds to InquirerPromptHandler which provides the same functionality but uses
    rich interactive prompts suitable for human users in interactive environments.
    """

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
        if not models:
            self.console.print(f"No models available for {model_type}.", "yellow")
            return None

        self.console.print(f"Available models for {model_type}:")
        for i, model in enumerate(models, 1):  # Start numbering from 1
            self.console.print(f"{i}. {model}")

        # Require user to select a model (no "None" option)
        choice = Prompt.ask(f"[bold cyan]Select model for {model_type}[/bold cyan]",
                            choices=[str(i) for i in range(1, len(models) + 1)])
        selected = models[int(choice) - 1]  # Adjust for 1-based indexing
        return selected

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
        """Display main menu using rich.prompt.Prompt for simplified input.

        This implementation uses numbered options and simple prompts that are easy to
        automate in testing environments. Corresponds to InquirerPromptHandler.show_menu()
        which provides a richer interactive experience for human users.

        :return: Selected menu option identifier
        :rtype: str
        """
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
    """Get the appropriate prompt handler based on the environment.

    Selects between InquirerPromptHandler for interactive use and TestPromptHandler
    for automated testing environments. This allows the application to provide an
    optimal user experience in interactive mode while remaining testable in CI/CD.

    :param console: Rich console instance for output
    :type console: Console
    :return: Appropriate prompt handler for the current environment
    :rtype: PromptHandler
    """
    is_test = 'PYTEST_CURRENT_TEST' in os.environ
    if is_test:
        return TestPromptHandler(console)
    else:
        return InquirerPromptHandler(console)


class ConfigTUI:
    """Terminal User Interface for managing Claude Code Interceptor configuration.

    Provides a comprehensive text-based interface for managing providers and configurations.
    Uses either InquirerPromptHandler or TestPromptHandler depending on the environment,
    providing an optimal interface for both interactive use and automated testing.

    The TUI supports the following operations:
    - Add/List/Delete providers
    - Create/List/Set/Delete configurations
    - Manage default configurations
    """

    def __init__(self):
        """Initialize the TUI with a ConfigManager and Rich console.

        Automatically selects the appropriate prompt handler based on the environment
        to provide the best user experience for interactive use or reliable behavior
        in automated testing scenarios.
        """
        self.config_manager = ConfigManager()
        self.console = Console()
        self.prompt_handler = get_prompt_handler(self.console)

    def run(self) -> None:
        """Run the main TUI loop.

        Continuously displays the menu and processes user selections until the user
        chooses to quit. Uses the configured prompt handler to adapt to different
        environments (interactive vs testing).

        :return: None
        :rtype: None
        """
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
        """Create a new configuration.

        Guides the user through creating a new configuration by selecting a provider
        and models for each model type (haiku, sonnet, opus), then saving the
        configuration with a user-provided name.

        :return: None
        :rtype: None
        """
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

    def _configure_api_key(self) -> tuple[str, str]:
        """Configure API key for a provider.

        :return: Tuple of (api_key, api_key_type)
        :rtype: tuple[str, str]
        """
        api_key_options = [
            "Enter API Key",
            "Use environment variable",
            "No API Key needed"
        ]

        choice = self.prompt_handler.select_option(
            "Set API Key",
            api_key_options
        )

        if choice == api_key_options[2]:  # No API key
            return "", "none"
        elif choice == api_key_options[0]:  # Enter API key
            api_key = self.prompt_handler.get_input("Enter API key")
            if not api_key:
                self.prompt_handler.print_message("API key cannot be empty.", "red")
                return "", "none"
            return api_key, "direct"
        elif choice == api_key_options[1]:  # Environment variable
            env_var = self.prompt_handler.get_input("Enter environment variable name")
            if not env_var:
                self.prompt_handler.print_message("Environment variable name cannot be empty.", "red")
                return "", "none"

            # Validate environment variable exists
            if not os.environ.get(env_var, '').strip():
                self.prompt_handler.print_message(
                    f"Warning: Environment variable '{env_var}' not found",
                    "yellow"
                )

                # Offer options to continue or re-enter
                continue_options = [
                    "Enter environment variable again",
                    "Force accept"
                ]
                continue_choice = self.prompt_handler.select_option(
                    f"Error: ENV VAR {env_var} not found",
                    continue_options
                )

                if continue_choice == continue_options[0]:  # Enter again
                    return self._configure_api_key()  # Recursive call to re-enter

            return env_var, "envvar"

        return "", "none"

    def _add_provider(self) -> None:
        """Add a new provider.

        Prompts the user for a provider name and base URL, validates the provider
        by fetching available models, and adds it to the configuration if valid.

        :return: None
        :rtype: None
        """
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

        # Configure API key
        api_key, api_key_type = self._configure_api_key()

        # Validate the provider by fetching models
        self.prompt_handler.print_message("Validating provider...", "yellow")
        try:
            # Determine the actual API key value for validation
            actual_api_key = ""
            if api_key_type == "direct":
                actual_api_key = api_key
            elif api_key_type == "envvar":
                actual_api_key = os.environ.get(api_key, '')

            # Fetch models using the API key for authentication
            models_data = fetch_models(base_url, actual_api_key)
            model_list = list_models(base_url, actual_api_key) if models_data else []

            if not model_list:
                self.prompt_handler.print_message("No models found, not saving provider", "red")
                self.prompt_handler.wait_for_continue()
                return

            # Add provider to config
            success = self.config_manager.add_provider(name, base_url, api_key, api_key_type)
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
        """List all configured providers.

        Displays a formatted list of all configured providers, including their
        base URLs, available models, and API key information, using the configured prompt handler.

        :return: None
        :rtype: None
        """
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

                # Display API key info
                api_key_type = provider.get('api_key_type', 'none')
                if api_key_type == 'direct':
                    self.prompt_handler.print_message("  API Key: [Direct Entry]")
                elif api_key_type == 'envvar':
                    env_var = provider.get('api_key', '')
                    self.prompt_handler.print_message(f"  API Key: [Env Var: {env_var}]")
                else:
                    self.prompt_handler.print_message("  API Key: [None Required]")

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
        """Delete a provider and associated configurations.

        Displays "Delete Provider" header to indicate the current operation mode.
        This method works with both InquirerPromptHandler and TestPromptHandler
        prompt handlers, adapting to the environment's input/output requirements.

        :return: None
        :rtype: None
        """
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
        """Set a configuration as the default.

        Allows the user to select from available configurations to set as the default.
        Can optionally skip the confirmation prompt for use in automated scenarios.

        :param no_confirm: If True, skip the "Press Enter to continue..." prompt
        :type no_confirm: bool
        :return: None
        :rtype: None
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
        """List all saved configurations.

        Displays a formatted table of all saved configurations using the display utility.
        Uses the configured prompt handler for consistent output formatting.

        :return: None
        :rtype: None
        """
        from cci.utils.display import display_configs_table

        self.prompt_handler.clear_screen()
        display_configs_table(self.config_manager)
        self.prompt_handler.wait_for_continue()

    def _delete_config(self) -> None:
        """Delete a saved configuration.

        Allows the user to select and delete a saved configuration, with special
        handling for default configurations that prompts for a new default.

        :return: None
        :rtype: None
        """
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
        """Check if there are other configs available and set default automatically or prompt user.

        Called when the default configuration is deleted. If there's only one
        configuration remaining, it's automatically set as default. If there are
        multiple configurations, the user is prompted to select a new default.

        :return: None
        :rtype: None
        """
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
