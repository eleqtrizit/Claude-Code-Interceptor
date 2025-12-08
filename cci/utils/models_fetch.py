"""Utility functions for fetching models from API endpoints."""

from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests


def normalize_base_url(base_url: str) -> str:
    """
    Normalize the base URL by removing trailing slashes and extracting the base path.

    :param base_url: The base URL to normalize
    :type base_url: str
    :return: Normalized base URL
    :rtype: str
    """
    # Remove trailing slashes
    base_url = base_url.rstrip('/')

    # Parse the URL to check if it ends with /v1 or /v1/
    parsed = urlparse(base_url)
    path = parsed.path

    # If the path ends with /v1, remove it to get the true base URL
    if path.endswith('/v1'):
        # Remove /v1 from the end
        base_path = path[:-3]  # Remove '/v1'
        # Reconstruct URL without /v1
        normalized = parsed._replace(path=base_path).geturl()
        return normalized.rstrip('/')

    return base_url


def discover_models_endpoint(base_url: str) -> Optional[str]:
    """
    Discover the models endpoint by trying different paths.

    :param base_url: The base URL to test
    :type base_url: str
    :return: The working models endpoint URL or None if not found
    :rtype: Optional[str]
    """
    # Normalize the base URL first
    normalized_base = normalize_base_url(base_url)

    # Test paths in order of preference
    test_paths = [
        '/v1/models',
        '/models'
    ]

    for path in test_paths:
        endpoint_url = urljoin(normalized_base + '/', path.lstrip('/'))
        try:
            response = requests.get(endpoint_url, timeout=10)
            # Check if the response is successful
            if response.status_code == 200:
                return endpoint_url
        except requests.RequestException:
            # Continue to next path if this one fails
            continue

    return None


def fetch_models(base_url: str) -> Optional[Dict]:
    """
    Fetch models from the /v1/models endpoint.

    :param base_url: The base URL to fetch models from
    :type base_url: str
    :return: Dictionary containing models data or None if failed
    :rtype: Optional[Dict]
    """
    # Discover the correct models endpoint
    models_endpoint = discover_models_endpoint(base_url)

    if not models_endpoint:
        return None

    try:
        response = requests.get(models_endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def list_models(base_url: str) -> List[str]:
    """
    List available models from the API endpoint.

    :param base_url: The base URL of the API
    :type base_url: str
    :return: List of model names
    :rtype: List[str]
    """
    models_data = fetch_models(base_url)

    if not models_data:
        return []

    # Extract model names based on common API response formats
    model_names = []

    # Handle OpenAI-like response format
    if 'data' in models_data and isinstance(models_data['data'], list):
        for model in models_data['data']:
            if isinstance(model, dict) and 'id' in model:
                model_names.append(model['id'])

    # Handle other common formats
    elif 'models' in models_data and isinstance(models_data['models'], list):
        for model in models_data['models']:
            if isinstance(model, dict) and 'id' in model:
                model_names.append(model['id'])
            elif isinstance(model, str):
                model_names.append(model)

    # Handle simple list format
    elif isinstance(models_data, list):
        for model in models_data:
            if isinstance(model, dict) and 'id' in model:
                model_names.append(model['id'])
            elif isinstance(model, str):
                model_names.append(model)

    return model_names
