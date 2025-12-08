import os
import subprocess
import sys

from cci.utils.display import display_env_vars_and_command
from cci.utils.version import get_project_version


def load_configuration(cci_args):
    """
    Load configuration based on cci arguments.

    :param cci_args: List of cci-specific arguments
    :type cci_args: list
    :return: Dictionary of environment variables
    :rtype: dict
    """
    env_vars = {}
    try:
        # Import here to avoid circular imports and unnecessary dependencies
        from cci.config import apply_configuration, get_config_manager
        config_manager = get_config_manager()

        # Check if --cci-use-config is specified
        if '--cci-use-config' in cci_args:
            # Find the config name (it should be the next argument after --cci-use-config)
            config_name = None
            for i, arg in enumerate(cci_args):
                if arg == '--cci-use-config' and i + 1 < len(cci_args):
                    config_name = cci_args[i + 1]
                    break

            if config_name:
                # Load the specified configuration
                if not config_manager.load_config_by_name(config_name):
                    print(f"Warning: Configuration '{config_name}' not found. Using default configuration.")
                    config_manager.load_default_config()
            else:
                print("Warning: No configuration name provided for --cci-use-config. Using default configuration.")
                config_manager.load_default_config()
        else:
            # Load default configuration if available
            config_manager.load_default_config()

        # Get environment variables from configuration
        # For now, we don't have a specific provider to use, so we pass None
        env_vars = config_manager.get_environment_variables(None)

        # Apply configuration to environment
        apply_configuration(env_vars)
    except Exception:
        # If configuration fails, continue without it
        pass

    return env_vars


def handle_version_command():
    """Handle the --cci-version command."""
    version = get_project_version()
    if version:
        print(f"Claude Code Interceptor v{version}")
    else:
        print("Claude Code Interceptor vUnknown")


def handle_help_command():
    """Handle the --cci-help command."""
    version = get_project_version()
    version_str = f"v{version}" if version else "vUnknown"

    print(f"Claude Code Interceptor {version_str}")
    print("A wrapper for Claude Code CLI")
    print("")
    print("Usage: cci [OPTIONS] [CLAUD_ARGS]...")
    print("")
    print("Claude Code Intercept Commands:")
    print("  --cci-version                                     Show Claude Code Interceptor version")
    print("  --cci-help                                        Show this help message")
    print("  --cci-config                                      Configure model providers and settings")
    print("  --cci-list-configs                                List saved configurations in a table")
    print("  --cci-use-config NAME                             Use a specific saved configuration")
    print("")
    print("All other arguments are passed through to the Claude Code CLI.")


def handle_config_command():
    """Handle the --cci-config command."""
    # Import here to avoid circular imports and unnecessary dependencies
    from cci.tui import ConfigTUI
    tui = ConfigTUI()
    tui.run()


def handle_list_configs_command():
    """Handle the --cci-list-configs command."""
    # Import here to avoid circular imports and unnecessary dependencies
    from cci.config import get_config_manager
    from cci.utils.display import display_configs_table
    config_manager = get_config_manager()
    display_configs_table(config_manager)


def handle_help_passthrough(passthrough_args, cci_args):
    """Handle the help command passthrough to Claude CLI."""
    # Apply configuration before showing help
    env_vars = load_configuration(cci_args)

    # Display environment variables
    display_env_vars_and_command(env_vars, passthrough_args)

    # Pass through to get Claude CLI help
    try:
        cmd = ['claude'] + passthrough_args
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        # Add cci-specific help at the bottom
        print("\nClaude Code Intercept Commands:")
        print("  --cci-version                                     Show Claude Code Interceptor version")
        print("  --cci-help                                        Show this help message")
        print("  --cci-config                                      Configure model providers and settings")
        print("  --cci-list-configs                                List saved configurations in a table")
        print("  --cci-use-config NAME                             Use a specific saved configuration")

        sys.exit(result.returncode)
    except FileNotFoundError:
        print("Error: Claude Code CLI ('claude') not found. Please ensure it's installed and in your PATH.")
        sys.exit(1)


def launch_claude_cli(passthrough_args, cci_args):
    """Launch the Claude CLI with appropriate configuration."""
    # Apply configuration before launching Claude CLI
    env_vars = load_configuration(cci_args)

    # Display environment variables and command
    display_env_vars_and_command(env_vars, passthrough_args)

    # Pass arguments to Claude Code CLI
    try:
        if passthrough_args:
            result = subprocess.run(['claude'] + passthrough_args)
        else:
            # Launch Claude CLI with no arguments (starts interactive session)
            # We need to preserve the current environment and add our variables
            full_env = os.environ.copy()
            full_env.update(env_vars)

            # Use subprocess with explicit stdin/stdout/stderr inheritance
            # This should preserve the TTY connection when run from a real terminal
            result = subprocess.run(['claude'], env=full_env,
                                    stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("Error: Claude Code CLI ('claude') not found. Please ensure it's installed and in your PATH.")
        sys.exit(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully for interactive sessions
        sys.exit(0)


def main():
    """Main entry point for the Claude Code Interceptor CLI."""
    # Check if this is a configuration command - if so, don't check for config
    config_cmd = False
    for arg in sys.argv[1:]:
        if arg in ['--cci-config', '--cci-help', '--cci-version', '--cci-list-configs']:
            config_cmd = True
            break

    # If not a config command, check if there are any saved configurations
    if not config_cmd:
        from cci.config import get_config_manager
        config_manager = get_config_manager()

        # Check if there are any saved configurations
        saved_configs = config_manager.config.get('configs', {})

        # If no saved configurations exist, prompt user to configure
        if not saved_configs:
            print("No configuration found. Please run 'cci --cci-config' to set up your configuration.")
            sys.exit(1)

    # Split arguments into cci-specific and passthrough arguments
    cci_args = []
    passthrough_args = []

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith('--cci-'):
            cci_args.append(arg)
            # Handle arguments with values
            if arg == '--cci-use-config':
                # Special handling for --cci-use-config to capture the config name
                if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('-'):
                    cci_args.append(sys.argv[i + 1])
                    i += 2
                else:
                    i += 1
            elif i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('-'):
                cci_args.append(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        else:
            passthrough_args.append(arg)
            i += 1

    # Handle cci-specific arguments
    if '--cci-version' in cci_args:
        handle_version_command()
        return

    if '--cci-help' in cci_args:
        handle_help_command()
        return

    if '--cci-config' in cci_args:
        handle_config_command()
        return

    if '--cci-list-configs' in cci_args:
        handle_list_configs_command()
        return

    # Handle help command to show cci-specific help at the bottom
    if '--help' in passthrough_args or '-h' in passthrough_args:
        handle_help_passthrough(passthrough_args, cci_args)
        return

    # Launch Claude CLI with appropriate configuration
    launch_claude_cli(passthrough_args, cci_args)


if __name__ == "__main__":
    main()
