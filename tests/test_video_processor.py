from unittest.mock import patch, MagicMock
from core.video_processor import sanitize_filename, download_youtube_video, extract_audio

# --- sanitize_filename ---
def test_sanitize_filename():
    assert sanitize_filename("My Video: #1.mp4") == "My_Video_1_mp4"
    assert sanitize_filename("a b/c?d") == "a_b_c_d"
    assert sanitize_filename("Test_123") == "Test_123"

# --- download_youtube_video ---
@patch("core.video_processor.YoutubeDL")
def test_download_youtube_video(mock_yt):
    mock_instance = MagicMock()
    mock_yt.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = {"title": "Sample Video"}
    mock_instance.prepare_filename.return_value = "downloads/Sample Video.mp4"

    from core.video_processor import download_youtube_video
    result = download_youtube_video("https://youtube.com/fake")

    assert result.endswith(".mp4")
    assert "Sample Video" in result

# --- extract_audio ---
@patch("core.video_processor.VideoFileClip")
def test_extract_audio(mock_clip):
    mock_audio = MagicMock()
    mock_clip.return_value.audio = mock_audio

    # Simulate audio write
    audio_path = extract_audio("fake_video.mp4")
    mock_audio.write_audiofile.assert_called_once()
    assert audio_path.endswith(".wav")