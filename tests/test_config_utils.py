"""Tests for the config_utils utility module."""

from claude_code_intercept.utils.config_utils import normalize_config_name


def test_normalize_config_name():
    """Test the normalize_config_name function."""
    # Test basic lowercase conversion
    assert normalize_config_name("TEST") == "test"

    # Test space replacement with dashes
    assert normalize_config_name("my config") == "my-config"

    # Test underscore replacement with dashes
    assert normalize_config_name("my_config") == "my-config"

    # Test combination of spaces and underscores
    assert normalize_config_name("my config_name") == "my-config-name"

    # Test removal of invalid characters
    assert normalize_config_name("my@config#name") == "myconfigname"

    # Test handling of numbers
    assert normalize_config_name("config123") == "config123"

    # Test handling of alphanumeric with dashes
    assert normalize_config_name("my-123-config") == "my-123-config"

    # Test removal of leading/trailing dashes
    assert normalize_config_name("-my-config-") == "my-config"

    # Test replacement of multiple consecutive dashes
    assert normalize_config_name("my---config") == "my-config"

    # Test complex example
    assert normalize_config_name("My Config_Name 123!") == "my-config-name-123"

    # Test empty string
    assert normalize_config_name("") == ""

    # Test only invalid characters
    assert normalize_config_name("@#$%") == ""

    # Test only dashes
    assert normalize_config_name("---") == ""
