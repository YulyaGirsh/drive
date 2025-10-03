#!/bin/bash

# Скрипт для обновления конфигурации на сервере
# Этот файл нужно запустить на сервере после git pull

echo "Обновляем конфигурацию бота..."

# Создаем config.js с реальными данными
cat > config.js << EOF
// Конфигурация бота
const BOT_CONFIG = {
    token: '8263208579:AAHbgB-KSmyqZwMf7FtxBbUzjWNIugUtKu0',
    recipientId: '7644513746'
};
EOF

echo "Конфигурация обновлена!"
echo "Токен бота: 8263208579:AAHbgB-KSmyqZwMf7FtxBbUzjWNIugUtKu0"
echo "ID получателя: 7644513746"
