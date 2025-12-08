"""Tests for the version utility module."""

from unittest.mock import patch

from cci.utils.version import get_project_version


def test_get_project_version_success():
    """Test successful retrieval of project version."""
    # Mock the tomllib.load function to return a dict with version
    with patch("cci.utils.version.tomllib.load", return_value={"project": {"version": "0.1.3"}}):
        with patch("cci.utils.version.open"):
            version = get_project_version()
            assert version == "0.1.3"


def test_get_project_version_no_version():
    """Test when version is not present in pyproject.toml."""
    # Mock the tomllib.load function to return a dict without version
    with patch("cci.utils.version.tomllib.load", return_value={"project": {}}):
        with patch("cci.utils.version.open"):
            version = get_project_version()
            assert version is None


def test_get_project_version_file_not_found():
    """Test when pyproject.toml file is not found."""
    with patch("cci.utils.version.open", side_effect=FileNotFoundError()):
        version = get_project_version()
        assert version is None


def test_get_project_version_invalid_toml():
    """Test when pyproject.toml contains invalid TOML."""
    with patch("cci.utils.version.open"):
        # Mock the tomllib.load function to raise an exception
        with patch("cci.utils.version.tomllib.load", side_effect=Exception("TOML decode error")):
            version = get_project_version()
            assert version is None
