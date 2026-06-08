import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
from faster_whisper import WhisperModel
from version import FULL_LABEL

MODELS = ["tiny", "base", "small", "medium", "large-v3"]
SUPPORTED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus",
    ".mp4", ".mkv", ".webm", ".avi", ".mov"
}

def is_supported(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in SUPPORTED_EXTENSIONS


def _transcribe_worker(
    path: str,
    model_name: str,
    model_cache: dict,
    result_queue: queue.Queue,
) -> None:
    try:
        result_queue.put(("progress", f"Загрузка модели {model_name}..."))

        if model_name not in model_cache:
            model_cache.clear()
            try:
                model = WhisperModel(model_name, device="cuda", compute_type="float16")
            except Exception as cuda_exc:
                print(f"[voxlate] CUDA unavailable ({cuda_exc}), falling back to CPU", file=sys.stderr)
                model = WhisperModel(model_name, device="cpu", compute_type="int8")
            model_cache[model_name] = model
        else:
            model = model_cache[model_name]

        result_queue.put(("progress", "Транскрипция..."))

        segments, info = model.transcribe(path, beam_size=5)
        text = " ".join(segment.text.strip() for segment in segments)

        result_queue.put(("result", text if text else "(пустой результат)"))

    except Exception as exc:
        result_queue.put(("error", str(exc)))


def _parse_drop_paths(data: str) -> list[str]:
    """Parse tkinterdnd2 drop data into a list of file paths."""
    paths = []
    data = data.strip()
    i = 0
    while i < len(data):
        if data[i] == "{":
            end = data.find("}", i)
            if end == -1:
                paths.append(data[i + 1:])
                break
            paths.append(data[i + 1:end])
            i = end + 1
        else:
            end = data.find(" ", i)
            if end == -1:
                paths.append(data[i:])
                break
            paths.append(data[i:end])
            i = end + 1
        data_rest = data[i:].strip()
        i = len(data) - len(data_rest)
    return [p for p in paths if p]


class AppWindow:
    def __init__(self, root: TkinterDnD.Tk):
        self.root = root
        self.root.title("Voxlate — Транскрипция аудио")
        self.root.geometry("700x520")
        self.root.minsize(500, 400)
        self.root.resizable(True, True)
        self.root.configure(bg="#1e1e2e")

        self._queue: queue.Queue = queue.Queue()
        self._model_cache: dict = {}  # {"model_name": WhisperModel instance}
        self._worker: threading.Thread | None = None
        self._running: bool = True
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_drop_zone()
        self._build_controls()
        self._build_text_area()
        self._build_footer()
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

        for widget in (self.drop_frame, self.drop_label):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop)
            widget.dnd_bind("<<DragEnter>>", self._on_drag_enter)
            widget.dnd_bind("<<DragLeave>>", self._on_drag_leave)

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
        self.text_frame = tk.Frame(self.root, bg="#1e1e2e")
        self.text_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        # Pack button first so it anchors to bottom before text_area claims expand space
        self.copy_btn = tk.Button(
            self.text_frame,
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
        self.copy_btn.pack(fill="x", side="bottom", pady=(8, 0))

        self.text_area = scrolledtext.ScrolledText(
            self.text_frame,
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

    # ── Footer ────────────────────────────────────────────────────────────────

    def _build_footer(self):
        tk.Label(
            self.root,
            text=FULL_LABEL,
            font=("Segoe UI", 8),
            fg="#585b70",
            bg="#1e1e2e",
        ).pack(side="bottom", pady=(0, 4))

    def _on_close(self):
        self._running = False
        self.root.destroy()

    # ── Drag & drop handlers ──────────────────────────────────────────────────

    def _on_drag_enter(self, event):
        self.drop_frame.configure(bg="#45475a")
        self.drop_label.configure(bg="#45475a")

    def _on_drag_leave(self, event):
        self.drop_frame.configure(bg="#313244")
        self.drop_label.configure(bg="#313244")

    def _on_drop(self, event):
        self.drop_frame.configure(bg="#313244")
        self.drop_label.configure(bg="#313244")

        raw = event.data.strip()
        paths = self._parse_drop_paths(raw)

        if len(paths) > 1:
            self._set_status("Можно перетащить только один файл", color="#f38ba8")
            self.root.after(3000, lambda: self._set_status("Готов"))
            return

        path = paths[0] if paths else raw

        if not is_supported(path):
            self._set_status("Неподдерживаемый формат файла", color="#f38ba8")
            self.root.after(3000, lambda: self._set_status("Готов"))
            return

        self._start_transcription(path)

    def _parse_drop_paths(self, data: str) -> list[str]:
        return _parse_drop_paths(data)

    # ── Copy ──────────────────────────────────────────────────────────────────

    def _copy_to_clipboard(self):
        text = self.text_area.get("1.0", "end-1c")
        if text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self._set_status("Скопировано!", color="#a6e3a1")
            self.root.after(2000, lambda: self._set_status("Готов"))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_status(self, message: str, color: str = "#a6e3a1"):
        self.status_var.set(message)
        self.status_label.configure(fg=color)

    def _set_text(self, text: str):
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", text)
        self.text_area.configure(state="disabled")

    def _start_transcription(self, path: str):
        if self._worker and self._worker.is_alive():
            self._set_status("Уже выполняется транскрипция...", color="#fab387")
            return

        model_name = self.model_var.get()
        self.drop_label.configure(text="Транскрибируется...")
        self._set_status("Запуск...", color="#89dceb")

        self._worker = threading.Thread(
            target=_transcribe_worker,
            args=(path, model_name, self._model_cache, self._queue),
            daemon=True,
        )
        self._worker.start()

    # ── Poll queue (Task 4) ───────────────────────────────────────────────────

    def _poll_queue(self):
        try:
            while True:
                msg_type, payload = self._queue.get_nowait()
                if msg_type == "result":
                    self._set_text(payload)
                    self._set_status("Готово")
                    self.drop_frame.configure(bg="#313244")
                    self.drop_label.configure(text="Перетащи аудиофайл сюда")
                elif msg_type == "error":
                    self._set_text(f"Ошибка: {payload}")
                    self._set_status("Ошибка", color="#f38ba8")
                    self.drop_label.configure(text="Перетащи аудиофайл сюда")
                elif msg_type == "progress":
                    self._set_status(payload, color="#89dceb")
        except queue.Empty:
            pass
        if self._running:
            self.root.after(100, self._poll_queue)


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = AppWindow(root)
    root.mainloop()
