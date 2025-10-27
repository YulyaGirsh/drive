#!/bin/bash

echo "🔄 Перезапуск сервера..."

cd /home/easydrive

# Останавливаем сервер
echo "Остановка сервера..."
pkill -f "python.*server.py" || true
sleep 2

# Проверяем что порт свободен
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Порт 8000 занят, освобождаем..."
    fuser -k 8000/tcp || true
    sleep 2
fi

# Запускаем сервер
echo "Запуск сервера..."
nohup python3 server.py > server.log 2>&1 &

# Получаем PID
SERVER_PID=$!
echo $SERVER_PID > server.pid

echo "✅ Сервер запущен с PID: $SERVER_PID"
echo "📋 Логи: tail -f /home/easydrive/server.log"

# Проверяем статус через 2 секунды
sleep 2
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Сервер успешно запущен!"
    echo ""
    echo "Проверка обработчика /api/tbank-init-payment..."
    if grep -q "def init_tbank_payment" server.py; then
        echo "✅ Обработчик найден в server.py"
    else
        echo "❌ Обработчик НЕ найден!"
    fi
else
    echo "❌ Ошибка запуска сервера"
    echo "Логи:"
    tail -20 server.log
fi
