#!/bin/bash

echo "🔍 Проверка статуса сервера..."

# Проверка процесса
if ps aux | grep -v grep | grep "python.*server.py" > /dev/null; then
    echo "✅ Сервер server.py запущен"
    ps aux | grep -v grep | grep "python.*server.py"
else
    echo "❌ Сервер server.py НЕ запущен"
fi

echo ""
echo "Проверка порта 8000..."
if lsof -Pi :8000 -sTCP:LISTEN > /dev/null; then
    echo "✅ Порт 8000 занят"
    lsof -Pi :8000 -sTCP:LISTEN
else
    echo "❌ Порт 8000 свободен (сервер не запущен)"
fi

echo ""
echo "Проверка логов..."
if [ -f "/home/easydrive/server.log" ]; then
    echo "Последние 20 строк логов:"
    tail -20 /home/easydrive/server.log
else
    echo "Файл логов не найден"
fi
