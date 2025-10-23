#!/bin/bash

# Скрипт для деплоя на сервер
echo "Деплой на сервер..."

# Настройка Git
echo "Настройка Git..."
git config pull.rebase true

# Получение изменений
echo "Получение изменений с GitHub..."
git fetch origin

# Переключение на main ветку
echo "Переключение на main ветку..."
git checkout main

# Pull с rebase
echo "Синхронизация с удаленным репозиторием..."
git pull --rebase origin main

# Проверка статуса
echo "Статус репозитория:"
git status

echo "Деплой завершен!"
