"""Utility functions for reading project version information."""

import os
import tomllib
from typing import Optional


def get_project_version() -> Optional[str]:
    """
    Read the project version from pyproject.toml.

    :return: The project version as a string, or None if not found
    :rtype: Optional[str]
    """
    # Get the project root directory (assuming this file is in cci/utils/)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    pyproject_path = os.path.join(project_root, "pyproject.toml")

    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        # Extract version from project metadata
        version = pyproject_data.get("project", {}).get("version")
        return version if version else None
    except (FileNotFoundError, tomllib.TOMLDecodeError, KeyError, Exception):
        # Return None if file not found, invalid TOML, version key missing, or any other error
        return None
