"""Utility functions for reading project version information."""

from importlib.metadata import PackageNotFoundError, version
from typing import Optional


def get_project_version() -> Optional[str]:
    """
    Read the project version from installed package metadata.

    :return: The project version as a string, or None if not found
    :rtype: Optional[str]
    """
    try:
        return version("claude-code-interceptor")
    except PackageNotFoundError:
        return None
