#!/bin/bash
# Скрипт для исправления проблемы с установкой Docker (конфликт containerd)
# Выполните: sudo bash FIX_DOCKER_INSTALL.sh

set -e

echo "========================================="
echo "Исправление установки Docker"
echo "========================================="

# Проверка, что скрипт запущен от root
if [ "$EUID" -ne 0 ]; then 
    echo "Пожалуйста, запустите скрипт с sudo: sudo bash FIX_DOCKER_INSTALL.sh"
    exit 1
fi

echo "1. Удаление старых версий Docker и containerd..."
apt remove -y docker docker-engine docker.io containerd containerd.io runc 2>/dev/null || true

echo "2. Очистка системы..."
apt autoremove -y
apt autoclean

echo "3. Установка Docker через официальный скрипт..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm -f get-docker.sh
    echo "✅ Docker установлен"
else
    echo "✅ Docker уже установлен"
fi

echo "4. Установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    apt update
    apt install -y docker-compose
    echo "✅ Docker Compose установлен"
else
    echo "✅ Docker Compose уже установлен"
fi

echo "5. Запуск Docker..."
systemctl start docker
systemctl enable docker

echo "6. Добавление пользователя в группу docker..."
if [ -n "$SUDO_USER" ]; then
    usermod -aG docker $SUDO_USER
    echo "✅ Пользователь $SUDO_USER добавлен в группу docker"
    echo ""
    echo "ВАЖНО: Выполните команду: newgrp docker"
    echo "Или выйдите и войдите снова"
fi

echo ""
echo "========================================="
echo "Проверка установки:"
echo "========================================="
docker --version
docker-compose --version
systemctl status docker --no-pager | head -5

echo ""
echo "========================================="
echo "Установка завершена!"
echo "========================================="
echo ""
echo "Выполните: newgrp docker"
echo "Затем проверьте: docker ps"

