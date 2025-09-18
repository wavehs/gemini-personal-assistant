import pytest
from unittest.mock import patch, MagicMock
import json

from core.intent_detector import detect_intent

@pytest.mark.asyncio
@patch('core.intent_detector.model')
async def test_detect_intent_success(mock_model):
    """
    Tests the detect_intent function with a successful API call.
    """
    mock_response = MagicMock()
    mock_response.text = '```json\n{"intent": "weather", "entities": {"location": "Paris"}}\n```'
    mock_model.generate_content.return_value = mock_response

    text = "What's the weather in Paris?"
    result = await detect_intent(text)

    assert result == {"intent": "weather", "entities": {"location": "Paris"}}
    mock_model.generate_content.assert_called_once()

@pytest.mark.asyncio
@patch('core.intent_detector.model', None)
async def test_detect_intent_no_model():
    """
    Tests the detect_intent function when the model is not initialized.
    """
    text = "What's the weather in Paris?"
    result = await detect_intent(text)

    assert result == {"intent": "error", "entities": {"message": "Gemini model not initialized"}}

@pytest.mark.asyncio
@patch('core.intent_detector.model')
async def test_detect_intent_api_error(mock_model):
    """
    Tests the detect_intent function when the API call raises an exception.
    """
    mock_model.generate_content.side_effect = Exception("API Error")

    text = "What's the weather in Paris?"
    result = await detect_intent(text)

    assert result == {"intent": "error", "entities": {"message": "API Error"}}

@pytest.mark.asyncio
@patch('core.intent_detector.model')
async def test_detect_intent_json_error(mock_model):
    """
    Tests the detect_intent function when the API returns invalid JSON.
    """
    mock_response = MagicMock()
    mock_response.text = 'This is not JSON'
    mock_model.generate_content.return_value = mock_response

    text = "What's the weather in Paris?"
    result = await detect_intent(text)

    assert result['intent'] == 'error'
    assert 'message' in result['entities']
