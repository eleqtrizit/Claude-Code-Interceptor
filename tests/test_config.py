"""Tests for the configuration management module."""

import json
from unittest.mock import patch

import pytest

from cci.config import ConfigManager, get_config_manager


class TestConfigManager:
    """Test suite for the ConfigManager class."""

    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """Create a temporary configuration directory."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        return config_dir

    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """Create a ConfigManager instance with a temporary directory."""
        return ConfigManager(str(temp_config_dir))

    def test_init_with_default_directory(self, tmp_path):
        """Test initialization with default directory."""
        # Create a mock home directory structure
        mock_home = tmp_path / "home"
        mock_home.mkdir()

        with patch("cci.config.Path.home") as mock_home_func:
            mock_home_func.return_value = mock_home
            cm = ConfigManager()
            expected_path = mock_home / ".config" / "cci"
            assert cm.config_dir == expected_path
            assert cm.config_file == expected_path / "config.json"

    def test_init_with_custom_directory(self, temp_config_dir):
        """Test initialization with custom directory."""
        cm = ConfigManager(str(temp_config_dir))
        assert cm.config_dir == temp_config_dir
        assert cm.config_file == temp_config_dir / "config.json"

    def test_load_config_creates_directories(self, temp_config_dir):
        """Test that _load_config creates directories if they don't exist."""
        # Create a nested directory path
        nested_dir = temp_config_dir / "nested" / "config"
        cm = ConfigManager(str(nested_dir))

        # This should create the directories
        config = cm._load_config()

        # Check that directories were created
        assert nested_dir.exists()
        assert isinstance(config, dict)
        assert "providers" in config

    def test_load_config_returns_default_when_no_file(self, temp_config_dir):
        """Test that _load_config returns default config when no file exists."""
        cm = ConfigManager(str(temp_config_dir))
        config = cm._load_config()

        # Check default config structure
        assert "providers" in config
        assert "models" in config
        assert "configs" in config
        assert "default_config" in config
        assert config["providers"] == {}
        assert config["models"] == {"haiku": None, "sonnet": None, "opus": None}
        assert config["configs"] == {}
        assert config["default_config"] is None

    def test_load_config_reads_existing_file(self, temp_config_dir):
        """Test that _load_config reads existing config file."""
        # Create a config file with test data
        config_data = {
            "providers": {"test": {"base_url": "http://test.com", "models": ["model1"]}},
            "models": {"haiku": "test-haiku", "sonnet": "test-sonnet", "opus": "test-opus"},
            "configs": {"test-config": {"provider": "test", "models": {"haiku": "test-haiku"}}},
            "default_config": "test-config"
        }

        config_file = temp_config_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        cm = ConfigManager(str(temp_config_dir))
        config = cm._load_config()

        assert config == config_data

    def test_load_config_handles_corrupted_file(self, temp_config_dir):
        """Test that _load_config handles corrupted config file."""
        # Create a corrupted config file
        config_file = temp_config_dir / "config.json"
        with open(config_file, "w") as f:
            f.write("invalid json")

        cm = ConfigManager(str(temp_config_dir))
        config = cm._load_config()

        # Should return default config despite corrupted file
        assert "providers" in config
        assert "models" in config
        assert config["providers"] == {}
        assert config["models"] == {"haiku": None, "sonnet": None, "opus": None}

    def test_save_config_creates_file(self, config_manager):
        """Test that save_config creates a config file."""
        # Modify the config
        config_manager.config["providers"]["test"] = {
            "base_url": "http://test.com",
            "models": ["model1"]
        }

        # Save the config
        config_manager.save_config()

        # Check that file was created
        assert config_manager.config_file.exists()

        # Check that file contains the correct data
        with open(config_manager.config_file, "r") as f:
            saved_config = json.load(f)

        assert saved_config["providers"]["test"]["base_url"] == "http://test.com"

    def test_add_provider_success(self, config_manager):
        """Test successful addition of a provider."""
        with patch("cci.config.fetch_models") as mock_fetch, \
                patch("cci.config.list_models") as mock_list:

            # Mock the API responses
            mock_fetch.return_value = {"data": [{"id": "model1"}, {"id": "model2"}]}
            mock_list.return_value = ["model1", "model2"]

            # Add provider
            result = config_manager.add_provider("test-provider", "http://test.com/v1")

            # Check results
            assert result is True
            assert "test-provider" in config_manager.config["providers"]
            assert config_manager.config["providers"]["test-provider"]["base_url"] == "http://test.com/v1"
            assert config_manager.config["providers"]["test-provider"]["models"] == ["model1", "model2"]

    def test_add_provider_failure(self, config_manager):
        """Test failure when adding a provider."""
        with patch("cci.config.fetch_models") as mock_fetch:
            # Mock an exception
            mock_fetch.side_effect = Exception("Connection failed")

            # Try to add provider
            result = config_manager.add_provider("test-provider", "http://test.com/v1")

            # Check results
            assert result is False
            assert "test-provider" not in config_manager.config["providers"]

    def test_remove_provider(self, config_manager):
        """Test removal of a provider."""
        # First add a provider and some configs
        config_manager.config["providers"]["test-provider"] = {
            "base_url": "http://test.com/v1",
            "models": ["model1"]
        }

        config_manager.config["configs"]["test-config"] = {
            "provider": "test-provider",
            "models": {"haiku": "model1"}
        }

        config_manager.config["default_config"] = "test-config"

        # Remove the provider
        config_manager.remove_provider("test-provider")

        # Check that provider and associated configs were removed
        assert "test-provider" not in config_manager.config["providers"]
        assert "test-config" not in config_manager.config["configs"]
        assert config_manager.config["default_config"] is None

    def test_remove_config_success(self, config_manager):
        """Test successful removal of a configuration."""
        # Add a config
        config_manager.config["configs"]["test-config"] = {
            "provider": "test-provider",
            "models": {"haiku": "model1"}
        }

        # Remove the config
        result = config_manager.remove_config("test-config")

        # Check results
        assert result is True
        assert "test-config" not in config_manager.config["configs"]

    def test_remove_config_not_found(self, config_manager):
        """Test removal of non-existent configuration."""
        result = config_manager.remove_config("non-existent")
        assert result is False

    def test_remove_config_resets_default(self, config_manager):
        """Test that removing default config resets default_config."""
        # Set up a default config
        config_manager.config["configs"]["default-test"] = {
            "provider": "test-provider",
            "models": {"haiku": "model1"}
        }
        config_manager.config["default_config"] = "default-test"

        # Remove the default config
        result = config_manager.remove_config("default-test")

        # Check results
        assert result is True
        assert config_manager.config["default_config"] is None

    def test_check_and_update_default_config_exists(self, config_manager):
        """Test check_and_update_default_config when default config exists."""
        # Set up a valid default config
        config_manager.config["configs"]["test-config"] = {
            "provider": "test-provider",
            "models": {"haiku": "model1"}
        }
        config_manager.config["default_config"] = "test-config"

        result = config_manager.check_and_update_default_config()

        # Should return True since default config exists
        assert result is True
        assert config_manager.config["default_config"] == "test-config"

    def test_check_and_update_default_config_missing(self, config_manager):
        """Test check_and_update_default_config when default config is missing."""
        # Set up a missing default config
        config_manager.config["default_config"] = "missing-config"

        result = config_manager.check_and_update_default_config()

        # Should reset default_config to None and return False
        assert result is False
        assert config_manager.config["default_config"] is None

    def test_update_provider_success(self, config_manager):
        """Test successful update of provider models."""
        # Add a provider first
        config_manager.config["providers"]["test-provider"] = {
            "base_url": "http://test.com/v1",
            "models": ["old-model"]
        }

        with patch("cci.config.list_models") as mock_list:
            # Mock the API response
            mock_list.return_value = ["new-model1", "new-model2"]

            # Update the provider
            result = config_manager.update_provider("test-provider")

            # Check results
            assert result is True
            assert config_manager.config["providers"]["test-provider"]["models"] == ["new-model1", "new-model2"]

    def test_update_provider_not_found(self, config_manager):
        """Test update of non-existent provider."""
        result = config_manager.update_provider("non-existent")
        assert result is False

    def test_update_provider_failure(self, config_manager):
        """Test failure when updating provider."""
        # Add a provider first
        config_manager.config["providers"]["test-provider"] = {
            "base_url": "http://test.com/v1",
            "models": ["old-model"]
        }

        with patch("cci.config.list_models") as mock_list:
            # Mock an exception
            mock_list.side_effect = Exception("Connection failed")

            # Try to update the provider
            result = config_manager.update_provider("test-provider")

            # Check results
            assert result is False

    def test_get_configs_for_provider(self, config_manager):
        """Test getting configurations for a specific provider."""
        # Add some configs
        config_manager.config["configs"]["config1"] = {
            "provider": "provider1",
            "models": {"haiku": "model1"}
        }
        config_manager.config["configs"]["config2"] = {
            "provider": "provider1",
            "models": {"sonnet": "model2"}
        }
        config_manager.config["configs"]["config3"] = {
            "provider": "provider2",
            "models": {"opus": "model3"}
        }

        # Get configs for provider1
        configs = config_manager.get_configs_for_provider("provider1")

        # Check results
        assert len(configs) == 2
        assert "config1" in configs
        assert "config2" in configs
        assert "config3" not in configs

    def test_set_model_success(self, config_manager):
        """Test successful setting of a model."""
        result = config_manager.set_model("haiku", "claude-3-haiku-20240307")

        # Check results
        assert result is True
        assert config_manager.config["models"]["haiku"] == "claude-3-haiku-20240307"

    def test_set_model_invalid_type(self, config_manager):
        """Test setting model with invalid type."""
        # Store original models
        original_models = config_manager.config["models"].copy()

        result = config_manager.set_model("invalid-type", "some-model")

        # Check results
        assert result is False
        # Models should remain unchanged
        assert config_manager.config["models"] == original_models

    def test_get_models(self, config_manager):
        """Test getting all models."""
        # Set some models
        config_manager.config["models"]["haiku"] = "test-haiku"
        config_manager.config["models"]["sonnet"] = "test-sonnet"

        models = config_manager.get_models()

        # Check results
        assert models["haiku"] == "test-haiku"
        assert models["sonnet"] == "test-sonnet"
        assert models["opus"] is None

    def test_get_available_models_success(self, config_manager):
        """Test getting available models from a provider."""
        # Add a provider with models
        config_manager.config["providers"]["test-provider"] = {
            "base_url": "http://test.com/v1",
            "models": ["model1", "model2", "model3"]
        }

        models = config_manager.get_available_models("test-provider")

        # Check results
        assert models == ["model1", "model2", "model3"]

    def test_get_available_models_not_found(self, config_manager):
        """Test getting available models from non-existent provider."""
        models = config_manager.get_available_models("non-existent")
        assert models == []

    def test_save_config_as(self, config_manager):
        """Test saving current configuration with a name."""
        # Set some models
        config_manager.config["models"]["haiku"] = "test-haiku"
        config_manager.config["models"]["sonnet"] = "test-sonnet"

        # Save config as
        config_manager.save_config_as("My Test Config", "test-provider")

        # Check results
        assert "my-test-config" in config_manager.config["configs"]
        assert config_manager.config["configs"]["my-test-config"]["provider"] == "test-provider"
        assert config_manager.config["configs"]["my-test-config"]["models"]["haiku"] == "test-haiku"
        assert config_manager.config["configs"]["my-test-config"]["models"]["sonnet"] == "test-sonnet"

    def test_load_config_by_name_success(self, config_manager):
        """Test successful loading of a saved configuration."""
        # Add a saved config
        config_manager.config["configs"]["test-config"] = {
            "provider": "test-provider",
            "models": {"haiku": "loaded-haiku", "sonnet": "loaded-sonnet", "opus": "loaded-opus"}
        }

        # Add the provider that the config references
        config_manager.config["providers"]["test-provider"] = {
            "base_url": "http://test.com/v1",
            "models": ["model1"]
        }

        # Load the saved config
        result = config_manager.load_config_by_name("test-config")

        # Check results - should return a dict with base_url and models
        assert isinstance(result, dict)
        assert result["base_url"] == "http://test.com/v1"
        assert result["models"]["haiku"] == "loaded-haiku"
        assert result["models"]["sonnet"] == "loaded-sonnet"
        assert result["models"]["opus"] == "loaded-opus"

    def test_load_config_by_name_not_found(self, config_manager):
        """Test loading non-existent configuration."""
        result = config_manager.load_config_by_name("non-existent")
        assert result == {}

    def test_set_default_config(self, config_manager):
        """Test setting a configuration as default."""
        config_manager.set_default_config("test-config")
        assert config_manager.config["default_config"] == "test-config"

    def test_get_environment_variables_with_provider(self, config_manager):
        """Test getting environment variables with a specific provider."""
        # Create a config dictionary as the method now expects
        config = {
            "base_url": "http://test.com/v1",
            "models": {
                "haiku": "test-haiku",
                "sonnet": "test-sonnet",
                "opus": "test-opus"
            },
            "api_key": "",
            "api_key_type": "none"
        }

        env_vars = config_manager.get_environment_variables(config)

        # Check results
        assert env_vars["ANTHROPIC_BASE_URL"] == "http://test.com/v1"
        assert env_vars["ANTHROPIC_API_KEY"] == ""
        assert env_vars["ANTHROPIC_AUTH_TOKEN"] == ""
        assert env_vars["ANTHROPIC_DEFAULT_HAIKU_MODEL"] == "test-haiku"
        assert env_vars["ANTHROPIC_DEFAULT_SONNET_MODEL"] == "test-sonnet"
        assert env_vars["ANTHROPIC_DEFAULT_OPUS_MODEL"] == "test-opus"

    def test_get_environment_variables_without_provider(self, config_manager):
        """Test getting environment variables without specifying a provider."""
        # Create a config dictionary with minimal information
        config = {
            "base_url": None,  # No base URL
            "models": {
                "haiku": "test-haiku",
                "sonnet": None,
                "opus": None
            },
            "api_key": "",
            "api_key_type": "none"
        }

        env_vars = config_manager.get_environment_variables(config)

        # Check results
        assert env_vars["ANTHROPIC_BASE_URL"] is None
        assert env_vars["ANTHROPIC_API_KEY"] == ""
        assert env_vars["ANTHROPIC_DEFAULT_HAIKU_MODEL"] == "test-haiku"
        assert env_vars["ANTHROPIC_DEFAULT_SONNET_MODEL"] is None
        assert env_vars["ANTHROPIC_DEFAULT_OPUS_MODEL"] is None

    def test_get_environment_variables_nonexistent_provider(self, config_manager):
        """Test getting environment variables with non-existent provider."""
        # Create a config dictionary with minimal information
        config = {
            "base_url": None,
            "models": {
                "haiku": None,
                "sonnet": None,
                "opus": None
            },
            "api_key": "",
            "api_key_type": "none"
        }

        env_vars = config_manager.get_environment_variables(config)

        # Should not have base URL but might have model vars
        assert env_vars["ANTHROPIC_BASE_URL"] is None
        assert env_vars["ANTHROPIC_API_KEY"] == ""

    def test_get_environment_variables_with_direct_api_key(self, config_manager):
        """Test getting environment variables with a direct API key."""
        # Create a config dictionary with a direct API key
        config = {
            "base_url": "http://test.com/v1",
            "models": {
                "haiku": "test-haiku",
                "sonnet": "test-sonnet",
                "opus": "test-opus"
            },
            "api_key": "test-api-key",
            "api_key_type": "direct"
        }

        env_vars = config_manager.get_environment_variables(config)

        # Check results
        assert env_vars["ANTHROPIC_BASE_URL"] == "http://test.com/v1"
        assert env_vars["ANTHROPIC_API_KEY"] == "test-api-key"
        assert env_vars["ANTHROPIC_DEFAULT_HAIKU_MODEL"] == "test-haiku"
        assert env_vars["ANTHROPIC_DEFAULT_SONNET_MODEL"] == "test-sonnet"
        assert env_vars["ANTHROPIC_DEFAULT_OPUS_MODEL"] == "test-opus"

    def test_get_environment_variables_with_envvar_api_key(self, config_manager):
        """Test getting environment variables with an environment variable API key."""
        # Create a config dictionary with an environment variable API key
        config = {
            "base_url": "http://test.com/v1",
            "models": {
                "haiku": "test-haiku",
                "sonnet": "test-sonnet",
                "opus": "test-opus"
            },
            "api_key": "TEST_API_KEY_VAR",
            "api_key_type": "envvar"
        }

        # Mock the environment variable
        import os
        original_value = os.environ.get("TEST_API_KEY_VAR")
        os.environ["TEST_API_KEY_VAR"] = "actual-api-key-from-env"

        try:
            env_vars = config_manager.get_environment_variables(config)

            # Check results
            assert env_vars["ANTHROPIC_BASE_URL"] == "http://test.com/v1"
            assert env_vars["ANTHROPIC_API_KEY"] == "actual-api-key-from-env"
            assert env_vars["ANTHROPIC_DEFAULT_HAIKU_MODEL"] == "test-haiku"
            assert env_vars["ANTHROPIC_DEFAULT_SONNET_MODEL"] == "test-sonnet"
            assert env_vars["ANTHROPIC_DEFAULT_OPUS_MODEL"] == "test-opus"
        finally:
            # Restore original environment
            if original_value is not None:
                os.environ["TEST_API_KEY_VAR"] = original_value
            else:
                os.environ.pop("TEST_API_KEY_VAR", None)

    def test_get_environment_variables_with_missing_envvar_api_key(self, config_manager):
        """Test getting environment variables with a missing environment variable API key."""
        # Create a config dictionary with a missing environment variable API key
        config = {
            "base_url": "http://test.com/v1",
            "models": {
                "haiku": "test-haiku",
                "sonnet": "test-sonnet",
                "opus": "test-opus"
            },
            "api_key": "MISSING_API_KEY_VAR",
            "api_key_type": "envvar"
        }

        # Ensure the environment variable is not set
        import os
        original_value = os.environ.get("MISSING_API_KEY_VAR")
        if original_value is not None:
            del os.environ["MISSING_API_KEY_VAR"]

        try:
            env_vars = config_manager.get_environment_variables(config)

            # Check results - should be empty string since env var doesn't exist
            assert env_vars["ANTHROPIC_BASE_URL"] == "http://test.com/v1"
            assert env_vars["ANTHROPIC_API_KEY"] == ""
            assert env_vars["ANTHROPIC_DEFAULT_HAIKU_MODEL"] == "test-haiku"
            assert env_vars["ANTHROPIC_DEFAULT_SONNET_MODEL"] == "test-sonnet"
            assert env_vars["ANTHROPIC_DEFAULT_OPUS_MODEL"] == "test-opus"
        finally:
            # Restore original environment
            if original_value is not None:
                os.environ["MISSING_API_KEY_VAR"] = original_value


def test_get_config_manager():
    """Test the get_config_manager convenience function."""
    cm = get_config_manager()
    assert isinstance(cm, ConfigManager)
