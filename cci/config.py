"""Configuration management for Claude Code Interceptor."""

import json
import os
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
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Return default config if file is corrupted
                pass

        # Return default config
        return {
            'providers': {},
            'current_provider': None,
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

    def add_provider(self, name: str, base_url: str) -> bool:
        """
        Add a new model provider.

        :param name: Name of the provider
        :type name: str
        :param base_url: Base URL of the provider
        :type base_url: str
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
                'models': model_list
            }

            # Set as current provider if none exists
            if self.config['current_provider'] is None:
                self.config['current_provider'] = name

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

            # Reset current provider if it was the one removed
            if self.config['current_provider'] == name:
                self.config['current_provider'] = None
                # Clear model selections
                self.config['models'] = {
                    'haiku': None,
                    'sonnet': None,
                    'opus': None
                }

            self.save_config()

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

    def set_current_provider(self, name: str) -> bool:
        """
        Set the current provider.

        :param name: Name of the provider to set as current
        :type name: str
        :return: True if successful, False otherwise
        :rtype: bool
        """
        if name not in self.config['providers']:
            return False

        self.config['current_provider'] = name
        self.save_config()
        return True

    def get_current_provider(self) -> Optional[Dict[str, Any]]:
        """
        Get the current provider.

        :return: Current provider information or None
        :rtype: Optional[Dict[str, Any]]
        """
        if self.config['current_provider'] is None:
            return None

        return self.config['providers'].get(self.config['current_provider'])

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

    def get_available_models(self) -> List[str]:
        """
        Get list of available models from current provider.

        :return: List of available model names
        :rtype: List[str]
        """
        provider = self.get_current_provider()
        if provider is None:
            return []

        return provider.get('models', [])

    def save_config_as(self, name: str) -> None:
        """
        Save current configuration with a name.

        :param name: Name to save configuration as
        :type name: str
        """
        normalized_name = normalize_config_name(name)
        self.config['configs'][normalized_name] = {
            'provider': self.config['current_provider'],
            'models': self.config['models'].copy()
        }
        self.save_config()

    def load_config_by_name(self, name: str) -> bool:
        """
        Load a saved configuration by name.

        :param name: Name of configuration to load
        :type name: str
        :return: True if successful, False otherwise
        :rtype: bool
        """
        if name not in self.config['configs']:
            return False

        config = self.config['configs'][name]
        self.config['current_provider'] = config['provider']
        self.config['models'] = config['models'].copy()
        self.save_config()
        return True

    def set_default_config(self, name: str) -> None:
        """
        Set a configuration as default.

        :param name: Name of configuration to set as default
        :type name: str
        """
        self.config['default_config'] = name
        self.save_config()

    def load_default_config(self) -> bool:
        """
        Load the default configuration.

        :return: True if successful, False otherwise
        :rtype: bool
        """
        if self.config['default_config'] is None:
            return False

        return self.load_config_by_name(self.config['default_config'])

    def get_environment_variables(self) -> Dict[str, str]:
        """
        Get environment variables based on current configuration.

        :return: Dictionary of environment variables
        :rtype: Dict[str, str]
        """
        env_vars = {}

        # Get current provider
        provider = self.get_current_provider()
        if provider is not None:
            env_vars['ANTHROPIC_BASE_URL'] = provider['base_url']

            # Unset AUTH_TOKEN if it exists in environment
            if 'ANTHROPIC_AUTH_TOKEN' in os.environ:
                env_vars['ANTHROPIC_AUTH_TOKEN'] = ''

        # Set model environment variables
        models = self.get_models()
        if models['haiku']:
            env_vars['ANTHROPIC_DEFAULT_HAIKU_MODEL'] = models['haiku']
        if models['sonnet']:
            env_vars['ANTHROPIC_DEFAULT_SONNET_MODEL'] = models['sonnet']
        if models['opus']:
            env_vars['ANTHROPIC_DEFAULT_OPUS_MODEL'] = models['opus']

        return env_vars


# Convenience functions
def get_config_manager() -> ConfigManager:
    """
    Get a configuration manager instance.

    :return: Configuration manager instance
    :rtype: ConfigManager
    """
    return ConfigManager()


def apply_configuration(env: Dict[str, str]) -> None:
    """
    Apply configuration to environment variables.

    :param env: Environment variables to set
    :type env: Dict[str, str]
    """
    for key, value in env.items():
        if value == '':
            # Unset variable if value is empty string
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
