#!/bin/bash
# Команды для деплоя на сервере
# Скопируйте и выполните на сервере

set -e

echo "========================================="
echo "Деплой EasyDrive на сервер"
echo "========================================="

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "ОШИБКА: Docker не установлен!"
    echo "Установите Docker выполнив:"
    echo "  sudo bash INSTALL_DOCKER.sh"
    echo "Или следуйте инструкциям в INSTALL_DOCKER.md"
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ОШИБКА: Docker Compose не установлен!"
    echo "Установите Docker Compose выполнив:"
    echo "  sudo apt install docker-compose"
    echo "Или следуйте инструкциям в INSTALL_DOCKER.md"
    exit 1
fi

# Определить команду docker-compose (старая или новая версия)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "ОШИБКА: Не удалось найти docker-compose"
    exit 1
fi

echo "Используется: $DOCKER_COMPOSE"
echo ""

# 1. Решить проблему с git pull
echo "1. Обновление кода из репозитория..."
if [ -n "$(git status --porcelain)" ]; then
    echo "Обнаружены незакоммиченные изменения"
    read -p "Сохранить изменения во временное хранилище? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git stash
        git pull origin main
        echo "Изменения сохранены в stash. Чтобы вернуть: git stash pop"
    else
        read -p "Отменить локальные изменения? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git reset --hard HEAD
            git pull origin main
        else
            echo "Пропуск обновления кода"
        fi
    fi
else
    git pull origin main
fi

# 2. Найти и остановить старое приложение
echo ""
echo "2. Остановка старого приложения..."
OLD_PID=$(sudo lsof -t -i:8000 2>/dev/null || true)
if [ ! -z "$OLD_PID" ]; then
    echo "Останавливаем процесс $OLD_PID на порту 8000"
    sudo kill $OLD_PID 2>/dev/null || true
    sleep 2
fi

# Или найти процесс server.py
SERVER_PIDS=$(ps aux | grep "server.py" | grep -v grep | awk '{print $2}' || true)
if [ ! -z "$SERVER_PIDS" ]; then
    echo "Останавливаем процессы server.py: $SERVER_PIDS"
    echo "$SERVER_PIDS" | xargs -r sudo kill 2>/dev/null || true
    sleep 2
fi

# 3. Остановить старые Docker контейнеры (если есть)
echo ""
echo "3. Остановка старых Docker контейнеров..."
$DOCKER_COMPOSE down 2>/dev/null || true

# 4. Собрать и запустить новые контейнеры
echo ""
echo "4. Сборка Docker образов..."
$DOCKER_COMPOSE build --no-cache

echo ""
echo "5. Запуск контейнеров..."
$DOCKER_COMPOSE up -d

# 5. Проверить статус
echo ""
echo "========================================="
echo "Проверка статуса:"
echo "========================================="
sleep 3
$DOCKER_COMPOSE ps

echo ""
echo "Проверка логов (последние 50 строк):"
$DOCKER_COMPOSE logs --tail=50

echo ""
echo "Проверка работы сервера:"
sleep 5
if curl -s http://localhost:8000/api/v2/heartbeat > /dev/null; then
    echo "✅ Сервер работает!"
    curl -s http://localhost:8000/api/v2/heartbeat | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/v2/heartbeat
else
    echo "⏳ Сервер еще запускается, подождите немного..."
    echo "Проверьте логи: $DOCKER_COMPOSE logs -f"
fi

echo ""
echo "========================================="
echo "Деплой завершен!"
echo "========================================="

