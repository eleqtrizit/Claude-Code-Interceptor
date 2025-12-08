"""Configuration management for Claude Code Interceptor."""


import contextlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from cci.utils.config_utils import normalize_config_name
from cci.utils.models_fetch import fetch_models, list_models


class ConfigManager:
    """Manages configuration for Claude Code Interceptor."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration manager.

        :param config_dir: Directory to store configuration files. Defaults to ~/.config/cci
        :type config_dir: Optional[str]
        """
        if config_dir is None:
            self.config_dir = Path.home() / '.config' / 'cci'
        else:
            self.config_dir = Path(config_dir)

        self.config_file = self.config_dir / 'config.json'
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        :return: Configuration dictionary
        :rtype: Dict[str, Any]
        """
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load config file if it exists
        if self.config_file.exists():
            with contextlib.suppress(json.JSONDecodeError, IOError):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        # Return default config
        return {
            'providers': {},
            'models': {
                'haiku': None,
                'sonnet': None,
                'opus': None
            },
            'configs': {},
            'default_config': None
        }

    def save_config(self) -> None:
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def add_provider(self, name: str, base_url: str, api_key: str = "", api_key_type: str = "none") -> bool:
        """
        Add a new model provider.

        :param name: Name of the provider
        :type name: str
        :param base_url: Base URL of the provider
        :type base_url: str
        :param api_key: API key for the provider (optional)
        :type api_key: str
        :param api_key_type: Type of API key handling (direct, envvar, none)
        :type api_key_type: str
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            # Fetch models from the provider
            models_data = fetch_models(base_url)
            model_list = list_models(base_url) if models_data else []

            # Add provider to config
            self.config['providers'][name] = {
                'base_url': base_url,
                'models': model_list,
                'api_key': api_key,
                'api_key_type': api_key_type
            }

            self.save_config()
            return True
        except Exception:
            return False

    def remove_provider(self, name: str) -> None:
        """
        Remove a model provider.

        :param name: Name of the provider to remove
        :type name: str
        """
        if name in self.config['providers']:
            # Remove associated configurations first
            configs_to_remove = self.get_configs_for_provider(name)
            for config_name in configs_to_remove:
                if config_name in self.config['configs']:
                    del self.config['configs'][config_name]

                    # Reset default config if it was the one removed
                    if self.config['default_config'] == config_name:
                        self.config['default_config'] = None

            del self.config['providers'][name]
            self.set_default_if_just_one_config()
            self.save_config()

    def remove_config(self, name: str) -> bool:
        """
        Remove a saved configuration.

        :param name: Name of the configuration to remove
        :type name: str
        :return: True if successful, False otherwise
        :rtype: bool
        """
        if name in self.config['configs']:
            del self.config['configs'][name]

            # Reset default config if it was the one removed
            if self.config['default_config'] == name:
                self.config['default_config'] = None

            self.save_config()
            return True
        return False

    def check_and_update_default_config(self) -> bool:
        """
        Check if the default configuration still exists and prompt user to select a new one if needed.

        :return: True if there are configs available and user selected a new default,
                 False if no configs available or user cancelled
        :rtype: bool
        """
        # If there's no default config set, nothing to check
        if self.config['default_config'] is not None:
            # Check if the default config still exists
            if self.config['default_config'] not in self.config['configs']:
                # Default config no longer exists, set to None
                self.config['default_config'] = None
                self.save_config()

        # If there's no default config set but there are configs available,
        # we could prompt the user to select one, but this should be handled in the UI
        return self.config['default_config'] is not None

    def update_provider(self, name: str) -> bool:
        """
        Update models for a provider.

        :param name: Name of the provider to update
        :type name: str
        :return: True if successful, False otherwise
        :rtype: bool
        """
        if name not in self.config['providers']:
            return False

        try:
            provider = self.config['providers'][name]
            base_url = provider['base_url']

            # Fetch updated models
            model_list = list_models(base_url)

            # Update provider models
            self.config['providers'][name]['models'] = model_list
            self.save_config()
            return True
        except Exception:
            return False

    def get_configs_for_provider(self, provider_name: str) -> List[str]:
        """
        Get list of configuration names that use a specific provider.

        :param provider_name: Name of the provider to check
        :type provider_name: str
        :return: List of configuration names that use the provider
        :rtype: List[str]
        """
        configs = self.config.get('configs', {})
        associated_configs = []

        for config_name, config_data in configs.items():
            if config_data.get('provider') == provider_name:
                associated_configs.append(config_name)

        return associated_configs

    def set_model(self, model_type: str, model_name: Optional[str]) -> bool:
        """
        Set a model for a specific type.

        :param model_type: Type of model (haiku, sonnet, opus)
        :type model_type: str
        :param model_name: Name of the model
        :type model_name: str
        :return: True if successful, False otherwise
        :rtype: bool
        """
        if model_type not in ['haiku', 'sonnet', 'opus']:
            return False

        self.config['models'][model_type] = model_name
        self.save_config()
        return True

    def get_models(self) -> Dict[str, Optional[str]]:
        """
        Get all configured models.

        :return: Dictionary of model types and their names
        :rtype: Dict[str, Optional[str]]
        """
        return self.config['models']

    def get_available_models(self, provider_name: str) -> List[str]:
        """
        Get list of available models from a specific provider.

        :param provider_name: Name of the provider
        :type provider_name: str
        :return: List of available model names
        :rtype: List[str]
        """
        if provider_name not in self.config['providers']:
            return []

        return self.config['providers'][provider_name].get('models', [])

    def save_config_as(self, name: str, provider_name: str) -> None:
        """
        Save current configuration with a name.

        :param name: Name to save configuration as
        :type name: str
        :param provider_name: Name of the provider to associate with this config
        :type provider_name: str
        """
        normalized_name = normalize_config_name(name)
        self.config['configs'][normalized_name] = {
            'provider': provider_name,
            'models': self.config['models'].copy()
        }
        self.save_config()

    def load_config_by_name(self, name: str) -> dict:
        """
        Load a saved configuration by name.

        :param name: Name of configuration to load
        :type name: str
        :return: Dictionary of provider base URL, models, and API key info, or empty dict if not found
        :rtype: dict
        """
        if name not in self.config['configs']:
            return {}

        provider = self.config['configs'][name]['provider']

        # Check if provider exists
        if provider not in self.config['providers']:
            return {}

        provider_config = self.config['providers'][provider]

        return {
            'base_url': provider_config['base_url'],
            'models': self.config['configs'][name]['models'],
            'api_key': provider_config.get('api_key', ''),
            'api_key_type': provider_config.get('api_key_type', 'none')
        }

    def get_default_config_name(self) -> Optional[str]:
        """
        Get the name of the default configuration.

        :return: Name of the default configuration or None if not set
        :rtype: Optional[str]
        """
        return self.config.get('default_config')

    def set_default_config(self, name: str) -> None:
        """
        Set a configuration as default.

        :param name: Name of configuration to set as default
        :type name: str
        """
        self.config['default_config'] = name
        self.save_config()

    def set_default_if_just_one_config(self) -> None:
        """
        If there is only one saved configuration, set it as the default.
        """
        if len(self.config['configs']) == 1:
            only_config_name = list(self.config['configs'].keys())[0]
            self.config['default_config'] = only_config_name
            self.save_config()

    def get_environment_variables(self, config: dict) -> Dict[str, str]:
        """
        Get environment variables based on current configuration.

        :param config: Configuration dictionary
        :type config: dict
        :return: Dictionary of environment variables
        :rtype: Dict[str, str]
        """
        # Determine the API key value based on the API key type
        api_key = ""
        api_key_type = config.get('api_key_type', 'none')
        api_key_value = config.get('api_key', '')

        if api_key_type == 'direct':
            api_key = api_key_value
        elif api_key_type == 'envvar':
            # Get the actual API key from the environment variable
            import os
            api_key = os.environ.get(api_key_value, '')

        return {
            'ANTHROPIC_DEFAULT_HAIKU_MODEL': config['models']['haiku'],
            'ANTHROPIC_DEFAULT_SONNET_MODEL': config['models']['sonnet'],
            'ANTHROPIC_DEFAULT_OPUS_MODEL': config['models']['opus'],
            'ANTHROPIC_BASE_URL': config['base_url'],
            'ANTHROPIC_API_KEY': api_key,
            "ANTHROPIC_AUTH_TOKEN": "",
        }


# Convenience functions
def get_config_manager() -> ConfigManager:
    """
    Get a configuration manager instance.

    :return: Configuration manager instance
    :rtype: ConfigManager
    """
    return ConfigManager()
