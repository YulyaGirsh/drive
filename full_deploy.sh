#!/bin/bash

# Полный скрипт деплоя EasyDrive
echo "=== ДЕПЛОЙ EASYDRIVE ==="

# 1. Настройка Git
echo "1. Настройка Git..."
git config pull.rebase true
git config --global pull.rebase true

# 2. Получение изменений
echo "2. Получение изменений с GitHub..."
git fetch origin
git checkout main
git pull --rebase origin main

# 3. Остановка старого сервера
echo "3. Остановка старого сервера..."
pkill -f "python.*server.py" || true

# 4. Настройка nginx
echo "4. Настройка nginx..."
chmod +x setup_nginx.sh
./setup_nginx.sh

# 5. Запуск Python сервера
echo "5. Запуск Python сервера..."
chmod +x start_server.sh
./start_server.sh

# 6. Проверка статуса
echo "6. Проверка статуса..."
sleep 3

echo "=== ПРОВЕРКА СЕРВИСОВ ==="
echo "Nginx статус:"
sudo systemctl status nginx --no-pager -l

echo ""
echo "Python сервер:"
if [ -f server.pid ]; then
    SERVER_PID=$(cat server.pid)
    if ps -p $SERVER_PID > /dev/null; then
        echo "✅ Сервер запущен (PID: $SERVER_PID)"
    else
        echo "❌ Сервер не запущен"
    fi
else
    echo "❌ PID файл не найден"
fi

echo ""
echo "=== ПРОВЕРКА API ==="
curl -s http://localhost:8000/api/check-subscription -X POST -H "Content-Type: application/json" -d '{"user_id":123}' || echo "❌ API недоступен"

echo ""
echo "=== ДЕПЛОЙ ЗАВЕРШЕН ==="
echo "Приложение доступно по адресу: http://your-domain.com"
echo "Логи сервера: tail -f /home/easydrive/server.log"
