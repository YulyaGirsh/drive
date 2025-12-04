#!/bin/bash
# Полный скрипт для установки Docker и деплоя приложения на сервер
# Загрузите этот файл на сервер и выполните: sudo bash deploy_to_server.sh

set -e

echo "========================================="
echo "Установка Docker и деплой EasyDrive"
echo "========================================="

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo "Пожалуйста, запустите скрипт с sudo: sudo bash deploy_to_server.sh"
    exit 1
fi

# 1. Установка Docker
echo ""
echo "1. Проверка и установка Docker..."
if ! command -v docker &> /dev/null; then
    echo "Удаление старых версий Docker и containerd..."
    apt remove -y docker docker-engine docker.io containerd containerd.io runc 2>/dev/null || true
    apt autoremove -y
    
    echo "Установка Docker через официальный скрипт..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm -f get-docker.sh
    
    echo "✅ Docker установлен"
else
    echo "✅ Docker уже установлен: $(docker --version)"
fi

# 2. Установка Docker Compose
echo ""
echo "2. Проверка и установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    apt update
    apt install -y docker-compose
    echo "✅ Docker Compose установлен"
else
    echo "✅ Docker Compose уже установлен: $(docker-compose --version)"
fi

# 3. Запуск Docker
echo ""
echo "3. Запуск Docker..."
systemctl start docker
systemctl enable docker

# 4. Остановка старого приложения
echo ""
echo "4. Остановка старого приложения..."
# Остановить процесс на порту 8000
OLD_PID=$(lsof -t -i:8000 2>/dev/null || true)
if [ ! -z "$OLD_PID" ]; then
    echo "Останавливаем процесс $OLD_PID на порту 8000"
    kill $OLD_PID 2>/dev/null || true
    sleep 2
fi

# Остановить процессы server.py
SERVER_PIDS=$(ps aux | grep "server.py" | grep -v grep | awk '{print $2}' || true)
if [ ! -z "$SERVER_PIDS" ]; then
    echo "Останавливаем процессы server.py"
    echo "$SERVER_PIDS" | xargs -r kill 2>/dev/null || true
    sleep 2
fi

# 5. Переход в директорию проекта
echo ""
echo "5. Подготовка директории проекта..."
PROJECT_DIR="/home/easydrive"
cd "$PROJECT_DIR" 2>/dev/null || {
    echo "Директория $PROJECT_DIR не найдена. Создаем..."
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
}

# 6. Обновление кода из репозитория
echo ""
echo "6. Обновление кода из репозитория..."
if [ -d ".git" ]; then
    echo "Обнаружен git репозиторий"
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        echo "Обнаружены незакоммиченные изменения. Сохраняем в stash..."
        git stash
    fi
    git pull origin main
else
    echo "Инициализация git репозитория..."
    git init
    git remote add origin https://github.com/YulyaGirsh/drive.git 2>/dev/null || true
    git pull origin main
fi

# 7. Остановка старых контейнеров
echo ""
echo "7. Остановка старых Docker контейнеров..."
docker-compose down 2>/dev/null || true

# 8. Сборка и запуск контейнеров
echo ""
echo "8. Сборка Docker образов..."
docker-compose build --no-cache

echo ""
echo "9. Запуск контейнеров..."
docker-compose up -d

# 9. Ожидание запуска
echo ""
echo "10. Ожидание запуска сервисов..."
sleep 5

# 10. Проверка статуса
echo ""
echo "========================================="
echo "Проверка статуса:"
echo "========================================="
docker-compose ps

echo ""
echo "Последние логи:"
docker-compose logs --tail=30

echo ""
echo "Проверка работы сервера:"
sleep 3
if curl -s http://localhost:8000/api/v2/heartbeat > /dev/null 2>&1; then
    echo "✅ Сервер работает!"
    curl -s http://localhost:8000/api/v2/heartbeat | head -20
else
    echo "⏳ Сервер еще запускается..."
    echo "Проверьте логи через: docker-compose logs -f"
fi

echo ""
echo "========================================="
echo "Деплой завершен!"
echo "========================================="
echo ""
echo "Полезные команды:"
echo "  docker-compose ps          - статус контейнеров"
echo "  docker-compose logs -f     - просмотр логов"
echo "  docker-compose restart     - перезапуск"
echo "  docker-compose down        - остановка"
