#!/bin/bash

# Скрипт для исправления проблемы с портом
echo "Исправление проблемы с портом 8000..."

# Останавливаем все процессы Python сервера
echo "Остановка всех процессов Python сервера..."
pkill -f "python.*server.py" || true

# Ждем завершения процессов
sleep 3

# Освобождаем порт 8000
echo "Освобождение порта 8000..."
fuser -k 8000/tcp || true

# Проверяем что порт свободен
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Порт 8000 все еще занят"
    echo "Процессы использующие порт 8000:"
    lsof -i :8000
    exit 1
else
    echo "✅ Порт 8000 свободен"
fi

# Запускаем сервер
echo "Запуск сервера..."
cd /home/easydrive
nohup python3 server.py > server.log 2>&1 &

# Получаем PID
SERVER_PID=$!
echo $SERVER_PID > server.pid

echo "Сервер запущен с PID: $SERVER_PID"

# Проверяем что сервер запустился
sleep 2
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Сервер успешно запущен!"
    
    # Проверяем API
    echo "Проверка API..."
    curl -s http://localhost:8000/api/check-subscription -X POST -H "Content-Type: application/json" -d '{"user_id":123}' || echo "❌ API недоступен"
else
    echo "❌ Ошибка запуска сервера. Проверьте логи:"
    tail -20 server.log
fi
