# VoceLate v1.0

**VoceLate** — десктопное приложение для локальной транскрипции аудио в текст с помощью [Whisper](https://github.com/openai/whisper). Поддерживает любой язык, работает полностью офлайн.

## Возможности

- Drag & drop аудиофайлов прямо в окно приложения
- Транскрипция на любом языке (автоопределение)
- Локальная обработка — данные не покидают компьютер
- Поддержка NVIDIA GPU (CUDA) с автоматическим fallback на CPU
- Выбор размера модели: `tiny` / `base` / `small` / `medium` / `large-v3`
- Копирование результата в буфер обмена одной кнопкой
- Тёмная тема (Catppuccin Mocha)

## Поддерживаемые форматы

`mp3`, `wav`, `m4a`, `flac`, `ogg`, `opus`, `mp4`, `mkv`, `webm`, `avi`, `mov`

## Установка

```bash
pip install faster-whisper tkinterdnd2
```

> Для ускорения на GPU дополнительно установите [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) и cuDNN.

## Запуск

```bash
python app.py
```

## Выбор модели

| Модель | VRAM | Скорость | Качество |
|--------|------|----------|----------|
| tiny | ~1 GB | быстро | базовое |
| base | ~1 GB | быстро | хорошее |
| small | ~2 GB | быстро | хорошее |
| medium | ~5 GB | среднее | отличное |
| large-v3 | ~10 GB | медленно | максимальное |

По умолчанию используется `small` — оптимальный баланс скорости и качества.

## Стек

- Python 3.10+
- [Tkinter](https://docs.python.org/3/library/tkinter.html) (UI)
- [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2) (drag & drop)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (транскрипция)

---

© 5B (Alexey Karpich)
