import sys, os
import queue
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import is_supported, MODELS, SUPPORTED_EXTENSIONS, _parse_drop_paths

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


def test_queue_result_message():
    q = queue.Queue()
    q.put(("result", "hello world"))
    msg_type, payload = q.get_nowait()
    assert msg_type == "result"
    assert payload == "hello world"

def test_queue_error_message():
    q = queue.Queue()
    q.put(("error", "file not found"))
    msg_type, payload = q.get_nowait()
    assert msg_type == "error"
    assert "not found" in payload

def test_queue_progress_message():
    q = queue.Queue()
    q.put(("progress", "Загрузка модели small..."))
    msg_type, payload = q.get_nowait()
    assert msg_type == "progress"
    assert "small" in payload


def test_parse_single_plain_path():
    assert _parse_drop_paths("C:\\audio\\file.mp3") == ["C:\\audio\\file.mp3"]

def test_parse_single_braced_path():
    assert _parse_drop_paths("{C:\\path with spaces\\file.mp3}") == ["C:\\path with spaces\\file.mp3"]

def test_parse_multiple_braced_paths():
    result = _parse_drop_paths("{C:\\a.mp3} {C:\\b.wav}")
    assert result == ["C:\\a.mp3", "C:\\b.wav"]

def test_parse_empty_data():
    assert _parse_drop_paths("") == []

def test_parse_whitespace_only():
    assert _parse_drop_paths("   ") == []
