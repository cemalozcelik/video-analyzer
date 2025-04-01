import pytest
from unittest.mock import patch, MagicMock
from core.transcriber import transcribe_audio, get_chunks

@patch("core.transcriber.AudioSegment")
@patch("core.transcriber.os.path.getsize")
def test_get_chunks(mock_getsize, mock_audio):
    # Fake audio 10 MB, 100 seconds long
    mock_getsize.return_value = 10 * 1024 * 1024
    fake_audio = MagicMock()
    fake_audio.__len__.return_value = 100000  # 100 sec in ms
    mock_audio.from_file.return_value = fake_audio

    chunks = get_chunks("fake_audio.wav", target_mb=2)
    assert len(chunks) > 1

@patch("core.transcriber.client.audio.transcriptions.create")
@patch("core.transcriber.AudioSegment")
@patch("core.transcriber.os.path.getsize")
def test_transcribe_audio_chunked(mock_getsize, mock_audio, mock_create):
    mock_getsize.return_value = 30 * 1024 * 1024  # > 25 MB triggers chunking
    fake_audio = MagicMock()
    fake_audio.__len__.return_value = 100000  # duration in ms
    fake_audio.__getitem__.side_effect = lambda s: fake_audio
    mock_audio.from_file.return_value = fake_audio

    mock_create.return_value = MagicMock(text="chunk result")

    result = transcribe_audio("big_audio.wav")
    assert "chunk result" in result