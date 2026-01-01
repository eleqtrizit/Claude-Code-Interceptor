"""Tests for the TUI module."""

import os
import unittest
from unittest.mock import MagicMock, patch

from rich.console import Console

from cci.tui import ConfigTUI, InquirerPromptHandler, PromptHandler, TestPromptHandler, get_prompt_handler


class TestPromptHandlerBase(unittest.TestCase):
    """Base test class for PromptHandler classes."""

    def setUp(self):
        """Set up test fixtures."""
        self.console = Console()

    def test_prompt_handler_is_abstract(self):
        """Test that PromptHandler is abstract and cannot be instantiated."""
        with self.assertRaises(TypeError):
            PromptHandler()


class TestInquirerPromptHandler(unittest.TestCase):
    """Test cases for the InquirerPromptHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.console = Console()
        self.handler = InquirerPromptHandler(self.console)

    @patch('cci.tui.inquirer.prompt')
    def test_select_option_success(self, mock_prompt):
        """Test successful option selection."""
        mock_prompt.return_value = {'option': 'choice1'}
        result = self.handler.select_option("Select an option", ['choice1', 'choice2'])
        self.assertEqual(result, 'choice1')
        mock_prompt.assert_called_once()

    @patch('cci.tui.inquirer.prompt')
    def test_select_option_keyboard_interrupt(self, mock_prompt):
        """Test keyboard interrupt handling."""
        mock_prompt.return_value = None
        with self.assertRaises(SystemExit):
            self.handler.select_option("Select an option", ['choice1', 'choice2'])

    @patch('cci.tui.inquirer.prompt')
    def test_select_provider(self, mock_prompt):
        """Test provider selection."""
        mock_prompt.return_value = {'option': 'provider1'}
        result = self.handler.select_provider(['provider1', 'provider2'])
        self.assertEqual(result, 'provider1')

    @patch('cci.tui.inquirer.prompt')
    def test_select_model_with_selection(self, mock_prompt):
        """Test model selection with a model chosen."""
        mock_prompt.return_value = {'option': 'model1'}
        result = self.handler.select_model('haiku', ['model1', 'model2'])
        self.assertEqual(result, 'model1')

    @patch('cci.tui.inquirer.prompt')
    def test_select_model_no_models_available(self, mock_prompt):
        """Test model selection when no models are available."""
        # Mock the console print method
        with patch.object(self.handler.console, 'print') as mock_print:
            result = self.handler.select_model('haiku', [])
            self.assertIsNone(result)
            mock_print.assert_called_once_with("No models available for haiku.", "yellow")

    @patch('cci.tui.inquirer.prompt')
    def test_select_config_with_default(self, mock_prompt):
        """Test config selection with default marking."""
        mock_prompt.return_value = {'option': 'config1 (*default)'}
        configs = ['config1', 'config2']
        result = self.handler.select_config(configs, 'config1')
        # Should return the config name without the default marker
        self.assertEqual(result, 'config1')

    @patch('cci.tui.inquirer.prompt')
    def test_confirm_action_yes(self, mock_prompt):
        """Test confirmation action with yes."""
        mock_prompt.return_value = {'confirm': True}
        result = self.handler.confirm_action("Confirm action?")
        self.assertTrue(result)

    @patch('cci.tui.inquirer.prompt')
    def test_confirm_action_no(self, mock_prompt):
        """Test confirmation action with no."""
        mock_prompt.return_value = {'confirm': False}
        result = self.handler.confirm_action("Confirm action?")
        self.assertFalse(result)

    @patch('cci.tui.inquirer.prompt')
    def test_confirm_action_keyboard_interrupt(self, mock_prompt):
        """Test keyboard interrupt in confirmation."""
        mock_prompt.return_value = None
        with self.assertRaises(SystemExit):
            self.handler.confirm_action("Confirm action?")

    @patch('cci.tui.inquirer.prompt')
    def test_get_input(self, mock_prompt):
        """Test getting user input."""
        mock_prompt.return_value = {'input': 'user input'}
        result = self.handler.get_input("Enter input:")
        self.assertEqual(result, 'user input')

    @patch('cci.tui.inquirer.prompt')
    def test_get_input_keyboard_interrupt(self, mock_prompt):
        """Test keyboard interrupt in input."""
        mock_prompt.return_value = None
        with self.assertRaises(SystemExit):
            self.handler.get_input("Enter input:")

    @patch('cci.tui.inquirer.prompt')
    def test_show_menu_quit(self, mock_prompt):
        """Test showing menu and quitting."""
        mock_prompt.return_value = {'option': 'Quit'}
        result = self.handler.show_menu()
        self.assertEqual(result, 'q')

    @patch('cci.tui.inquirer.prompt')
    def test_show_menu_add_provider(self, mock_prompt):
        """Test showing menu and selecting add provider."""
        mock_prompt.return_value = {'option': 'Add Provider'}
        result = self.handler.show_menu()
        self.assertEqual(result, '1')

    def test_clear_screen(self):
        """Test clearing screen."""
        with patch.object(self.console, 'clear') as mock_clear:
            self.handler.clear_screen()
            mock_clear.assert_called_once()

    def test_print_message_without_style(self):
        """Test printing message without style."""
        with patch.object(self.console, 'print') as mock_print:
            self.handler.print_message("Test message")
            mock_print.assert_called_once_with("Test message")

    def test_print_message_with_style(self):
        """Test printing message with style."""
        with patch.object(self.console, 'print') as mock_print:
            self.handler.print_message("Test message", "green")
            mock_print.assert_called_once_with("[green]Test message[/green]")

    @patch('builtins.input')
    def test_wait_for_continue(self, mock_input):
        """Test waiting for continue."""
        self.handler.wait_for_continue()
        mock_input.assert_called_once_with("Press Enter to continue...")

    @patch('builtins.input')
    def test_wait_for_continue_keyboard_interrupt(self, mock_input):
        """Test keyboard interrupt in wait for continue."""
        mock_input.side_effect = KeyboardInterrupt
        with self.assertRaises(SystemExit):
            self.handler.wait_for_continue()


class TestTestPromptHandler(unittest.TestCase):
    """Test cases for the TestPromptHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.console = Console()
        self.handler = TestPromptHandler(self.console)

    @patch('cci.tui.Prompt.ask')
    def test_select_option(self, mock_ask):
        """Test option selection."""
        mock_ask.return_value = '1'
        result = self.handler.select_option("Select an option", ['choice1', 'choice2'])
        self.assertEqual(result, 'choice1')

    @patch('cci.tui.Prompt.ask')
    def test_select_provider(self, mock_ask):
        """Test provider selection."""
        mock_ask.return_value = '2'
        result = self.handler.select_provider(['provider1', 'provider2', 'provider3'])
        self.assertEqual(result, 'provider2')

    @patch('cci.tui.Prompt.ask')
    def test_select_model_with_selection(self, mock_ask):
        """Test model selection with a model chosen."""
        mock_ask.return_value = '2'  # Second option (second model, because 1 is model1, 2 is model2)
        result = self.handler.select_model('haiku', ['model1', 'model2'])
        self.assertEqual(result, 'model2')

    @patch('cci.tui.Prompt.ask')
    def test_select_model_no_models_available(self, mock_ask):
        """Test model selection when no models are available."""
        # Mock the console print method
        with patch.object(self.handler.console, 'print') as mock_print:
            result = self.handler.select_model('haiku', [])
            self.assertIsNone(result)
            mock_print.assert_called_once_with("No models available for haiku.", "yellow")

    @patch('cci.tui.Prompt.ask')
    def test_select_config(self, mock_ask):
        """Test config selection."""
        mock_ask.return_value = '1'
        result = self.handler.select_config(['config1', 'config2'], 'config1')
        self.assertEqual(result, 'config1')

    @patch('cci.tui.Prompt.ask')
    def test_confirm_action_yes(self, mock_ask):
        """Test confirmation action with yes."""
        mock_ask.return_value = 'y'
        result = self.handler.confirm_action("Confirm action?")
        self.assertTrue(result)

    @patch('cci.tui.Prompt.ask')
    def test_confirm_action_no(self, mock_ask):
        """Test confirmation action with no."""
        mock_ask.return_value = 'n'
        result = self.handler.confirm_action("Confirm action?")
        self.assertFalse(result)

    @patch('cci.tui.Prompt.ask')
    def test_get_input(self, mock_ask):
        """Test getting user input."""
        mock_ask.return_value = 'user input'
        result = self.handler.get_input("Enter input:")
        self.assertEqual(result, 'user input')

    @patch('cci.tui.Prompt.ask')
    def test_show_menu_lowercase_q(self, mock_ask):
        """Test showing menu with lowercase q."""
        mock_ask.return_value = 'q'
        result = self.handler.show_menu()
        self.assertEqual(result, 'q')

    @patch('cci.tui.Prompt.ask')
    def test_show_menu_uppercase_q(self, mock_ask):
        """Test showing menu with uppercase Q."""
        mock_ask.return_value = 'Q'
        result = self.handler.show_menu()
        self.assertEqual(result, 'Q')

    @patch('cci.tui.Prompt.ask')
    def test_show_menu_numeric_choice(self, mock_ask):
        """Test showing menu with numeric choice."""
        mock_ask.return_value = '1'
        result = self.handler.show_menu()
        self.assertEqual(result, '1')

    def test_clear_screen(self):
        """Test clearing screen."""
        with patch.object(self.console, 'clear') as mock_clear:
            self.handler.clear_screen()
            mock_clear.assert_called_once()

    def test_print_message_without_style(self):
        """Test printing message without style."""
        with patch.object(self.console, 'print') as mock_print:
            self.handler.print_message("Test message")
            mock_print.assert_called_once_with("Test message")

    def test_print_message_with_style(self):
        """Test printing message with style."""
        with patch.object(self.console, 'print') as mock_print:
            self.handler.print_message("Test message", "green")
            mock_print.assert_called_once_with("[green]Test message[/green]")

    @patch('builtins.input')
    def test_wait_for_continue(self, mock_input):
        """Test waiting for continue."""
        self.handler.wait_for_continue()
        mock_input.assert_called_once_with("Press Enter to continue...")

    @patch('builtins.input')
    def test_wait_for_continue_keyboard_interrupt(self, mock_input):
        """Test keyboard interrupt in wait for continue."""
        mock_input.side_effect = KeyboardInterrupt
        with self.assertRaises(SystemExit):
            self.handler.wait_for_continue()


