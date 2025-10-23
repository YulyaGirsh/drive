#!/bin/bash

# Скрипт для запуска Python сервера
echo "Запуск Python сервера..."

# Переходим в директорию проекта
cd /home/easydrive

# Останавливаем предыдущий процесс если он запущен
pkill -f "python.*server.py" || true

# Запускаем сервер в фоновом режиме
nohup python3 server.py > server.log 2>&1 &

# Получаем PID процесса
SERVER_PID=$!

# Сохраняем PID в файл
echo $SERVER_PID > server.pid

echo "Сервер запущен с PID: $SERVER_PID"
echo "Логи сервера: /home/easydrive/server.log"
echo "PID файл: /home/easydrive/server.pid"

# Проверяем что сервер запустился
sleep 2
if ps -p $SERVER_PID > /dev/null; then
    echo "Сервер успешно запущен!"
else
    echo "Ошибка запуска сервера. Проверьте логи:"
    tail -20 server.log
fi