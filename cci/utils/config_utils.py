"""Utility functions for configuration management."""

import re


def normalize_config_name(name: str) -> str:
    """
    Normalize a configuration name according to specified rules.

    Rules:
    1. Lowercase the name
    2. Replace spaces with dashes
    3. Replace underscores with dashes
    4. Only allow 0-9, a-z, and - (dash)

    :param name: The configuration name to normalize
    :type name: str
    :return: The normalized configuration name
    :rtype: str
    """
    # Convert to lowercase
    normalized = name.lower()

    # Replace spaces and underscores with dashes
    normalized = normalized.replace(' ', '-').replace('_', '-')

    # Remove any characters that are not alphanumeric or dash
    normalized = re.sub(r'[^a-z0-9\-]', '', normalized)

    # Remove leading/trailing dashes
    normalized = normalized.strip('-')

    # Replace multiple consecutive dashes with a single dash
    normalized = re.sub(r'-+', '-', normalized)

    return normalized
