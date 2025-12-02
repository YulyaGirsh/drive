#!/bin/bash
# Скрипт для проверки статуса на сервере
# Запустите на сервере: bash check_server_status.bash

echo "============================================================"
echo "ПРОВЕРКА СТАТУСА ПРОЕКТА НА СЕРВЕРЕ"
echo "============================================================"

cd /home/easydrive

echo ""
echo "📁 GIT STATUS:"
echo "----------------------------------------"
git status

echo ""
echo "🖥️  ПРОЦЕСС SERVER.PY:"
echo "----------------------------------------"
ps aux | grep "python.*server.py" | grep -v grep || echo "❌ Сервер НЕ запущен!"

echo ""
echo "🔍 ПРОВЕРКА ОБРАБОТЧИКА /api/tbank-init-payment:"
echo "----------------------------------------"
if grep -q "def init_tbank_payment" server.py; then
    echo "✅ Обработчик НАЙДЕН в server.py"
    grep -n "def init_tbank_payment" server.py
else
    echo "❌ Обработчик НЕ НАЙДЕН!"
fi

echo ""
echo "📋 РОУТЫ В server.py:"
echo "----------------------------------------"
grep -n "elif self.path == '/api/tbank-init-payment':" server.py || echo "❌ Роут не найден"

echo ""
echo "📝 ПОСЛЕДНИЕ КОММИТЫ:"
echo "----------------------------------------"
git log --oneline -3

echo ""
echo "📋 ЛОГИ СЕРВЕРА (последние 30 строк):"
echo "----------------------------------------"
if [ -f "server.log" ]; then
    tail -30 server.log
else
    echo "❌ Файл логов не найден"
fi

echo ""
echo "============================================================"
echo "✅ ПРОВЕРКА ЗАВЕРШЕНА"
echo "============================================================"

