@echo off
REM Скрипт для тестирования проверки подписки на канал
REM Использование: test_subscription.bat <user_id> [channel]

if "%1"=="" (
    echo Использование: test_subscription.bat ^<user_id^> [channel]
    echo.
    echo Примеры:
    echo   test_subscription.bat 123456789
    echo   test_subscription.bat 123456789 avtoshkolavtelefone
    echo   test_subscription.bat 123456789 --api
    exit /b 1
)

python test_subscription.py %*

