"""Unit tests for llm_client.py covering initialization, model listing, connection check, and prompt generation."""

import pytest
from unittest.mock import patch, MagicMock
from llm_client import OllamaClient

@patch("llm_client.requests.Session", autospec=True)
def test_initialization_and_connection(mock_session):
    # Setup mock
    mock_instance = mock_session.return_value
    mock_instance.get.return_value.status_code = 200
    mock_instance.get.return_value.json.return_value = {"models": [{"name": "qwen2.5:32b"}]}

    client = OllamaClient()
    assert client.base_url
    assert client.model
    # Should say connection is present
    mock_instance.get.return_value.raise_for_status = MagicMock()
    assert client.check_connection() == True

@patch("llm_client.requests.Session", autospec=True)
def test_list_models(mock_session):
    mock_instance = mock_session.return_value
    mock_instance.get.return_value.status_code = 200
    mock_instance.get.return_value.json.return_value = {"models": [{"name": "qwen2.5:32b"}, {"name": "gemma2:9b"}]}
    client = OllamaClient()
    models = client.list_models()
    assert "qwen2.5:32b" in models
    assert "gemma2:9b" in models

@patch("llm_client.requests.Session", autospec=True)
def test_generate_prompt_and_failures(mock_session):
    mock_instance = mock_session.return_value
    mock_post = mock_instance.post
    # Provide a dummy JSON response for successful case
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"response": "print('hello')"}
    client = OllamaClient()
    result = client.generate(prompt="Print hello", system_prompt=None, temperature=0.2)
    assert "hello" in result

    # Now for the failure case: empty prompt
    with pytest.raises(ValueError):
        client.generate(prompt="  ")

    with pytest.raises(ValueError):
        client.generate(prompt="test", temperature=2)

    # HTTP error handling
    mock_post.side_effect = Exception("HTTP error!")
    with pytest.raises(Exception):
        client.generate(prompt="fail")
