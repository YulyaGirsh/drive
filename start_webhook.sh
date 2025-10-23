#!/bin/bash

# Скрипт для запуска webhook сервера
echo "Запуск webhook сервера для Т-банка..."

# Переходим в директорию проекта
cd /home/easydrive

# Останавливаем предыдущий webhook процесс если он запущен
echo "Остановка предыдущих webhook процессов..."
pkill -f "webhook_server.py" || true
sleep 2

# Проверяем что порт 8001 свободен
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "Порт 8001 занят, освобождаем..."
    fuser -k 8001/tcp || true
    sleep 2
fi

# Запускаем webhook сервер в фоновом режиме
nohup python3 webhook_server.py > webhook.log 2>&1 &

# Получаем PID процесса
WEBHOOK_PID=$!

# Сохраняем PID в файл
echo $WEBHOOK_PID > webhook.pid

echo "Webhook сервер запущен с PID: $WEBHOOK_PID"
echo "Логи webhook сервера: /home/easydrive/webhook.log"
echo "PID файл: /home/easydrive/webhook.pid"

# Проверяем что сервер запустился
sleep 2
if ps -p $WEBHOOK_PID > /dev/null; then
    echo "Webhook сервер успешно запущен!"
    echo "Webhook URL: https://hochupravaeasy.ru/api/tbank-webhook"
else
    echo "Ошибка запуска webhook сервера. Проверьте логи:"
    tail -20 webhook.log
fi
