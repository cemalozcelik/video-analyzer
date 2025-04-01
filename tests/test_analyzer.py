from unittest.mock import patch, MagicMock
from core.analyzer import analyze_transcript

@patch("core.analyzer.get_openai_client")
def test_analyze_transcript_with_gpt(mock_get_client):
    # Setup attribute-style fake response
    fake_message = MagicMock()
    fake_message.content = "# Summary\n- Point 1\n- Point 2"

    fake_choice = MagicMock()
    fake_choice.message = fake_message

    fake_response = MagicMock()
    fake_response.choices = [fake_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = fake_response
    mock_get_client.return_value = mock_client

    result = analyze_transcript("This is a sample transcript.")
    
    assert isinstance(result, dict)
    assert "Summary" in result["result"]
