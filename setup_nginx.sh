#!/bin/bash

# Скрипт для настройки nginx
echo "Настройка nginx для EasyDrive..."

# Создаем конфигурацию nginx
sudo tee /etc/nginx/sites-available/easydrive << 'EOF'
server {
    listen 80;
    server_name hochupravaeasy.ru www.hochupravaeasy.ru;  # Ваш домен
    
    # Статические файлы
    location / {
        root /home/easydrive;
        index index.html;
        try_files $uri $uri/ =404;
    }
    
    # API запросы к Python серверу
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS заголовки
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
        
        # Обработка preflight запросов
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }
}
EOF

# Активируем конфигурацию
echo "Активация конфигурации nginx..."
sudo ln -sf /etc/nginx/sites-available/easydrive /etc/nginx/sites-enabled/

# Удаляем дефолтную конфигурацию если она есть
sudo rm -f /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
echo "Проверка конфигурации nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "Конфигурация nginx корректна. Перезапуск nginx..."
    sudo systemctl reload nginx
    echo "Nginx настроен и перезапущен!"
else
    echo "Ошибка в конфигурации nginx!"
    exit 1
fi

echo "Настройка nginx завершена!"
