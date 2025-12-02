#!/bin/bash
# Скрипт для исправления 404 ошибки

echo "🔧 ИСПРАВЛЕНИЕ 404 ОШИБКИ"
echo "=========================="

cd /home/easydrive

echo ""
echo "1️⃣ Обновляем код из Git..."
git pull origin main

echo ""
echo "2️⃣ Останавливаем старый сервер..."
pkill -f "python.*server.py" || echo "Сервер не был запущен"
sleep 2

echo ""
echo "3️⃣ Запускаем обновленный сервер..."
nohup python3 server.py > server.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > server.pid
echo "✅ Сервер запущен (PID: $SERVER_PID)"

echo ""
echo "4️⃣ Проверяем обработчик..."
sleep 2
if grep -q "def init_tbank_payment" server.py; then
    echo "✅ Обработчик /api/tbank-init-payment найден!"
else
    echo "❌ Обработчик НЕ найден!"
fi

echo ""
echo "5️⃣ Проверяем статус сервера..."
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Сервер работает (PID: $SERVER_PID)"
    echo ""
    echo "📋 Логи (последние 20 строк):"
    tail -20 server.log
else
    echo "❌ Сервер не запустился!"
    echo "Логи:"
    cat server.log
fi

echo ""
echo "✅ ГОТОВО! Попробуйте оплату снова."
