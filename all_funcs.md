# Claude Code Interceptor Functions

This document lists all functions in the Claude Code Interceptor project and describes what they do.

## Main Module Functions (`cci/__main__.py`)

### `load_configuration(cci_args)`
Loads configuration based on cci arguments. Handles loading specific configurations by name or default configuration. Applies configuration to environment variables. Returns dictionary of environment variables.

### `main()`
Main entry point for the Claude Code Interceptor CLI. Parses command-line arguments into cci-specific and passthrough arguments. Handles various cci-specific commands (--cci-version, --cci-help, --cci-config, --cci-list-configs). Manages help command display with cci-specific additions. Launches Claude CLI with appropriate configuration and environment variables.

## Configuration Module Functions (`cci/config.py`)

### `ConfigManager.__init__(config_dir)`
Initializes the configuration manager. Sets up configuration directory and file paths.

### `ConfigManager._load_config()`
Loads configuration from file or creates default configuration.

### `ConfigManager.save_config()`
Saves current configuration to file.

### `ConfigManager.add_provider(name, base_url)`
Adds a new model provider with validation. Fetches models from the provider and stores them.

### `ConfigManager.remove_provider(name)`
Removes a model provider and associated configurations.

### `ConfigManager.remove_config(name)`
Removes a saved configuration.

### `ConfigManager.check_and_update_default_config()`
Checks if the default configuration still exists. Updates default configuration if needed.

### `ConfigManager.update_provider(name)`
Updates models for a specific provider.

### `ConfigManager.get_configs_for_provider(provider_name)`
Gets list of configuration names that use a specific provider.

### `ConfigManager.set_model(model_type, model_name)`
Sets a model for a specific type (haiku, sonnet, opus).

### `ConfigManager.get_models()`
Gets all configured models.

### `ConfigManager.get_available_models(provider_name)`
Gets list of available models from a specific provider.

### `ConfigManager.save_config_as(name, provider_name)`
Saves current configuration with a name.

### `ConfigManager.load_config_by_name(name)`
Loads a saved configuration by name.

### `ConfigManager.set_default_config(name)`
Sets a configuration as default.

### `ConfigManager.load_default_config()`
Loads the default configuration.

### `ConfigManager.get_environment_variables(provider_name)`
Gets environment variables based on current configuration.

### `get_config_manager()`
Gets a configuration manager instance.

### `apply_configuration(env)`
Applies configuration to environment variables.

## TUI Module Functions (`cci/tui.py`)

### `ConfigTUI.__init__()`
Initializes the TUI with a ConfigManager and Rich console.

### `ConfigTUI.run()`
Runs the main TUI loop with menu options.

### `ConfigTUI._create_config()`
Creates a new configuration through interactive prompts.

### `ConfigTUI._show_main_menu()`
Displays the main menu.

### `ConfigTUI._add_provider()`
Adds a new provider through interactive prompts.

### `ConfigTUI._list_providers()`
Lists all configured providers.

### `ConfigTUI._delete_provider()`
Deletes a provider through interactive prompts.

### `ConfigTUI._set_default_config(no_confirm)`
Sets a configuration as the default.

### `ConfigTUI._list_configs()`
Lists all saved configurations in a table format.

### `ConfigTUI._delete_config()`
Deletes a saved configuration through interactive prompts.

### `ConfigTUI._check_and_prompt_for_new_default()`
Checks if there are other configs available and sets default automatically or prompts user.

## Utility Functions (`cci/utils/config_utils.py`)

### `normalize_config_name(name)`
Normalizes a configuration name according to specified rules. Converts to lowercase, replaces spaces/underscores with dashes, removes invalid characters.

## Utility Functions (`cci/utils/models_fetch.py`)

### `normalize_base_url(base_url)`
Normalizes the base URL by removing trailing slashes and extracting the base path.

### `discover_models_endpoint(base_url)`
Discovers the models endpoint by trying different paths (/v1/models, /models).

### `fetch_models(base_url)`
Fetches models from the /v1/models endpoint.

### `list_models(base_url)`
Lists available models from the API endpoint in various formats.

## Utility Functions (`cci/utils/display.py`)

### `display_env_vars_and_command(env_vars, command_args)`
Displays environment variables and command information.

### `display_configs_table(config_manager)`
Displays saved configurations in a table format.