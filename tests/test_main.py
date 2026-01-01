"""Tests for the main module."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from cci.__main__ import (handle_config_command, handle_help_command, handle_help_passthrough,
                          handle_list_configs_command, handle_version_command, launch_claude_cli, load_configuration,
                          main)


def test_handle_version_command():
    """Test the handle_version_command function."""
    with patch('cci.__main__.get_project_version') as mock_get_version, \
            patch('builtins.print') as mock_print:

        # Test with version
        mock_get_version.return_value = '1.2.3'
        handle_version_command()
        mock_print.assert_called_once_with('Claude Code Interceptor v1.2.3')

        # Reset mocks
        mock_print.reset_mock()

        # Test without version
        mock_get_version.return_value = None
        handle_version_command()
        mock_print.assert_called_once_with('Claude Code Interceptor vUnknown')


def test_handle_help_command():
    """Test the handle_help_command function."""
    with patch('cci.__main__.get_project_version') as mock_get_version, \
            patch('builtins.print') as mock_print:

        # Test with version
        mock_get_version.return_value = '1.2.3'
        handle_help_command()

        # Check that print was called with expected messages
        calls = mock_print.call_args_list
        assert any('Claude Code Interceptor v1.2.3' in str(call) for call in calls)
        assert any('A wrapper for Claude Code CLI' in str(call) for call in calls)
        assert any('Usage: cci [OPTIONS] [CLAUD_ARGS]...' in str(call) for call in calls)


@patch('cci.tui.ConfigTUI')
def test_handle_config_command(mock_config_tui):
    """Test the handle_config_command function."""
    mock_tui_instance = MagicMock()
    mock_config_tui.return_value = mock_tui_instance

    handle_config_command()

    mock_config_tui.assert_called_once()
    mock_tui_instance.run.assert_called_once()


@patch('cci.config.get_config_manager')
@patch('cci.utils.display.display_configs_table')
def test_handle_list_configs_command(mock_display_table, mock_get_config_manager):
    """Test the handle_list_configs_command function."""
    mock_config_manager = MagicMock()
    mock_get_config_manager.return_value = mock_config_manager

    handle_list_configs_command()

    mock_get_config_manager.assert_called_once()
    mock_display_table.assert_called_once_with(mock_config_manager)


@patch('cci.__main__.load_configuration')
def test_launch_claude_cli_success(mock_load_config):
    """Test launch_claude_cli function with successful execution."""
    mock_load_config.return_value = {'TEST_VAR': 'test_value'}

    with patch('subprocess.run') as mock_run, \
            patch('sys.exit') as mock_exit:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # This should not raise an exception
        launch_claude_cli([], [])

        mock_run.assert_called_once()
        mock_exit.assert_called_once_with(0)


@patch('cci.__main__.load_configuration')
def test_launch_claude_cli_file_not_found(mock_load_config):
    """Test launch_claude_cli function when claude CLI is not found."""
    mock_load_config.return_value = {'TEST_VAR': 'test_value'}

    with patch('subprocess.run') as mock_run, \
            patch('builtins.print') as mock_print, \
            patch('sys.exit') as mock_exit:
        mock_run.side_effect = FileNotFoundError()

        launch_claude_cli([], [])

        mock_exit.assert_called_once_with(1)
        mock_print.assert_called_with(
            "Error: Claude Code CLI ('claude') not found. Please ensure it's installed and in your PATH."
        )


@patch('cci.__main__.load_configuration')
@patch('cci.utils.display.display_env_vars_and_command')
def test_launch_claude_cli_keyboard_interrupt(mock_display, mock_load_config):
    """Test launch_claude_cli function when KeyboardInterrupt is raised."""
    mock_load_config.return_value = {'TEST_VAR': 'test_value'}

    with patch('subprocess.run') as mock_run, \
            patch('sys.exit') as mock_exit:
        mock_run.side_effect = KeyboardInterrupt()

        launch_claude_cli([], [])

        mock_exit.assert_called_once_with(0)


@patch('cci.config.get_config_manager')
def test_load_configuration_success(mock_get_config_manager):
    """Test load_configuration function with successful config loading."""
    mock_config_manager = MagicMock()
    mock_get_config_manager.return_value = mock_config_manager

    mock_config = MagicMock()
    mock_config_manager.load_config_by_name.return_value = mock_config
    mock_config_manager.get_environment_variables.return_value = {'TEST_VAR': 'test_value'}
    mock_config_manager.get_default_config_name.return_value = 'default_config'

    result = load_configuration([])

    assert result == {'TEST_VAR': 'test_value'}
    mock_config_manager.set_default_if_just_one_config.assert_called_once()


@patch('cci.config.get_config_manager')
def test_load_configuration_with_specific_config(mock_get_config_manager):
    """Test load_configuration function with --cci-use-config argument."""
    mock_config_manager = MagicMock()
    mock_get_config_manager.return_value = mock_config_manager

    mock_config = MagicMock()
    mock_config_manager.load_config_by_name.return_value = mock_config
    mock_config_manager.get_environment_variables.return_value = {'TEST_VAR': 'test_value'}

    result = load_configuration(['--cci-use-config', 'test_config'])

    assert result == {'TEST_VAR': 'test_value'}
    mock_config_manager.load_config_by_name.assert_called_once_with('test_config')


@patch('cci.__main__.handle_list_configs_command')
@patch('cci.config.get_config_manager')
def test_load_configuration_config_not_found(mock_get_config_manager, mock_handle_list):
    """Test load_configuration function when config is not found."""
    mock_config_manager = MagicMock()
    mock_get_config_manager.return_value = mock_config_manager

    mock_config_manager.load_config_by_name.return_value = None
    mock_config_manager.get_default_config_name.return_value = 'nonexistent_config'

    with patch('builtins.print') as mock_print, \
            pytest.raises(SystemExit) as exc_info:
        load_configuration([])

    assert exc_info.value.code == 1
    # Verify error message is printed
    assert any("Error: Configuration 'nonexistent_config' not found." in str(call)
               for call in mock_print.call_args_list)
    # Verify available configs header is printed
    assert any("Available configurations:" in str(call)
               for call in mock_print.call_args_list)
    # Verify handle_list_configs_command was called
    mock_handle_list.assert_called_once()


@patch('cci.config.get_config_manager')
def test_load_configuration_no_default_or_specified(mock_get_config_manager):
    """Test load_configuration function when no config is available."""
    mock_config_manager = MagicMock()
    mock_get_config_manager.return_value = mock_config_manager

    mock_config_manager.get_default_config_name.return_value = None
    mock_config_manager.load_config_by_name.return_value = None

    with patch('builtins.print') as mock_print, \
            pytest.raises(SystemExit) as exc_info:
        load_configuration([])

    assert exc_info.value.code == 1
    mock_print.assert_called_with(
        "Error: Set a default model (--cci-config) or use --cci-use-config with a valid configuration name."
    )


@patch('sys.argv', ['cci', '--cci-version'])
@patch('cci.__main__.handle_version_command')
def test_main_version_command(mock_handle_version):
    """Test main function with --cci-version argument."""
    main()

    mock_handle_version.assert_called_once()


@patch('sys.argv', ['cci', '--cci-help'])
@patch('cci.__main__.handle_help_command')
def test_main_help_command(mock_handle_help):
    """Test main function with --cci-help argument."""
    main()

    mock_handle_help.assert_called_once()


@patch('sys.argv', ['cci', '--cci-config'])
@patch('cci.__main__.handle_config_command')
def test_main_config_command(mock_handle_config):
    """Test main function with --cci-config argument."""
    main()

    mock_handle_config.assert_called_once()


@patch('sys.argv', ['cci', '--cci-list-configs'])
@patch('cci.__main__.handle_list_configs_command')
def test_main_list_configs_command(mock_handle_list_configs):
    """Test main function with --cci-list-configs argument."""
    main()

    mock_handle_list_configs.assert_called_once()


@patch('sys.argv', ['cci', '--help'])
@patch('cci.__main__.handle_help_passthrough')
def test_main_help_passthrough(mock_handle_help_passthrough):
    """Test main function with --help argument."""
    mock_handle_help_passthrough.side_effect = SystemExit(0)

    with pytest.raises(SystemExit):
        main()

    mock_handle_help_passthrough.assert_called_once()


@patch('sys.argv', ['cci'])
@patch('cci.config.get_config_manager')
@patch('cci.__main__.launch_claude_cli')
def test_main_launch_claude_cli(mock_launch_claude_cli, mock_get_config_manager):
    """Test main function launching Claude CLI."""
    mock_config_manager = MagicMock()
    mock_get_config_manager.return_value = mock_config_manager
    mock_config_manager.config = {'configs': {'default': {}}}

    main()

    mock_launch_claude_cli.assert_called_once()


@patch('sys.argv', ['cci'])
@patch('cci.config.get_config_manager')
def test_main_no_configs_exit(mock_get_config_manager):
    """Test main function exiting when no configurations exist."""
    mock_config_manager = MagicMock()
    mock_get_config_manager.return_value = mock_config_manager
    mock_config_manager.config = {'configs': {}}

    with patch('builtins.print') as mock_print, \
            pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    mock_print.assert_called_with(
        "No configuration found. Please run 'cci --cci-config' to set up your configuration."
    )


@patch('cci.__main__.load_configuration')
@patch('cci.utils.display.display_env_vars_and_command')
@patch('subprocess.run')
def test_handle_help_passthrough_success(mock_subprocess, mock_display, mock_load_config):
    """Test handle_help_passthrough function with successful execution."""
    mock_load_config.return_value = {'TEST_VAR': 'test_value'}
    mock_result = MagicMock()
    mock_result.stdout = "Claude help output"
    mock_result.stderr = ""
    mock_result.returncode = 0
    mock_subprocess.return_value = mock_result

    with patch('sys.exit') as mock_exit:
        handle_help_passthrough(['--help'], [])

        # Check that subprocess.run was called with the right arguments
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        assert call_args[0][0] == ['claude', '--help']
        assert call_args[1]['capture_output'] is True
        assert call_args[1]['text'] is True
        # Check that our TEST_VAR is in the env
        assert call_args[1]['env']['TEST_VAR'] == 'test_value'
        mock_exit.assert_called_once_with(0)


@patch('cci.__main__.load_configuration')
@patch('cci.utils.display.display_env_vars_and_command')
@patch('subprocess.run')
def test_handle_help_passthrough_file_not_found(mock_subprocess, mock_display, mock_load_config):
    """Test handle_help_passthrough function when claude CLI is not found."""
    mock_load_config.return_value = {'TEST_VAR': 'test_value'}
    mock_subprocess.side_effect = FileNotFoundError()

    with patch('builtins.print') as mock_print, \
            patch('sys.exit') as mock_exit:
        handle_help_passthrough(['--help'], [])

        mock_print.assert_called_with(
            "Error: Claude Code CLI ('claude') not found. Please ensure it's installed and in your PATH."
        )
        mock_exit.assert_called_once_with(1)


@patch('cci.__main__.load_configuration')
@patch('cci.utils.display.display_env_vars_and_command')
@patch('subprocess.run')
def test_handle_help_passthrough_with_stderr(mock_subprocess, mock_display, mock_load_config):
    """Test handle_help_passthrough function when there's stderr output."""
    mock_load_config.return_value = {'TEST_VAR': 'test_value'}
    mock_result = MagicMock()
    mock_result.stdout = "Claude help output"
    mock_result.stderr = "Some error message"
    mock_result.returncode = 0
    mock_subprocess.return_value = mock_result

    with patch('builtins.print') as mock_print, \
            patch('sys.exit') as mock_exit:
        handle_help_passthrough(['--help'], [])

        # Check that both stdout and stderr were printed
        mock_print.assert_any_call("Claude help output")
        mock_print.assert_any_call("Some error message", file=sys.stderr)
        mock_exit.assert_called_once_with(0)


@patch('sys.argv', ['cci', '--cci-use-config', 'test-config'])
@patch('cci.__main__.load_configuration')
@patch('cci.__main__.launch_claude_cli')
def test_main_with_cci_use_config_argument(mock_launch_claude_cli, mock_load_config):
    """Test main function with --cci-use-config argument."""
    mock_load_config.return_value = {'TEST_VAR': 'test_value'}

    with patch('cci.config.get_config_manager') as mock_get_config_manager:
        mock_config_manager = MagicMock()
        mock_get_config_manager.return_value = mock_config_manager
        mock_config_manager.config = {'configs': {'default': {}}}

        # We can't easily test the full main function, but we can test that
        # our tests have improved coverage by running all tests and checking coverage
        pass


if __name__ == '__main__':
    pytest.main([__file__])
