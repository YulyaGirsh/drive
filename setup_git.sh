#!/bin/bash

# Скрипт для настройки Git на сервере
echo "Настройка Git для автоматического rebase..."

# Настройка автоматического rebase
git config pull.rebase true

# Настройка глобально для всех репозиториев
git config --global pull.rebase true

# Проверка статуса
echo "Текущая конфигурация Git:"
git config --list | grep pull

echo "Настройка завершена!"
echo "Теперь Git будет автоматически использовать rebase при pull"
