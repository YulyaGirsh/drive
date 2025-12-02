@echo off
REM Скрипт для автоматического коммита с русским комментарием
REM Использование: auto_commit.bat [сообщение] [--push]

setlocal

if "%1"=="" (
    python auto_commit.py
) else if "%1"=="--push" (
    python auto_commit.py --push
) else if "%1"=="-p" (
    python auto_commit.py --push %2
) else (
    python auto_commit.py "%*"
)

endlocal

