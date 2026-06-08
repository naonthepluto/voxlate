import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import is_supported, MODELS, SUPPORTED_EXTENSIONS

def test_supported_extensions():
    assert is_supported("audio.mp3")
    assert is_supported("recording.WAV")
    assert is_supported("video.mp4")
    assert not is_supported("document.pdf")
    assert not is_supported("image.png")
    assert not is_supported("noextension")

def test_models_list():
    assert "small" in MODELS
    assert "large-v3" in MODELS
    assert len(MODELS) == 5
