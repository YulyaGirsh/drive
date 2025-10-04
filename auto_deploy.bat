@echo off
chcp 65001 >nul
echo 👀 Запуск автоматического мониторинга изменений...
echo 📁 Отслеживаемые файлы: .html, .css, .js, .py
echo 🔄 Деплой будет запускаться автоматически при изменениях
echo ⏹️  Для остановки нажмите Ctrl+C
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден. Установите Python для продолжения работы.
    pause
    exit /b 1
)

REM Устанавливаем зависимости если нужно
echo 📦 Проверяем зависимости...
pip install -r requirements.txt >nul 2>&1

REM Запускаем автоматический мониторинг
echo 🚀 Запуск автоматического мониторинга...
python auto_deploy.py

pause
