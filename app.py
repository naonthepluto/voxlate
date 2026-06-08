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
    def __init__(self, root: TkinterDnD.Tk):
        self.root = root
        self.root.title("Voxlate — Транскрипция аудио")
        self.root.geometry("700x520")
        self.root.resizable(True, True)
        self.root.configure(bg="#1e1e2e")

        self._queue: queue.Queue = queue.Queue()
        self._model_cache: dict = {}  # {"model_name": WhisperModel instance}
        self._worker: threading.Thread | None = None

        self._build_drop_zone()
        self._build_controls()
        self._build_text_area()
        self._poll_queue()

    # ── Drop zone ────────────────────────────────────────────────────────────

    def _build_drop_zone(self):
        self.drop_frame = tk.Frame(
            self.root, bg="#313244", bd=2, relief="ridge", height=130
        )
        self.drop_frame.pack(fill="x", padx=16, pady=(16, 8))
        self.drop_frame.pack_propagate(False)

        self.drop_label = tk.Label(
            self.drop_frame,
            text="Перетащи аудиофайл сюда",
            font=("Segoe UI", 14),
            fg="#cdd6f4",
            bg="#313244",
        )
        self.drop_label.pack(expand=True)

        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self._on_drop)
        self.drop_frame.dnd_bind("<<DragEnter>>", self._on_drag_enter)
        self.drop_frame.dnd_bind("<<DragLeave>>", self._on_drag_leave)

    # ── Controls ─────────────────────────────────────────────────────────────

    def _build_controls(self):
        ctrl = tk.Frame(self.root, bg="#1e1e2e")
        ctrl.pack(fill="x", padx=16, pady=(0, 8))

        tk.Label(ctrl, text="Модель:", fg="#a6adc8", bg="#1e1e2e",
                 font=("Segoe UI", 11)).pack(side="left")

        self.model_var = tk.StringVar(value="small")
        self.model_combo = ttk.Combobox(
            ctrl, textvariable=self.model_var,
            values=MODELS, state="readonly", width=12,
            font=("Segoe UI", 11),
        )
        self.model_combo.pack(side="left", padx=(6, 20))

        self.status_var = tk.StringVar(value="Готов")
        self.status_label = tk.Label(
            ctrl, textvariable=self.status_var,
            fg="#a6e3a1", bg="#1e1e2e",
            font=("Segoe UI", 11),
        )
        self.status_label.pack(side="left")

    # ── Text area ─────────────────────────────────────────────────────────────

    def _build_text_area(self):
        text_frame = tk.Frame(self.root, bg="#1e1e2e")
        text_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap="word",
            font=("Segoe UI", 12),
            bg="#181825",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat",
            padx=10,
            pady=10,
            state="disabled",
        )
        self.text_area.pack(fill="both", expand=True)

        self.copy_btn = tk.Button(
            self.root,
            text="Копировать в буфер",
            font=("Segoe UI", 11),
            bg="#89b4fa",
            fg="#1e1e2e",
            activebackground="#74c7ec",
            relief="flat",
            cursor="hand2",
            command=self._copy_to_clipboard,
            pady=6,
        )
        self.copy_btn.pack(fill="x", padx=16, pady=(0, 16))

    # ── Stubs for Tasks 3 and 4 ───────────────────────────────────────────────

    def _on_drop(self, event): pass
    def _on_drag_enter(self, event): pass
    def _on_drag_leave(self, event): pass
    def _copy_to_clipboard(self): pass
    def _poll_queue(self): pass


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = AppWindow(root)
    root.mainloop()
