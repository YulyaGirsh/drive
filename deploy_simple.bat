@echo off
chcp 65001 >nul
echo 🚀 Запуск простого деплоя EasyDrive...
echo.

REM Проверяем наличие PowerShell
powershell -Command "Get-Host" >nul 2>&1
if errorlevel 1 (
    echo ❌ PowerShell не найден. Установите PowerShell для продолжения работы.
    pause
    exit /b 1
)

REM Запускаем PowerShell скрипт
echo 🚀 Запуск деплоя через PowerShell...
powershell -ExecutionPolicy Bypass -File "deploy_simple.ps1"

if errorlevel 1 (
    echo.
    echo ❌ Ошибка деплоя!
    pause
    exit /b 1
)

echo.
echo ✅ Деплой завершен!
echo.
pause