class TestGetPromptHandler(unittest.TestCase):
    """Test cases for the get_prompt_handler function."""

    def setUp(self):
        """Set up test fixtures."""
        self.console = Console()

    def test_get_prompt_handler_normal_environment(self):
        """Test getting prompt handler in normal environment."""
        # Ensure PYTEST_CURRENT_TEST is not set
        if 'PYTEST_CURRENT_TEST' in os.environ:
            del os.environ['PYTEST_CURRENT_TEST']

        handler = get_prompt_handler(self.console)
        self.assertIsInstance(handler, InquirerPromptHandler)

    def test_get_prompt_handler_test_environment(self):
        """Test getting prompt handler in test environment."""
        # Set PYTEST_CURRENT_TEST to simulate test environment
        os.environ['PYTEST_CURRENT_TEST'] = '1'

        handler = get_prompt_handler(self.console)
        self.assertIsInstance(handler, TestPromptHandler)

        # Clean up
        del os.environ['PYTEST_CURRENT_TEST']


class TestConfigTUI(unittest.TestCase):
    """Test cases for the ConfigTUI class."""

    def setUp(self):
        """Set up test fixtures."""
        with patch('cci.tui.ConfigManager') as mock_config_manager:
            mock_cm_instance = mock_config_manager.return_value
            mock_cm_instance.config = {}
            self.tui = ConfigTUI()

    @patch('cci.tui.Prompt')
    def test_show_main_menu(self, mock_prompt):
        """Test the main menu can be displayed and exits properly."""
        # Mock the prompt to return 'q' to exit immediately
        mock_prompt.ask.return_value = 'q'

        # Call the run method which will show the menu
        with self.assertRaises(SystemExit):
            self.tui.run()

    @patch('builtins.input')
    @patch('cci.tui.Prompt')
    @patch('cci.tui.ConfigManager')
    def test_run_add_provider(self, mock_config_manager, mock_prompt, mock_input):
        """Test running TUI with add provider option."""
        # Mock the prompt sequence: first select "1" (Add Provider), then "q" (Quit)
        # We also need to provide values for the provider name, base URL, and API key inputs
        mock_prompt.ask.side_effect = ['1', 'test_provider', 'http://test.com', '3', 'q']  # 3 = "No API Key needed"
        # Mock input for wait_for_continue calls
        mock_input.return_value = ''

        # Mock config manager methods
        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {'providers': {}}

        with self.assertRaises(SystemExit):
            self.tui.run()

    @patch('builtins.input')
    @patch('cci.tui.Prompt')
    @patch('cci.tui.ConfigManager')
    def test_run_list_providers_empty(self, mock_config_manager, mock_prompt, mock_input):
        """Test running TUI with list providers option when no providers exist."""
        # Mock the prompt sequence: first select "2" (List Providers), then "q" (Quit)
        mock_prompt.ask.side_effect = ['2', 'q']
        # Mock input for wait_for_continue call
        mock_input.return_value = ''

        # Mock config manager methods
        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {'providers': {}}

        with self.assertRaises(SystemExit):
            self.tui.run()

    @patch('builtins.input')
    @patch('cci.tui.Prompt')
    def test_run_create_config_no_providers(self, mock_prompt, mock_input):
        """Test running TUI with create config option when no providers exist."""
        # Mock the prompt sequence: first select "4" (Create Config), then "q" (Quit)
        mock_prompt.ask.side_effect = ['4', 'q']
        # Mock input for wait_for_continue call
        mock_input.return_value = ''

        with self.assertRaises(SystemExit):
            self.tui.run()

    @patch('builtins.input')
    @patch('cci.tui.Prompt')
    @patch('cci.tui.ConfigManager')
    def test_run_list_configs(self, mock_config_manager, mock_prompt, mock_input):
        """Test running TUI with list configs option."""
        # Mock the prompt sequence: first select "5" (List Configs), then "q" (Quit)
        mock_prompt.ask.side_effect = ['5', 'q']
        # Mock input for wait_for_continue call
        mock_input.return_value = ''

        # Mock config manager methods
        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {'configs': {}}

        with patch('cci.utils.display.display_configs_table'):
            with self.assertRaises(SystemExit):
                self.tui.run()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_create_config_success_flow(self, mock_config_manager, mock_prompt_handler):
        """Test the complete flow of creating a configuration."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_provider.return_value = 'test_provider'
        mock_ph_instance.select_model.return_value = 'test_model'
        mock_ph_instance.get_input.return_value = 'test_config'

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'providers': {
                'test_provider': {
                    'base_url': 'http://test.com',
                    'models': ['test_model']
                }
            }
        }
        mock_cm_instance.get_live_models_for_provider.return_value = ['test_model']
        mock_cm_instance.get_available_models.return_value = ['test_model']

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._create_config()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.select_provider.assert_called()
        mock_ph_instance.select_model.assert_any_call('haiku', ['test_model'])
        mock_ph_instance.select_model.assert_any_call('sonnet', ['test_model'])
        mock_ph_instance.select_model.assert_any_call('opus', ['test_model'])
        mock_ph_instance.get_input.assert_called_with("Enter a name for this configuration")
        mock_cm_instance.save_config_as.assert_called()
        mock_ph_instance.print_message.assert_called()
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_add_provider_success_flow(self, mock_config_manager, mock_prompt_handler):
        """Test the complete flow of adding a provider."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.get_input.side_effect = ['test_provider', 'http://test.com']
        mock_ph_instance.print_message = MagicMock()
        mock_ph_instance.wait_for_continue = MagicMock()
        mock_ph_instance.select_option.return_value = "No API Key needed"  # Mock API key selection

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.add_provider.return_value = True

        # Patch the external functions
        with patch('cci.tui.fetch_models') as mock_fetch_models, \
                patch('cci.tui.list_models') as mock_list_models:

            mock_fetch_models.return_value = True
            mock_list_models.return_value = ['test_model']

            # Create a new TUI instance with mocked dependencies
            tui = ConfigTUI()
            tui.prompt_handler = mock_ph_instance

            # Call the method
            tui._add_provider()

            # Verify calls were made
            mock_ph_instance.clear_screen.assert_called()
            mock_ph_instance.get_input.assert_any_call("Enter provider name")
            mock_ph_instance.get_input.assert_any_call("Enter base URL")
            mock_ph_instance.select_option.assert_called_with(
                "Set API Key", ["Enter API Key", "Use environment variable", "No API Key needed"])
            mock_fetch_models.assert_called_with('http://test.com', '')
            mock_list_models.assert_called_with('http://test.com', '')
            mock_cm_instance.add_provider.assert_called_with('test_provider', 'http://test.com', '', 'none')
            mock_ph_instance.print_message.assert_called()
            mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_list_providers_with_data(self, mock_config_manager, mock_prompt_handler):
        """Test listing providers when providers exist."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'providers': {
                'test_provider': {
                    'base_url': 'http://test.com',
                    'models': ['model1', 'model2', 'model3', 'model4', 'model5', 'model6']
                }
            }
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._list_providers()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.print_message.assert_any_call("Configured Providers", "bold blue")
        mock_ph_instance.print_message.assert_any_call("test_provider", "bold")
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_set_default_config_success_flow(self, mock_config_manager, mock_prompt_handler):
        """Test setting a default configuration."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_config.return_value = 'test_config'
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'configs': {
                'test_config': {},
                'other_config': {}
            },
            'default_config': 'other_config'
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._set_default_config()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.select_config.assert_called()
        mock_cm_instance.set_default_config.assert_called_with('test_config')
        mock_ph_instance.print_message.assert_called()
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_delete_config_success_flow(self, mock_config_manager, mock_prompt_handler):
        """Test deleting a configuration."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_config.return_value = 'test_config'
        mock_ph_instance.confirm_action.return_value = True
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'configs': {
                'test_config': {},
                'other_config': {}
            },
            'default_config': 'other_config'
        }
        mock_cm_instance.remove_config.return_value = True

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._delete_config()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.select_config.assert_called()
        mock_ph_instance.confirm_action.assert_called()
        mock_cm_instance.remove_config.assert_called_with('test_config')
        mock_ph_instance.print_message.assert_called()
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_configure_api_key_no_api_key(self, mock_config_manager, mock_prompt_handler):
        """Test configuring API key with 'No API Key needed' option."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_option.return_value = "No API Key needed"

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        api_key, api_key_type = tui._configure_api_key()

        # Verify results
        self.assertEqual(api_key, "")
        self.assertEqual(api_key_type, "none")

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_configure_api_key_enter_api_key(self, mock_config_manager, mock_prompt_handler):
        """Test configuring API key with direct entry."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_option.return_value = "Enter API Key"
        mock_ph_instance.get_input.return_value = "test-api-key"

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        api_key, api_key_type = tui._configure_api_key()

        # Verify results
        self.assertEqual(api_key, "test-api-key")
        self.assertEqual(api_key_type, "direct")

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_configure_api_key_use_env_var(self, mock_config_manager, mock_prompt_handler):
        """Test configuring API key with environment variable."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_option.return_value = "Use environment variable"
        mock_ph_instance.get_input.return_value = "TEST_API_KEY"

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        api_key, api_key_type = tui._configure_api_key()

        # Verify results
        self.assertEqual(api_key, "TEST_API_KEY")
        self.assertEqual(api_key_type, "envvar")

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_configure_api_key_empty_api_key(self, mock_config_manager, mock_prompt_handler):
        """Test configuring API key with empty direct entry."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_option.return_value = "Enter API Key"
        mock_ph_instance.get_input.return_value = ""

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        api_key, api_key_type = tui._configure_api_key()

        # Verify results
        self.assertEqual(api_key, "")
        self.assertEqual(api_key_type, "none")

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_configure_api_key_empty_env_var(self, mock_config_manager, mock_prompt_handler):
        """Test configuring API key with empty environment variable name."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_option.return_value = "Use environment variable"
        mock_ph_instance.get_input.return_value = ""

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        api_key, api_key_type = tui._configure_api_key()

        # Verify results
        self.assertEqual(api_key, "")
        self.assertEqual(api_key_type, "none")

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_delete_provider_no_providers(self, mock_config_manager, mock_prompt_handler):
        """Test deleting a provider when no providers exist."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'providers': {}
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._delete_provider()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.print_message.assert_any_call("Delete Provider", "bold blue")
        mock_ph_instance.print_message.assert_any_call("No providers configured.", "yellow")
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_delete_provider_cancel_deletion(self, mock_config_manager, mock_prompt_handler):
        """Test deleting a provider but canceling the operation."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_option.return_value = "test_provider"
        mock_ph_instance.confirm_action.return_value = False
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'providers': {
                'test_provider': {
                    'base_url': 'http://test.com',
                    'models': ['model1']
                }
            }
        }
        mock_cm_instance.get_configs_for_provider.return_value = []

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._delete_provider()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.select_option.assert_called()
        mock_ph_instance.confirm_action.assert_called()
        mock_ph_instance.print_message.assert_any_call("Deletion cancelled.", "yellow")
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_check_and_prompt_for_new_default_no_configs(self, mock_config_manager, mock_prompt_handler):
        """Test checking for new default when no configurations exist."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'configs': {}
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method and expect SystemExit
        with self.assertRaises(SystemExit) as cm:
            tui._check_and_prompt_for_new_default()

        # Verify the exit code is 1
        self.assertEqual(cm.exception.code, 1)

        # Verify calls were made
        mock_ph_instance.print_message.assert_called_with("No configurations available. Exiting with error.", "red")

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_check_and_prompt_for_new_default_one_config(self, mock_config_manager, mock_prompt_handler):
        """Test checking for new default when only one configuration exists."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'configs': {
                'single_config': {}
            }
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._check_and_prompt_for_new_default()

        # Verify calls were made
        mock_cm_instance.set_default_config.assert_called_with('single_config')
        mock_ph_instance.print_message.assert_called_with(
            "Configuration 'single_config' automatically set as default.", "green")

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_check_and_prompt_for_new_default_multiple_configs(self, mock_config_manager, mock_prompt_handler):
        """Test checking for new default when multiple configurations exist."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_config.return_value = 'selected_config'
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'configs': {
                'config1': {},
                'config2': {},
                'selected_config': {}
            }
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._check_and_prompt_for_new_default()

        # Verify calls were made
        mock_ph_instance.print_message.assert_any_call("The default configuration has been deleted.", "yellow")
        mock_ph_instance.print_message.assert_any_call("You must select a new default configuration:", "bold yellow")

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_add_provider_empty_name(self, mock_config_manager, mock_prompt_handler):
        """Test adding a provider with empty name."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.get_input.return_value = ""  # Empty name
        mock_ph_instance.wait_for_continue = MagicMock()

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._add_provider()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.get_input.assert_called_with("Enter provider name")
        mock_ph_instance.print_message.assert_called_with("Provider name cannot be empty.", "red")
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_add_provider_empty_base_url(self, mock_config_manager, mock_prompt_handler):
        """Test adding a provider with empty base URL."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.get_input.side_effect = ['test_provider', '']  # Provider name, then empty URL
        mock_ph_instance.wait_for_continue = MagicMock()

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._add_provider()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.get_input.assert_any_call("Enter provider name")
        mock_ph_instance.get_input.assert_any_call("Enter base URL")
        mock_ph_instance.print_message.assert_called_with("Base URL cannot be empty.", "red")
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_create_config_no_providers(self, mock_config_manager, mock_prompt_handler):
        """Test creating a configuration when no providers exist."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'providers': {}
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._create_config()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.print_message.assert_called_with(
            "No providers configured. Please add a provider first.", "yellow")
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_create_config_no_models_available(self, mock_config_manager, mock_prompt_handler):
        """Test creating a configuration when no models are available for the provider."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_provider.return_value = 'test_provider'
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'providers': {
                'test_provider': {
                    'base_url': 'http://test.com',
                    'models': []
                }
            }
        }
        mock_cm_instance.get_live_models_for_provider.return_value = None
        mock_cm_instance.get_available_models.return_value = []

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._create_config()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.select_provider.assert_called()
        mock_ph_instance.print_message.assert_called_with("No models available for the selected provider.", "yellow")
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_set_default_config_no_configs(self, mock_config_manager, mock_prompt_handler):
        """Test setting default configuration when no configurations exist."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'configs': {}
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._set_default_config()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.print_message.assert_called_with(
            "No configurations saved. Please create a configuration first.", "yellow")
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_delete_config_no_configs(self, mock_config_manager, mock_prompt_handler):
        """Test deleting a configuration when no configurations exist."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'configs': {}
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._delete_config()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.print_message.assert_called_with("No configurations saved.", "yellow")
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_delete_config_cancel_deletion(self, mock_config_manager, mock_prompt_handler):
        """Test deleting a configuration but canceling the operation."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.select_config.return_value = 'test_config'
        mock_ph_instance.confirm_action.return_value = False
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'configs': {
                'test_config': {},
                'other_config': {}
            },
            'default_config': 'other_config'
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._delete_config()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.select_config.assert_called()
        mock_ph_instance.confirm_action.assert_called()
        mock_ph_instance.print_message.assert_called_with("Deletion cancelled.", "yellow")
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_list_providers_no_providers(self, mock_config_manager, mock_prompt_handler):
        """Test listing providers when no providers exist."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'providers': {}
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._list_providers()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.print_message.assert_any_call("Configured Providers", "bold blue")
        mock_ph_instance.print_message.assert_any_call("No providers configured.", "yellow")
        mock_ph_instance.wait_for_continue.assert_called()

    @patch('cci.tui.TestPromptHandler')
    @patch('cci.tui.ConfigManager')
    def test_list_providers_with_api_keys(self, mock_config_manager, mock_prompt_handler):
        """Test listing providers with different API key types."""
        # Setup mocks
        mock_ph_instance = mock_prompt_handler.return_value
        mock_ph_instance.wait_for_continue = MagicMock()

        mock_cm_instance = mock_config_manager.return_value
        mock_cm_instance.config = {
            'providers': {
                'direct_key_provider': {
                    'base_url': 'http://direct.com',
                    'models': ['model1'],
                    'api_key': 'secret-key',
                    'api_key_type': 'direct'
                },
                'env_var_provider': {
                    'base_url': 'http://env.com',
                    'models': ['model2'],
                    'api_key': 'ENV_VAR_NAME',
                    'api_key_type': 'envvar'
                },
                'no_key_provider': {
                    'base_url': 'http://none.com',
                    'models': ['model3'],
                    'api_key': '',
                    'api_key_type': 'none'
                }
            }
        }

        # Create a new TUI instance with mocked dependencies
        tui = ConfigTUI()
        tui.prompt_handler = mock_ph_instance

        # Call the method
        tui._list_providers()

        # Verify calls were made
        mock_ph_instance.clear_screen.assert_called()
        mock_ph_instance.print_message.assert_any_call("Configured Providers", "bold blue")
        mock_ph_instance.print_message.assert_any_call("direct_key_provider", "bold")
        mock_ph_instance.print_message.assert_any_call("  URL: http://direct.com")
        mock_ph_instance.print_message.assert_any_call("  API Key: [Direct Entry]")
        mock_ph_instance.print_message.assert_any_call("  Models: 1")
        mock_ph_instance.wait_for_continue.assert_called()


if __name__ == '__main__':
    unittest.main()
