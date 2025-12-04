#!/bin/bash
# Команды для деплоя на сервере
# Скопируйте и выполните на сервере

# 1. Решить проблему с git pull (выберите один вариант)
# Вариант А: Сохранить изменения
git stash && git pull origin main

# Вариант Б: Отменить локальные изменения (если не нужны)
# git reset --hard HEAD && git pull origin main

# 2. Найти и остановить старое приложение
# Найти процесс на порту 8000
OLD_PID=$(sudo lsof -t -i:8000)
if [ ! -z "$OLD_PID" ]; then
    echo "Останавливаем процесс $OLD_PID на порту 8000"
    sudo kill $OLD_PID
    sleep 2
fi

# Или найти процесс server.py
ps aux | grep "server.py" | grep -v grep | awk '{print $2}' | xargs -r sudo kill

# 3. Остановить старые Docker контейнеры (если есть)
docker-compose down 2>/dev/null || true

# 4. Собрать и запустить новые контейнеры
docker-compose build --no-cache
docker-compose up -d

# 5. Проверить статус
echo "Проверка статуса контейнеров:"
docker-compose ps

echo ""
echo "Проверка логов (последние 50 строк):"
docker-compose logs --tail=50

echo ""
echo "Проверка работы сервера:"
sleep 5
curl -s http://localhost:8000/api/v2/heartbeat || echo "Сервер еще не запустился, подождите немного"

