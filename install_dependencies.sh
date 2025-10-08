#!/bin/bash

# Скрипт для установки зависимостей на сервере
echo "Установка зависимостей для EasyDrive бота..."

# Переходим в директорию проекта
cd /home/easydrive

# Активируем виртуальное окружение
source .venv/bin/activate

# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости
pip install -r requirements.txt

# Проверяем установку
echo "Проверка установленных пакетов:"
pip list | grep -E "(aiogram|dotenv|watchdog)"

echo "Зависимости установлены! Теперь можно запустить бота:"
echo "python bot.py"
