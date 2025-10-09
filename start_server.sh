#!/bin/bash

# Скрипт для запуска сервера на продакшене
echo "Запуск сервера EasyDrive..."

# Переходим в директорию проекта
cd /home/easydrive

# Проверяем, что мы в правильной директории
if [ ! -f "server.py" ]; then
    echo "Ошибка: server.py не найден в текущей директории"
    exit 1
fi

# Проверяем, не запущен ли уже сервер
if pgrep -f "python.*server.py" > /dev/null; then
    echo "Сервер уже запущен. Останавливаем старый процесс..."
    pkill -f "python.*server.py"
    sleep 2
fi

# Запускаем сервер в фоновом режиме
echo "Запускаем сервер на порту 8000..."
nohup python server.py > server.log 2>&1 &

# Ждем немного и проверяем статус
sleep 3

if pgrep -f "python.*server.py" > /dev/null; then
    echo "✅ Сервер успешно запущен!"
    echo "Логи: tail -f /home/easydrive/server.log"
    echo "Остановка: pkill -f 'python.*server.py'"
else
    echo "❌ Ошибка запуска сервера. Проверьте логи:"
    cat /home/easydrive/server.log
fi
