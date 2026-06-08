import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
from faster_whisper import WhisperModel

MODELS = ["tiny", "base", "small", "medium", "large-v3"]
SUPPORTED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus",
    ".mp4", ".mkv", ".webm", ".avi", ".mov"
}

def is_supported(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in SUPPORTED_EXTENSIONS


class AppWindow:
    def __init__(self, root):
        pass  # implemented in later tasks


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = AppWindow(root)
    root.mainloop()
