#!/bin/bash
# Скрипт автоматической установки Docker и Docker Compose
# Выполните на сервере: sudo bash INSTALL_DOCKER.sh

set -e

echo "========================================="
echo "Установка Docker и Docker Compose"
echo "========================================="

# Проверка, что скрипт запущен от root
if [ "$EUID" -ne 0 ]; then 
    echo "Пожалуйста, запустите скрипт с sudo: sudo bash INSTALL_DOCKER.sh"
    exit 1
fi

# Обновление пакетов
echo "Обновление списка пакетов..."
apt update

# Установка необходимых пакетов
echo "Установка необходимых пакетов..."
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Установка Docker
echo "Установка Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "Docker установлен"
else
    echo "Docker уже установлен"
fi

# Установка Docker Compose
echo "Установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    apt install -y docker-compose
    echo "Docker Compose установлен"
else
    echo "Docker Compose уже установлен"
fi

# Добавление текущего пользователя в группу docker
if [ -n "$SUDO_USER" ]; then
    echo "Добавление пользователя $SUDO_USER в группу docker..."
    usermod -aG docker $SUDO_USER
    echo "Пользователь $SUDO_USER добавлен в группу docker"
    echo "ВАЖНО: Выйдите и войдите снова, чтобы изменения вступили в силу"
fi

# Включение автозапуска Docker
echo "Включение автозапуска Docker..."
systemctl enable docker
systemctl start docker

# Проверка установки
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
echo "Если вы запускали скрипт с sudo, выполните:"
echo "  newgrp docker"
echo "или выйдите и войдите снова"
echo ""
echo "Проверьте работу:"
echo "  docker ps"
echo "  docker-compose --version"

