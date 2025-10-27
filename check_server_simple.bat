@echo off
echo ============================================================
echo ПРОВЕРКА СТАТУСА ПРОЕКТА НА СЕРВЕРЕ
echo ============================================================
echo.
echo Выполните на сервере через SSH:
echo.
echo ssh root@89.23.99.152
echo Пароль: dJN.wJ-YM*+J9b
echo.
echo Затем выполните:
echo.
echo cd /home/easydrive
echo git status
echo ps aux ^| grep server.py ^| grep -v grep
echo grep "def init_tbank_payment" server.py
echo git log --oneline -3
echo.
echo ИЛИ скопируйте весь скрипт check_server_status.bash на сервер
echo.
echo ============================================================
pause

