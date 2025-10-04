@echo off
chcp 65001 >nul
echo 🚀 Запуск автоматического деплоя EasyDrive...
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

REM Запускаем деплой
echo 🚀 Запуск деплоя...
python deploy_windows.py

if errorlevel 1 (
    echo.
    echo ❌ Ошибка деплоя!
    pause
    exit /b 1
)

echo.
echo ✅ Деплой завершен успешно!
echo.
pause
