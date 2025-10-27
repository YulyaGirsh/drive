#!/usr/bin/env python3
"""
Проверка статуса проекта EasyDrive
"""
import os
import sys

print("="*60)
print("СТАТУС ПРОЕКТА EASYDRIVE")
print("="*60)

# 1. Проверка файлов
print("\n📁 Проверка файлов:")
files_to_check = [
    'videos.html',
    'server.py', 
    'tbank_payment.py',
    'tbank_config.py',
    'config.env',
    'ARCHITECTURE.md',
    'PAYMENT_README.md'
]

for file in files_to_check:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    print(f"{status} {file}")
    if exists:
        size = os.path.getsize(file)
        print(f"   Размер: {size:,} байт")

# 2. Проверка server.py
print("\n🔧 Проверка server.py:")
with open('server.py', 'r', encoding='utf-8') as f:
    server_content = f.read()
    
checks = {
    'Обработчик init_tbank_payment': 'def init_tbank_payment',
    'Роут /api/tbank-init-payment': '/api/tbank-init-payment',
    'Функция handle_api_post': 'def handle_api_post',
    'Импорт tbank_payment': 'from tbank_payment import'
}

for name, check_str in checks.items():
    found = check_str in server_content
    status = "✅" if found else "❌"
    print(f"{status} {name}")

# 3. Проверка videos.html
print("\n🌐 Проверка videos.html:")
with open('videos.html', 'r', encoding='utf-8') as f:
    videos_content = f.read()
    
checks = {
    'TBANK_TERMINAL_KEY': 'TBANK_TERMINAL_KEY =',
    'BACKEND_API_URL': 'BACKEND_API_URL =',
    'processCardPayment': 'async function processCardPayment',
    'POST запрос к бэкенду': 'fetch(BACKEND_API_URL'
}

for name, check_str in checks.items():
    found = check_str in videos_content
    status = "✅" if found else "❌"
    print(f"{status} {name}")

# 4. Проверка конфигурации
print("\n⚙️ Проверка конфигурации:")
try:
    from tbank_config import TBANK_TERMINAL_KEY, TBANK_SECRET_KEY, TBANK_API_URL
    print(f"✅ TerminalKey: {TBANK_TERMINAL_KEY}")
    print(f"✅ SecretKey длина: {len(TBANK_SECRET_KEY)} символов")
    print(f"✅ API URL: {TBANK_API_URL}")
except Exception as e:
    print(f"❌ Ошибка загрузки конфигурации: {e}")

# 5. Проверка tbank_payment
print("\n💳 Проверка tbank_payment.py:")
with open('tbank_payment.py', 'r', encoding='utf-8') as f:
    tbank_content = f.read()
    
checks = {
    'Класс TbankPayment': 'class TbankPayment',
    'Генерация токена': 'def _create_simple_token',
    'SHA-256 хеширование': 'hashlib.sha256',
    'Сортировка по ключу': 'sorted(token_data.keys())'
}

for name, check_str in checks.items():
    found = check_str in tbank_content
    status = "✅" if found else "❌"
    print(f"{status} {name}")

print("\n" + "="*60)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
print("="*60)

