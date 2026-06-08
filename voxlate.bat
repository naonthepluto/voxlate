@echo off
cd /d "%~dp0"
python app.py
if errorlevel 1 (
    echo.
    echo Ошибка запуска. Убедитесь что Python установлен и зависимости установлены:
    echo pip install faster-whisper tkinterdnd2
    pause
)
