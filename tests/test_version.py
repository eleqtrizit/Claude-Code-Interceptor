"""Tests for the version utility module."""

from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

from cci.utils.version import get_project_version


def test_get_project_version_success():
    """Test successful retrieval of project version from package metadata."""
    with patch("cci.utils.version.version", return_value="0.1.3"):
        version = get_project_version()
        assert version == "0.1.3"


def test_get_project_version_package_not_found():
    """Test when package is not installed."""
    with patch("cci.utils.version.version", side_effect=PackageNotFoundError()):
        version = get_project_version()
        assert version is None
