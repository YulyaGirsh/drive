#!/bin/bash

# Скрипт для установки зависимостей на сервере
echo "Установка зависимостей для EasyDrive бота..."

# Переходим в директорию проекта
cd /home/easydrive

# Активируем виртуальное окружение
source .venv/bin/activate

# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости с принудительной переустановкой
echo "Установка python-dotenv..."
pip install --force-reinstall python-dotenv==1.0.0

echo "Установка watchdog..."
pip install --force-reinstall watchdog==3.0.0

echo "Установка aiohttp (совместимая версия)..."
pip install --force-reinstall "aiohttp>=3.8.0,<4.0.0"

echo "Установка aiogram..."
pip install --force-reinstall aiogram==3.13.1

# Проверяем установку
echo "Проверка установленных пакетов:"
pip list | grep -E "(aiogram|dotenv|watchdog|aiohttp)"

echo "Зависимости установлены! Теперь можно запустить бота:"
echo "python bot.py"
