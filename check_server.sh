#!/bin/bash

# Скрипт для проверки статуса сервера
echo "Проверка статуса сервера EasyDrive..."

# Проверяем, запущен ли сервер
if pgrep -f "python.*server.py" > /dev/null; then
    echo "✅ Сервер запущен"
    echo "PID: $(pgrep -f 'python.*server.py')"
    
    # Проверяем, слушает ли порт 8000
    if netstat -tlnp 2>/dev/null | grep :8000 > /dev/null; then
        echo "✅ Порт 8000 активен"
    else
        echo "❌ Порт 8000 не активен"
    fi
    
    # Показываем последние логи
    echo ""
    echo "Последние логи сервера:"
    echo "========================"
    tail -10 /home/easydrive/server.log 2>/dev/null || echo "Логи не найдены"
    
else
    echo "❌ Сервер не запущен"
    echo ""
    echo "Для запуска выполните:"
    echo "bash start_server.sh"
fi
