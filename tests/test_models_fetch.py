"""Tests for the models_fetch utility module."""

import json
import os
from unittest.mock import Mock, patch

import requests

from cci.utils.models_fetch import discover_models_endpoint, fetch_models, list_models, normalize_base_url


def load_fixture(filename):
    """Load a JSON fixture file."""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
    with open(fixture_path, 'r') as f:
        return json.load(f)


def test_normalize_base_url():
    """Test the normalize_base_url function."""
    # Test with trailing slash
    assert normalize_base_url("http://example.com/") == "http://example.com"

    # Test with /v1 path
    assert normalize_base_url("http://example.com/v1") == "http://example.com"

    # Test with /v1/ path
    assert normalize_base_url("http://example.com/v1/") == "http://example.com"

    # Test with base URL
    assert normalize_base_url("http://example.com") == "http://example.com"


def test_discover_models_endpoint_success():
    """Test discover_models_endpoint when it finds a working endpoint."""
    with patch('requests.get') as mock_get:
        # Mock successful response for /v1/models
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = discover_models_endpoint("http://example.com")
        assert result == "http://example.com/v1/models"


def test_discover_models_endpoint_fallback():
    """Test discover_models_endpoint falling back to /models."""
    with patch('requests.get') as mock_get:
        # Mock failure for /v1/models and success for /models
        def side_effect(url, timeout=None):
            mock_response = Mock()
            if url == "http://example.com/v1/models":
                raise requests.RequestException("Connection failed")
            elif url == "http://example.com/models":
                mock_response.status_code = 200
                return mock_response
            return mock_response

        mock_get.side_effect = side_effect

        result = discover_models_endpoint("http://example.com")
        assert result == "http://example.com/models"


def test_discover_models_endpoint_none():
    """Test discover_models_endpoint when no endpoints work."""
    with patch('requests.get') as mock_get:
        # Mock failures for all endpoints
        mock_get.side_effect = requests.RequestException("Connection failed")

        result = discover_models_endpoint("http://example.com")
        assert result is None


def test_fetch_models_success():
    """Test fetch_models with successful response."""
    with patch('cci.utils.models_fetch.discover_models_endpoint') as mock_discover, \
            patch('requests.get') as mock_get:

        # Mock discovery to return a URL
        mock_discover.return_value = "http://example.com/v1/models"

        # Load real models data
        models_data = load_fixture('models_response.json')

        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = models_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_models("http://example.com")
        assert result == models_data


def test_fetch_models_discovery_failed():
    """Test fetch_models when discovery fails."""
    with patch('cci.utils.models_fetch.discover_models_endpoint') as mock_discover:
        # Mock discovery to return None
        mock_discover.return_value = None

        result = fetch_models("http://example.com")
        assert result is None


def test_fetch_models_request_failed():
    """Test fetch_models when the request fails."""
    with patch('cci.utils.models_fetch.discover_models_endpoint') as mock_discover, \
            patch('requests.get') as mock_get:

        # Mock discovery to return a URL
        mock_discover.return_value = "http://example.com/v1/models"

        # Mock request exception
        mock_get.side_effect = requests.RequestException("Request failed")

        result = fetch_models("http://example.com")
        assert result is None


def test_list_models_openai_format():
    """Test list_models with OpenAI-like response format."""
    # Load real models data
    models_data = load_fixture('models_response.json')

    with patch('cci.utils.models_fetch.fetch_models') as mock_fetch:
        mock_fetch.return_value = models_data

        result = list_models("http://example.com")

        # Check that we get the expected model names
        expected_models = [
            "gpt-5.1", "gpt-5.1-codex", "gpt-5-mini", "gpt-5-pro", "gpt-5-nano",
            "claude-sonnet", "claude-haiku", "claude-opus", "qwen3-coder-480b",
            "GLM-4.5-Air", "Intellect3", "Minimax-M2", "Qwen3-30B-A3B-Thinking-2507",
            "Qwen3-Next-80B-A3B", "Qwen3-VL-8B", "gpt-oss-120b", "gpt-oss-20b",
            "nomic-embed-text-v2-moe"
        ]
        assert result == expected_models


def test_list_models_simple_list_format():
    """Test list_models with simple list format."""
    models_data = [{"id": "model1"}, {"id": "model2"}]

    with patch('cci.utils.models_fetch.fetch_models') as mock_fetch:
        mock_fetch.return_value = models_data

        result = list_models("http://example.com")
        assert result == ["model1", "model2"]


def test_list_models_string_list_format():
    """Test list_models with string list format."""
    models_data = ["model1", "model2"]

    with patch('cci.utils.models_fetch.fetch_models') as mock_fetch:
        mock_fetch.return_value = models_data

        result = list_models("http://example.com")
        assert result == ["model1", "model2"]


def test_list_models_empty_response():
    """Test list_models with empty response."""
    with patch('cci.utils.models_fetch.fetch_models') as mock_fetch:
        mock_fetch.return_value = None

        result = list_models("http://example.com")
        assert result == []


def test_list_models_invalid_format():
    """Test list_models with invalid response format."""
    models_data = {"unknown_key": "unknown_value"}

    with patch('cci.utils.models_fetch.fetch_models') as mock_fetch:
        mock_fetch.return_value = models_data

        result = list_models("http://example.com")
        assert result == []
