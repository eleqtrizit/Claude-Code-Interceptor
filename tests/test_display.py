"""Tests for display utilities."""

import unittest
from unittest.mock import Mock, patch

from cci.utils.display import display_configs_table, display_env_vars_and_command


class TestDisplayUtils(unittest.TestCase):
    """Test cases for display utilities."""

    @patch('cci.utils.display.Console')
    def test_display_env_vars_and_command_with_vars_and_args(self, mock_console):
        """Test display_env_vars_and_command with environment variables and command args."""
        env_vars = {'TEST_VAR': 'test_value', 'ANOTHER_VAR': 'another_value'}
        command_args = ['--help']

        display_env_vars_and_command(env_vars, command_args)

        # Check that console print was called
        self.assertTrue(mock_console.return_value.print.called)

    @patch('cci.utils.display.Console')
    def test_display_env_vars_and_command_without_vars(self, mock_console):
        """Test display_env_vars_and_command without environment variables."""
        env_vars = {}
        command_args = ['--version']

        display_env_vars_and_command(env_vars, command_args)

        # Check that console print was called
        self.assertTrue(mock_console.return_value.print.called)

    @patch('cci.utils.display.Console')
    def test_display_env_vars_and_command_without_args(self, mock_console):
        """Test display_env_vars_and_command without command args."""
        env_vars = {'TEST_VAR': 'test_value'}
        command_args = []

        display_env_vars_and_command(env_vars, command_args)

        # Check that console print was called
        self.assertTrue(mock_console.return_value.print.called)

    @patch('cci.utils.display.Console')
    def test_display_configs_table_empty(self, mock_console):
        """Test display_configs_table with no saved configurations."""
        mock_config_manager = Mock()
        mock_config_manager.config = {'configs': {}}

        display_configs_table(mock_config_manager)

        # Check that yellow message was printed for no configs
        mock_console.return_value.print.assert_called_with("[yellow]No saved configurations found.[/yellow]")

    @patch('cci.utils.display.Console')
    @patch('cci.utils.display.Table')
    def test_display_configs_table_with_configs(self, mock_table, mock_console):
        """Test display_configs_table with saved configurations."""
        mock_config_manager = Mock()
        mock_config_manager.config = {
            'configs': {
                'test-config': {
                    'provider': 'test-provider',
                    'models': {
                        'haiku': 'test-haiku',
                        'sonnet': 'test-sonnet',
                        'opus': 'test-opus'
                    }
                }
            },
            'default_config': 'test-config'
        }
        # Mock the get_live_models_for_provider to return live models
        mock_config_manager.get_live_models_for_provider.return_value = [
            'test-haiku', 'test-sonnet', 'test-opus'
        ]

        display_configs_table(mock_config_manager)

        # Check that table was created and printed
        self.assertTrue(mock_table.return_value.add_column.called)
        self.assertTrue(mock_table.return_value.add_row.called)
        self.assertTrue(mock_console.return_value.print.called)


if __name__ == '__main__':
    unittest.main()
